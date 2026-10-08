from __future__ import annotations

import base64
import json
import time
from dataclasses import dataclass
from typing import Any

import requests

from . import __version__
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

STATUS_URL = "https://w.seu.edu.cn/drcom/chkstatus"
LOGIN_URL = "https://w.seu.edu.cn:801/eportal/"
TIMEOUT = (3.05, 8.0)


class SeuWlanError(RuntimeError):
    pass


class GatewayUnavailable(SeuWlanError):
    pass


class AuthenticationRejected(SeuWlanError):
    pass


@dataclass(frozen=True)
class Status:
    authenticated: bool
    ip: str = ""


def make_session() -> requests.Session:
    retry = Retry(
        total=2,
        connect=2,
        read=2,
        status=2,
        backoff_factor=0.3,
        status_forcelist=(502, 503, 504),
        allowed_methods=frozenset({"GET"}),
        raise_on_status=False,
    )
    adapter = HTTPAdapter(max_retries=retry)
    session = requests.Session()
    session.mount("https://", adapter)
    session.headers.update({"User-Agent": f"SEU-WLAN-AUTOLOGIN/{__version__}"})
    return session


def parse_jsonp(payload: str) -> dict[str, Any]:
    start = payload.find("{")
    end = payload.rfind("}")
    if start < 0 or end <= start:
        raise GatewayUnavailable("认证网关返回了无法识别的数据。")
    try:
        data = json.loads(payload[start : end + 1])
    except json.JSONDecodeError as exc:
        raise GatewayUnavailable("认证网关返回了无效 JSON。") from exc
    if not isinstance(data, dict):
        raise GatewayUnavailable("认证网关返回的数据格式异常。")
    return data


def _get_jsonp(session: requests.Session, url: str, params: dict[str, str]) -> dict[str, Any]:
    try:
        response = session.get(url, params=params, timeout=TIMEOUT)
        response.raise_for_status()
    except requests.RequestException as exc:
        raise GatewayUnavailable("无法访问 SEU 校园网认证网关，请确认设备已连接 seu-wlan。") from exc
    return parse_jsonp(response.text)


def status(session: requests.Session | None = None) -> Status:
    session = session or make_session()
    data = _get_jsonp(session, STATUS_URL, {"callback": "dr1002"})
    result = str(data.get("result", ""))
    ip = str(data.get("v46ip") or data.get("v4ip") or data.get("ss5") or "")
    if result == "1":
        return Status(True, ip)
    if result == "0":
        return Status(False, ip)
    raise GatewayUnavailable(f"认证网关返回未知状态：result={result!r}")


def _decode_message(raw: Any) -> str:
    if raw is None:
        return ""
    text = str(raw)
    try:
        return base64.b64decode(text, validate=True).decode("utf-8", errors="replace")
    except Exception:
        return text


def login(
    username: str,
    password: str,
    session: requests.Session | None = None,
    known_status: Status | None = None,
) -> Status:
    username = username.strip()
    if not username:
        raise AuthenticationRejected("一卡通号不能为空。")
    if not password:
        raise AuthenticationRejected("校园网密码不能为空。")

    session = session or make_session()
    current = known_status or status(session)
    if current.authenticated:
        return current
    if not current.ip:
        raise GatewayUnavailable("认证网关没有返回当前校园网 IP。")

    data = _get_jsonp(
        session,
        LOGIN_URL,
        {
            "c": "Portal",
            "a": "login",
            "callback": "dr1003",
            "login_method": "1",
            "user_account": f",0,{username}",
            "user_password": password,
            "wlan_user_ip": current.ip,
        },
    )

    if str(data.get("result", "")) != "1":
        message = _decode_message(data.get("msg")).strip()
        normalized = message.lower()
        friendly = {
            "ldap auth error": "一卡通号或密码错误。",
            "userid error1": "一卡通号不存在。",
            "userid error2": "校园网密码错误。",
        }.get(normalized)
        raise AuthenticationRejected(friendly or (f"认证失败：{message}" if message else "认证失败。"))

    for _ in range(3):
        time.sleep(0.35)
        verified = status(session)
        if verified.authenticated:
            return verified
    raise GatewayUnavailable("网关返回登录成功，但状态复核仍显示未认证。")
