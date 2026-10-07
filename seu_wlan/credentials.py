from __future__ import annotations

import getpass
import json
import os
import sys
from pathlib import Path

APP_NAME = "SEU-WLAN-AUTOLOGIN"
SERVICE_NAME = APP_NAME
ENV_USERNAME = "SEU_WLAN_USERNAME"
ENV_PASSWORD = "SEU_WLAN_PASSWORD"

try:
    import keyring
except ImportError:
    keyring = None


def config_dir() -> Path:
    if os.name == "nt":
        return Path(os.environ.get("APPDATA", str(Path.home()))) / APP_NAME
    if sys.platform == "darwin":
        return Path.home() / "Library" / "Application Support" / APP_NAME
    return Path(os.environ.get("XDG_CONFIG_HOME", str(Path.home() / ".config"))) / APP_NAME


CONFIG_FILE = config_dir() / "config.json"
LOG_FILE = config_dir() / "autologin.log"


def _read_username() -> str | None:
    env = os.getenv(ENV_USERNAME)
    if env:
        return env.strip() or None
    try:
        data = json.loads(CONFIG_FILE.read_text(encoding="utf-8"))
    except (FileNotFoundError, OSError, json.JSONDecodeError):
        return None
    value = data.get("username") if isinstance(data, dict) else None
    return str(value).strip() if value else None


def _write_username(username: str) -> None:
    CONFIG_FILE.parent.mkdir(parents=True, exist_ok=True)
    CONFIG_FILE.write_text(json.dumps({"username": username}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def _read_password(username: str) -> str | None:
    env = os.getenv(ENV_PASSWORD)
    if env:
        return env
    if keyring is None:
        return None
    try:
        return keyring.get_password(SERVICE_NAME, username)
    except Exception:
        return None


def _write_password(username: str, password: str) -> bool:
    if keyring is None:
        return False
    try:
        keyring.set_password(SERVICE_NAME, username, password)
        return True
    except Exception:
        return False


def setup() -> tuple[str, str, bool]:
    previous = _read_username()
    prompt = "东南大学一卡通号"
    if previous:
        prompt += f" [{previous}]"
    username = input(f"{prompt}: ").strip() or (previous or "")
    if not username:
        raise ValueError("一卡通号不能为空。")

    password = getpass.getpass("校园网密码（输入时不会显示）: ")
    if not password:
        raise ValueError("校园网密码不能为空。")

    _write_username(username)
    stored = _write_password(username, password)
    return username, password, stored


def get(interactive: bool = True) -> tuple[str, str]:
    username = _read_username()
    password = _read_password(username) if username else None
    if username and password:
        return username, password
    if not interactive:
        missing = "账号和密码" if not username else "密码"
        raise ValueError(f"缺少已保存的{missing}。")
    username, password, _ = setup()
    return username, password


def forget() -> None:
    username = _read_username()
    if username and keyring is not None:
        try:
            keyring.delete_password(SERVICE_NAME, username)
        except Exception:
            pass
    try:
        CONFIG_FILE.unlink()
    except FileNotFoundError:
        pass
