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


def current_windows_ssid() -> str | None:
    if os.name != "nt":
        return None

    result = subprocess.run(
        ["netsh", "wlan", "show", "interfaces"],
        capture_output=True,
        text=True,
        errors="replace",
        check=False,
    )
    if result.returncode != 0:
        return None

    for line in result.stdout.splitlines():
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        if key.strip().upper() == "SSID":
            ssid = value.strip()
            return ssid or None
    return None


def reconnect_windows(profile: str, *, quiet: bool, to_log: bool) -> bool:
    if os.name != "nt":
        return False

    current = current_windows_ssid()
    if current and current.casefold() != profile.casefold():
        emit(
            f"当前 Wi-Fi 为 {current}，不会为 {profile} 断开现有连接。",
            quiet=quiet,
            to_log=to_log,
        )
        return False

    emit(f"尝试重新连接 Wi-Fi：{profile}", quiet=quiet, to_log=to_log)

    if current:
        subprocess.run(
            ["netsh", "wlan", "disconnect"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=False,
        )
        time.sleep(3)

    result = subprocess.run(
        ["netsh", "wlan", "connect", f"name={profile}"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        check=False,
    )
    return result.returncode == 0


def watch(interval: int, recover_after: int, profile: str, quiet: bool) -> int:
    failures = 0
    last_state: str | None = None
    emit("SEU WLAN 后台守护已启动。", quiet=quiet, to_log=True)

    while True:
        if os.name == "nt":
            ssid = current_windows_ssid()
            if ssid and ssid.casefold() != profile.casefold():
                state = f"other-wifi:{ssid}"
                if state != last_state:
                    emit(
                        f"当前 Wi-Fi：{ssid}；等待连接 {profile}。",
                        quiet=quiet,
                        to_log=True,
                    )
                last_state = state
                failures = 0
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
            failures = 0

        except client.AuthenticationRejected as exc:
            state = f"auth-rejected:{exc}"
            if state != last_state:
                emit(f"✗ 认证失败：{exc}", quiet=quiet, to_log=True)
            last_state = state
            failures = 0

        except (client.GatewayUnavailable, ValueError) as exc:
            failures += 1
            state = f"gateway-error:{exc}"
            if state != last_state:
                emit(f"! {exc}", quiet=quiet, to_log=True)
            last_state = state

            if failures >= recover_after and os.name == "nt":
                reconnect_windows(profile, quiet=quiet, to_log=True)
                failures = 0
                time.sleep(8)

        time.sleep(interval)


def diagnose() -> int:
    print(f"SEU-WLAN-AUTOLOGIN {__version__}")
    print(f"运行模式: {'单文件 EXE' if startup.is_frozen() else 'Python 源码'}")
    print(f"运行文件: {Path(sys.executable if startup.is_frozen() else __file__).resolve()}")
    print(f"配置目录: {credentials.config_dir()}")
    print(f"日志文件: {credentials.LOG_FILE}")

    if os.name == "nt":
        print(f"当前 Wi-Fi: {current_windows_ssid() or '未检测到'}")
        try:
            installed = startup.startup_installed()
        except RuntimeError:
            installed = False
        print(f"开机守护: {'已安装' if installed else '未安装'}")
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
    group.add_argument("--watch", action="store_true", help="持续监控，掉线后自动重新认证")
    group.add_argument("--diagnose", action="store_true", help="输出脱敏后的运行环境诊断信息")
    group.add_argument("--install-startup", action="store_true", help="安装后台自动守护（Windows / macOS / Linux）")
    group.add_argument("--uninstall-startup", action="store_true", help="移除后台自动守护")
    parser.add_argument("--interval", type=int, default=60, help="守护模式检查间隔，默认 60 秒")
    parser.add_argument("--recover-after", type=int, default=2, help="连续网关失败多少次后重连 Wi-Fi，默认 2")
    parser.add_argument("--profile", default="seu-wlan", help="Windows Wi-Fi 配置名称")
    parser.add_argument("--quiet", action="store_true", help="不输出控制台信息，守护日志仍写入本机配置目录")
    return parser


def main(argv: list[str] | None = None) -> int:
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
            if args.recover_after < 1:
                raise ValueError("--recover-after 必须至少为 1。")
            return watch(args.interval, args.recover_after, args.profile, args.quiet)

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
