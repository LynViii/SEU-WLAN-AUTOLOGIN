#!/usr/bin/env python3
from __future__ import annotations

import argparse
import os
import subprocess
import time
from datetime import datetime
from pathlib import Path

from seu_wlan import client, credentials, startup


def emit(message: str, *, quiet: bool = False, to_log: bool = False) -> None:
    line = f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {message}"
    if not quiet:
        print(message, flush=True)
    if to_log:
        credentials.LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
        with credentials.LOG_FILE.open("a", encoding="utf-8") as handle:
            handle.write(line + "\n")


def describe(status: client.Status) -> str:
    suffix = f"（IP: {status.ip}）" if status.ip else ""
    return ("✓ 已认证" if status.authenticated else "○ 未认证") + suffix


def ensure_authenticated(*, interactive: bool, quiet: bool = False, to_log: bool = False) -> bool:
    username, password = credentials.get(interactive=interactive)

    session = client.make_session()
    current = client.status(session)
    if current.authenticated:
        emit(describe(current), quiet=quiet, to_log=to_log)
        return True

    emit("正在认证……", quiet=quiet, to_log=to_log)
    result = client.login(username, password, session=session)
    emit(describe(result), quiet=quiet, to_log=to_log)
    return True


def reconnect_windows(profile: str, *, quiet: bool, to_log: bool) -> bool:
    if os.name != "nt":
        return False

    emit(f"尝试重新连接 Wi-Fi：{profile}", quiet=quiet, to_log=to_log)
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
    emit("SEU WLAN 后台守护已启动。", quiet=quiet, to_log=True)

    while True:
        try:
            ensure_authenticated(interactive=False, quiet=quiet, to_log=True)
            failures = 0
        except client.AuthenticationRejected as exc:
            emit(f"✗ 认证失败：{exc}", quiet=quiet, to_log=True)
            failures = 0
        except (client.GatewayUnavailable, ValueError) as exc:
            failures += 1
            emit(f"! {exc}", quiet=quiet, to_log=True)
            if failures >= recover_after and os.name == "nt":
                reconnect_windows(profile, quiet=quiet, to_log=True)
                failures = 0
                time.sleep(8)
        time.sleep(interval)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="东南大学 seu-wlan 自动认证")
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--status", action="store_true", help="仅查看当前认证状态")
    group.add_argument("--setup", action="store_true", help="重新设置账号密码")
    group.add_argument("--forget", action="store_true", help="删除保存的账号密码")
    group.add_argument("--watch", action="store_true", help="持续监控，掉线后自动重新认证")
    group.add_argument("--install-startup", action="store_true", help="Windows：登录系统后自动启动后台守护")
    group.add_argument("--uninstall-startup", action="store_true", help="Windows：移除自动启动")
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

        if args.install_startup:
            username, password = credentials.get(interactive=True)
            if not credentials.has_persisted_password(username):
                if not credentials.store(username, password):
                    raise RuntimeError(
                        "无法把密码写入系统凭据管理器，未安装自动启动。"
                        "请先安装 requirements/desktop.txt 并确认系统 keyring 可用。"
                    )
            path = startup.install(Path(__file__))
            print(f"✓ 已安装 Windows 自动启动：{path}")
            print("下次登录 Windows 后会后台运行 --watch，并直接使用已保存凭据自动认证。")
            return 0

        if args.uninstall_startup:
            print("✓ 已移除 Windows 自动启动。" if startup.uninstall() else "○ 尚未安装 Windows 自动启动。")
            return 0

        if args.watch:
            if args.interval < 15:
                raise ValueError("--interval 不能小于 15 秒。")
            if args.recover_after < 1:
                raise ValueError("--recover-after 必须至少为 1。")
            return watch(args.interval, args.recover_after, args.profile, args.quiet)

        return 0 if ensure_authenticated(interactive=True, quiet=args.quiet) else 1

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
