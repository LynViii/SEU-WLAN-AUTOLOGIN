#!/usr/bin/env python3
from __future__ import annotations

import argparse
import codecs
import os
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

from seu_wlan import __version__, client, credentials, startup

MAX_LOG_BYTES = 512 * 1024


def is_windows() -> bool:
    return os.name == "nt"


def _configure_stdio() -> None:
    """Avoid crashes when a terminal code page cannot represent Chinese text."""
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(errors="replace")
        except (AttributeError, OSError):
            pass


def _prepare_log_file() -> None:
    path = credentials.LOG_FILE
    path.parent.mkdir(parents=True, exist_ok=True)

    if path.exists() and path.stat().st_size >= MAX_LOG_BYTES:
        backup = path.with_suffix(path.suffix + ".1")
        try:
            backup.unlink()
        except FileNotFoundError:
            pass
        path.replace(backup)

    if not path.exists():
        path.write_bytes(codecs.BOM_UTF8)
        return

    with path.open("rb") as handle:
        has_bom = handle.read(3) == codecs.BOM_UTF8
    if not has_bom:
        data = path.read_bytes()
        path.write_bytes(codecs.BOM_UTF8 + data)


def _append_log(line: str) -> None:
    _prepare_log_file()
    with credentials.LOG_FILE.open("ab") as handle:
        handle.write((line + "\n").encode("utf-8"))


def emit(message: str, *, quiet: bool = False, to_log: bool = False) -> None:
    line = f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {message}"
    if not quiet:
        print(message, flush=True)
    if to_log:
        _append_log(line)


def describe(status: client.Status) -> str:
    suffix = f"（IP: {status.ip}）" if status.ip else ""
    return ("✓ 已认证" if status.authenticated else "○ 未认证") + suffix


def ensure_authenticated(
    *,
    interactive: bool,
    quiet: bool = False,
    to_log: bool = False,
) -> client.Status:
    username, password = credentials.get(interactive=interactive)

    session = client.make_session()
    current = client.status(session)
    if current.authenticated:
        emit(describe(current), quiet=quiet, to_log=to_log)
        return current

    emit("正在认证……", quiet=quiet, to_log=to_log)
    result = client.login(
        username,
        password,
        session=session,
        known_status=current,
    )
    emit(describe(result), quiet=quiet, to_log=to_log)
    return result


def _decode_windows_text(raw: bytes) -> str:
    for encoding in (
        "utf-8",
        getattr(sys.stdout, "encoding", None),
        "mbcs",
        "gbk",
    ):
        if not encoding:
            continue
        try:
            return raw.decode(encoding)
        except (LookupError, UnicodeDecodeError):
            continue
    return raw.decode(errors="replace")


def current_windows_ssid() -> str | None:
    if not is_windows():
        return None

    try:
        result = subprocess.run(
            ["netsh", "wlan", "show", "interfaces"],
            capture_output=True,
            check=False,
        )
    except OSError:
        return None

    if result.returncode != 0:
        return None

    # "SSID" itself is ASCII even on localized Windows, so identify the field
    # in bytes first and only decode the value. This avoids code-page issues.
    for raw_line in (result.stdout or b"").splitlines():
        if b":" not in raw_line:
            continue
        key, value = raw_line.split(b":", 1)
        if key.strip().upper() == b"SSID":
            value = value.strip()
            if not value:
                return None
            return _decode_windows_text(value).strip() or None

    return None


