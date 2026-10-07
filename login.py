#!/usr/bin/env python3
"""SEU WLAN login client.

The script talks directly to Southeast University's Dr.COM/ePortal gateway.
Credentials are entered interactively and the password is stored in the OS
credential store through `keyring` when available.
"""

from __future__ import annotations

import argparse
import base64
import getpass
import json
import os
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Optional

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

try:
    import keyring
    from keyring.errors import KeyringError
except ImportError:  # pragma: no cover - handled at runtime
    keyring = None

    class KeyringError(Exception):
        pass


APP_NAME = "SEU-WLAN-AUTOLOGIN"
KEYRING_SERVICE = "SEU-WLAN-AUTOLOGIN"
STATUS_URL = "https://w.seu.edu.cn/drcom/chkstatus"
PORTAL_URL = "https://w.seu.edu.cn:801/eportal/"
DEFAULT_TIMEOUT = (3.05, 8.0)


class SeuWlanError(RuntimeError):
    """Base error for expected SEU WLAN failures."""


class GatewayError(SeuWlanError):
    """Raised when the campus authentication gateway cannot be used."""


class AuthenticationError(SeuWlanError):
    """Raised when authentication is rejected."""


@dataclass(frozen=True)
class NetworkStatus:
    authenticated: bool
    ip: str = ""
    raw: Optional[dict[str, Any]] = None


def _config_dir() -> Path:
    if os.name == "nt":
        base = Path(os.environ.get("APPDATA", Path.home()))
        return base / APP_NAME
    if sys.platform == "darwin":
        return Path.home() / "Library" / "Application Support" / APP_NAME
    return Path(os.environ.get("XDG_CONFIG_HOME", Path.home() / ".config")) / APP_NAME


CONFIG_FILE = _config_dir() / "config.json"


def build_session() -> requests.Session:
    retry = Retry(
        total=2,
        connect=2,
        read=2,
        status=2,
        backoff_factor=0.35,
        status_forcelist=(502, 503, 504),
        allowed_methods=frozenset({"GET"}),
        raise_on_status=False,
    )
    adapter = HTTPAdapter(max_retries=retry)
    session = requests.Session()
    session.mount("https://", adapter)
    session.headers.update({"User-Agent": f"{APP_NAME}/1.0"})
    return session


def parse_jsonp(text: str) -> dict[str, Any]:
    """Extract the JSON object from a Dr.COM JSONP response."""
    match = re.search(r"\{.*\}", text, flags=re.DOTALL)
    if not match:
        raise GatewayError("校园网网关返回了无法识别的数据。")
    try:
        value = json.loads(match.group(0))
    except json.JSONDecodeError as exc:
        raise GatewayError("校园网网关返回的 JSON 数据无效。") from exc
    if not isinstance(value, dict):
        raise GatewayError("校园网网关返回的数据格式异常。")
    return value


def _request_jsonp(
    session: requests.Session,
    url: str,
    *,
    params: dict[str, str],
) -> dict[str, Any]:
    try:
        response = session.get(url, params=params, timeout=DEFAULT_TIMEOUT)
        response.raise_for_status()
    except requests.RequestException as exc:
        raise GatewayError("无法连接东南大学校园网认证网关。请先确认已连接 seu-wlan。") from exc
    return parse_jsonp(response.text)


def get_status(session: Optional[requests.Session] = None) -> NetworkStatus:
    session = session or build_session()
    data = _request_jsonp(session, STATUS_URL, params={"callback": "dr1002"})

    result = str(data.get("result", ""))
    ip = str(data.get("v46ip") or data.get("v4ip") or data.get("ss5") or "")

    if result == "1":
        return NetworkStatus(authenticated=True, ip=ip, raw=data)
    if result == "0":
        return NetworkStatus(authenticated=False, ip=ip, raw=data)
    raise GatewayError(f"校园网返回了未知状态 result={result!r}。")


def _decode_message(value: Any) -> str:
    if value is None:
        return ""
    text = str(value)
    try:
        return base64.b64decode(text, validate=True).decode("utf-8", errors="replace")
    except Exception:
        return text


