#!/usr/bin/env python3
"""Keep SEU WLAN authenticated, with optional Windows Wi-Fi recovery."""

from __future__ import annotations

import argparse
import os
import subprocess
import time
from datetime import datetime

import login


def log(message: str) -> None:
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {message}", flush=True)


def reconnect_windows(profile: str) -> bool:
    if os.name != "nt":
        return False
    log(f"尝试重新连接 Wi-Fi 配置：{profile}")
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


def ensure_authenticated() -> bool:
    session = login.build_session()
    status = login.get_status(session)
    if status.authenticated:
        return True

    username, password = login.get_credentials()
    result = login.authenticate(username, password, session=session, status=status)
    return result.authenticated


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="保持 seu-wlan 在线并在掉线后自动重新认证")
    parser.add_argument("--interval", type=int, default=60, help="检查间隔（秒），默认 60")
    parser.add_argument(
        "--profile",
        default="seu-wlan",
        help="Windows 无线网络配置名称，默认 seu-wlan",
    )
    parser.add_argument(
        "--recover-after",
        type=int,
        default=2,
        help="连续多少次无法访问认证网关后尝试重连 Wi-Fi，默认 2",
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()
    if args.interval < 15:
        print("检查间隔不能小于 15 秒。")
        return 2
    if args.recover_after < 1:
        print("--recover-after 必须至少为 1。")
        return 2

    log("SEU WLAN 自动保持已启动。按 Ctrl+C 退出。")
    failures = 0

    try:
        while True:
            try:
                if ensure_authenticated():
                    if failures:
                        log("✓ 网络已恢复并通过认证")
                    failures = 0
            except login.AuthenticationError as exc:
                log(f"✗ 认证失败：{exc}")
                failures = 0
            except login.GatewayError as exc:
                failures += 1
                log(f"! 无法访问校园网认证网关（{failures}/{args.recover_after}）：{exc}")
                if failures >= args.recover_after and os.name == "nt":
                    if reconnect_windows(args.profile):
                        log("已发起 Wi-Fi 重连，等待网络恢复……")
                        time.sleep(8)
                    else:
                        log("Wi-Fi 重连命令失败；请确认 Windows 中已保存该无线网络配置。")
                    failures = 0
            time.sleep(args.interval)
    except KeyboardInterrupt:
        log("已退出。")
        return 0


if __name__ == "__main__":
    raise SystemExit(main())