class WatchLock:
    def __init__(self) -> None:
        self.path = credentials.config_dir() / "watch.lock"
        self.handle = None

    def acquire(self) -> bool:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.handle = self.path.open("a+b")
        self.handle.seek(0, os.SEEK_END)
        if self.handle.tell() == 0:
            self.handle.write(b"0")
            self.handle.flush()
        self.handle.seek(0)

        try:
            if os.name == "nt":
                import msvcrt

                msvcrt.locking(self.handle.fileno(), msvcrt.LK_NBLCK, 1)
            else:
                import fcntl

                fcntl.flock(self.handle.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
            return True
        except (OSError, ImportError):
            self.handle.close()
            self.handle = None
            return False

    def release(self) -> None:
        if self.handle is None:
            return
        try:
            if os.name == "nt":
                import msvcrt

                self.handle.seek(0)
                msvcrt.locking(self.handle.fileno(), msvcrt.LK_UNLCK, 1)
            else:
                import fcntl

                fcntl.flock(self.handle.fileno(), fcntl.LOCK_UN)
        except (OSError, ImportError):
            pass
        self.handle.close()
        self.handle = None


def watch(interval: int, profile: str, quiet: bool) -> int:
    lock = WatchLock()
    if not lock.acquire():
        emit("已有一个 SEU WLAN 后台守护实例在运行，当前实例退出。", quiet=quiet)
        return 0

    last_state: str | None = None
    emit("SEU WLAN 后台守护已启动。", quiet=quiet, to_log=True)

    try:
        while True:
            if is_windows():
                ssid = current_windows_ssid()

                # Safety invariant: this tool never changes Windows Wi-Fi
                # connections. It only authenticates after positively
                # identifying the target SSID.
                if not ssid:
                    state = "wifi-unknown"
                    if state != last_state:
                        emit(
                            f"未检测到当前 Wi-Fi；等待连接 {profile}，不会修改网络连接。",
                            quiet=quiet,
                            to_log=True,
                        )
                    last_state = state
                    time.sleep(interval)
                    continue

                if ssid.casefold() != profile.casefold():
                    state = f"other-wifi:{ssid}"
                    if state != last_state:
                        emit(
                            f"当前 Wi-Fi：{ssid}；等待连接 {profile}，不会修改当前网络。",
                            quiet=quiet,
                            to_log=True,
                        )
                    last_state = state
                    time.sleep(interval)
                    continue

            try:
                result = ensure_authenticated(
                    interactive=False,
                    quiet=True,
                    to_log=False,
                )
                if last_state != "authenticated":
                    emit(describe(result), quiet=quiet, to_log=True)
                last_state = "authenticated"

            except client.AuthenticationRejected as exc:
                state = f"auth-rejected:{exc}"
                if state != last_state:
                    emit(f"✗ 认证失败：{exc}", quiet=quiet, to_log=True)
                last_state = state

            except (client.GatewayUnavailable, ValueError) as exc:
                state = f"gateway-error:{exc}"
                if state != last_state:
                    emit(f"! {exc}", quiet=quiet, to_log=True)
                last_state = state

            time.sleep(interval)
    finally:
        lock.release()


def diagnose() -> int:
    print(f"SEU-WLAN-AUTOLOGIN {__version__}")
    print(f"运行模式: {'单文件 EXE' if startup.is_frozen() else 'Python 源码'}")
    print(f"运行文件: {Path(sys.executable if startup.is_frozen() else __file__).resolve()}")
    print(f"配置目录: {credentials.config_dir()}")
    print(f"日志文件: {credentials.LOG_FILE}")

    try:
        installed = startup.startup_installed()
    except RuntimeError:
        installed = False
    print(f"后台守护: {'已安装' if installed else '未安装'}")

    if is_windows():
        print(f"当前 Wi-Fi: {current_windows_ssid() or '未检测到'}")
        print("Wi-Fi 控制: 禁用（守护只负责认证，不会切换或断开网络）")
        if startup.is_frozen():
            print(f"固定安装位置: {startup.installed_executable()}")

    try:
        print(f"认证状态: {describe(client.status())}")
    except client.GatewayUnavailable as exc:
        print(f"认证网关: 不可访问（{exc}）")

    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="东南大学 seu-wlan 自动认证")
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--status", action="store_true", help="仅查看当前认证状态")
    group.add_argument("--setup", action="store_true", help="重新设置账号密码")
    group.add_argument("--forget", action="store_true", help="删除保存的账号密码")
    group.add_argument("--watch", action="store_true", help="持续监控，连接 seu-wlan 后自动补认证")
    group.add_argument("--diagnose", action="store_true", help="输出脱敏后的运行环境诊断信息")
    group.add_argument("--install-startup", action="store_true", help="安装后台自动守护（Windows / macOS / Linux）")
    group.add_argument("--uninstall-startup", action="store_true", help="移除后台自动守护")
    parser.add_argument("--interval", type=int, default=60, help="守护模式检查间隔，默认 60 秒")
    parser.add_argument("--profile", default="seu-wlan", help="Windows 目标 Wi-Fi 名称")
    parser.add_argument("--quiet", action="store_true", help="不输出控制台信息，守护日志仍写入本机配置目录")
    return parser


def main(argv: list[str] | None = None) -> int:
    _configure_stdio()
    args = build_parser().parse_args(argv)

    try:
        if args.setup:
            _, _, stored = credentials.setup()
            if stored:
                print("✓ 账号已保存，密码已写入系统凭据管理器。")
            else:
                print("! 当前系统没有可用的安全凭据后端；本次可用，但下次可能需要重新输入密码。")
            return 0

        if args.forget:
            credentials.forget()
            print("✓ 已删除本机保存的账号信息。")
            return 0

        if args.status:
            print(describe(client.status()))
            return 0

        if args.diagnose:
            return diagnose()

        if args.install_startup:
            username, password = credentials.get(interactive=True)
            if not credentials.has_persisted_password(username):
                if not credentials.store(username, password):
                    raise RuntimeError(
                        "无法把密码写入系统凭据管理器，未安装自动启动。"
                        "请确认系统 keyring 可用。"
                    )
            path = startup.install(Path(__file__))
            print(f"✓ 已安装后台自动守护：{path}")
            if startup.is_frozen():
                print(f"✓ 后台运行副本：{startup.installed_executable()}")
                print("现在可以移动或删除当前下载的 EXE；开机守护不会受影响。")
            else:
                print("源码模式的后台守护依赖当前 Python 和脚本路径；移动源码目录后请重新安装守护。")
            return 0

        if args.uninstall_startup:
            print("✓ 已移除后台自动守护。" if startup.uninstall() else "○ 尚未安装后台自动守护。")
            return 0

        if args.watch:
            if args.interval < 15:
                raise ValueError("--interval 不能小于 15 秒。")
            return watch(args.interval, args.profile, args.quiet)

        ensure_authenticated(interactive=True, quiet=args.quiet)
        return 0

    except KeyboardInterrupt:
        if not args.quiet:
            print("\n已退出。")
        return 130
    except (client.SeuWlanError, ValueError, RuntimeError) as exc:
        if not args.quiet:
            print(f"✗ {exc}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