def authenticate(
    username: str,
    password: str,
    *,
    session: Optional[requests.Session] = None,
    status: Optional[NetworkStatus] = None,
) -> NetworkStatus:
    if not username.strip():
        raise AuthenticationError("一卡通号不能为空。")
    if not password:
        raise AuthenticationError("校园网密码不能为空。")

    session = session or build_session()
    status = status or get_status(session)
    if status.authenticated:
        return status
    if not status.ip:
        raise GatewayError("未能从校园网网关获取当前 IP，无法发起认证。")

    params = {
        "c": "Portal",
        "a": "login",
        "callback": "dr1003",
        "login_method": "1",
        "user_account": f",0,{username.strip()}",
        "user_password": password,
        "wlan_user_ip": status.ip,
    }
    data = _request_jsonp(session, PORTAL_URL, params=params)

    if str(data.get("result", "")) == "1":
        return NetworkStatus(authenticated=True, ip=status.ip, raw=data)

    message = _decode_message(data.get("msg")).strip()
    normalized = message.lower()
    known = {
        "ldap auth error": "一卡通号或密码错误。",
        "userid error1": "一卡通号不存在。",
        "userid error2": "校园网密码错误。",
    }
    if normalized in known:
        raise AuthenticationError(known[normalized])
    if message:
        raise AuthenticationError(f"登录失败：{message}")
    raise AuthenticationError("登录失败，校园网没有返回明确原因。")


def load_username() -> Optional[str]:
    try:
        data = json.loads(CONFIG_FILE.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return None
    except (OSError, json.JSONDecodeError):
        return None
    username = data.get("username") if isinstance(data, dict) else None
    return str(username).strip() if username else None


def save_username(username: str) -> None:
    CONFIG_FILE.parent.mkdir(parents=True, exist_ok=True)
    CONFIG_FILE.write_text(
        json.dumps({"username": username.strip()}, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def load_password(username: str) -> Optional[str]:
    if keyring is None:
        return None
    try:
        return keyring.get_password(KEYRING_SERVICE, username)
    except KeyringError:
        return None


def save_password(username: str, password: str) -> bool:
    if keyring is None:
        return False
    try:
        keyring.set_password(KEYRING_SERVICE, username, password)
        return True
    except KeyringError:
        return False


def delete_saved_credentials() -> None:
    username = load_username()
    if username and keyring is not None:
        try:
            keyring.delete_password(KEYRING_SERVICE, username)
        except Exception:
            pass
    try:
        CONFIG_FILE.unlink()
    except FileNotFoundError:
        pass


def setup_credentials() -> tuple[str, str]:
    old_username = load_username()
    prompt = "东南大学一卡通号"
    if old_username:
        prompt += f" [{old_username}]"
    username = input(f"{prompt}: ").strip() or (old_username or "")
    if not username:
        raise AuthenticationError("一卡通号不能为空。")

    password = getpass.getpass("校园网密码（输入时不会显示）: ")
    if not password:
        raise AuthenticationError("校园网密码不能为空。")

    save_username(username)
    if save_password(username, password):
        print("✓ 账号已保存，密码已写入系统凭据管理器。")
    else:
        print("! 无法使用系统凭据管理器；本次仍可登录，但下次需要重新输入密码。")
    return username, password


def get_credentials(*, force_setup: bool = False) -> tuple[str, str]:
    if force_setup:
        return setup_credentials()

    username = load_username()
    if not username:
        print("首次运行，需要先配置校园网账号。")
        return setup_credentials()

    password = load_password(username)
    if password:
        return username, password

    print(f"已找到一卡通号 {username}，但未找到已保存的密码。")
    password = getpass.getpass("校园网密码（输入时不会显示）: ")
    if not password:
        raise AuthenticationError("校园网密码不能为空。")
    if save_password(username, password):
        print("✓ 密码已写入系统凭据管理器。")
    return username, password


def print_status(status: NetworkStatus) -> None:
    if status.authenticated:
        suffix = f"（IP: {status.ip}）" if status.ip else ""
        print(f"✓ 已通过 seu-wlan 校园网认证{suffix}")
    else:
        suffix = f"（IP: {status.ip}）" if status.ip else ""
        print(f"○ 已连接校园网，但尚未认证{suffix}")


def cmd_login() -> int:
    session = build_session()
    status = get_status(session)
    if status.authenticated:
        print_status(status)
        return 0

    print_status(status)
    username, password = get_credentials()
    print("正在认证……")
    result = authenticate(username, password, session=session, status=status)
    print_status(result)
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="东南大学 seu-wlan 命令行自动登录工具")
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--status", action="store_true", help="仅检查当前校园网认证状态")
    group.add_argument("--setup", action="store_true", help="重新设置一卡通号和校园网密码")
    group.add_argument("--forget", action="store_true", help="删除本机保存的账号与密码")
    return parser


def main(argv: Optional[list[str]] = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        if args.forget:
            delete_saved_credentials()
            print("✓ 已删除本机保存的校园网账号信息。")
            return 0
        if args.setup:
            setup_credentials()
            return 0
        if args.status:
            print_status(get_status())
            return 0
        return cmd_login()
    except KeyboardInterrupt:
        print("\n已取消。")
        return 130
    except SeuWlanError as exc:
        print(f"✗ {exc}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
