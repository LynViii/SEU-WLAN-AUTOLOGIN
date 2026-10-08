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
        appdata = os.environ.get("APPDATA")
        base = Path(appdata) if appdata else Path.home()
        return base / APP_NAME
    if sys.platform == "darwin":
        return Path.home() / "Library" / "Application Support" / APP_NAME
    xdg_config = os.environ.get("XDG_CONFIG_HOME")
    base = Path(xdg_config) if xdg_config else Path.home() / ".config"
    return base / APP_NAME


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
    CONFIG_FILE.write_text(
        json.dumps({"username": username}, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def _read_password_from_keyring(username: str) -> str | None:
    if keyring is None:
        return None
    try:
        return keyring.get_password(SERVICE_NAME, username)
    except Exception:
        return None


def _read_password(username: str) -> str | None:
    env = os.getenv(ENV_PASSWORD)
    if env:
        return env
    return _read_password_from_keyring(username)


def _write_password(username: str, password: str) -> bool:
    if keyring is None:
        return False
    try:
        keyring.set_password(SERVICE_NAME, username, password)
        return True
    except Exception:
        return False


def _masked_password(prompt: str) -> str:
    """Read a password while showing one * per entered character when possible."""
    if os.name == "nt":
        import msvcrt

        sys.stdout.write(prompt)
        sys.stdout.flush()
        chars: list[str] = []

        while True:
            char = msvcrt.getwch()

            if char in ("\r", "\n"):
                sys.stdout.write("\n")
                sys.stdout.flush()
                return "".join(chars)

            if char == "\x03":
                sys.stdout.write("\n")
                sys.stdout.flush()
                raise KeyboardInterrupt

            if char == "\b":
                if chars:
                    chars.pop()
                    sys.stdout.write("\b \b")
                    sys.stdout.flush()
                continue

            if char in ("\x00", "\xe0"):
                msvcrt.getwch()
                continue

            if char.isprintable():
                chars.append(char)
                sys.stdout.write("*")
                sys.stdout.flush()

    if not sys.stdin.isatty():
        return getpass.getpass(prompt)

    try:
        import termios
        import tty

        fd = sys.stdin.fileno()
        previous = termios.tcgetattr(fd)
        chars: list[str] = []

        sys.stdout.write(prompt)
        sys.stdout.flush()
        tty.setraw(fd)
        try:
            while True:
                char = sys.stdin.read(1)
                if char in ("\r", "\n"):
                    sys.stdout.write("\r\n")
                    sys.stdout.flush()
                    return "".join(chars)

                if char == "\x03":
                    sys.stdout.write("\r\n")
                    sys.stdout.flush()
                    raise KeyboardInterrupt

                if char in ("\x08", "\x7f"):
                    if chars:
                        chars.pop()
                        sys.stdout.write("\b \b")
                        sys.stdout.flush()
                    continue

                if char.isprintable():
                    chars.append(char)
                    sys.stdout.write("*")
                    sys.stdout.flush()
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, previous)
    except (ImportError, OSError):
        return getpass.getpass(prompt)


def store(username: str, password: str) -> bool:
    username = username.strip()
    if not username or not password:
        return False
    _write_username(username)
    return _write_password(username, password)


def has_persisted_password(username: str) -> bool:
    return bool(_read_password_from_keyring(username))


def setup() -> tuple[str, str, bool]:
    previous = _read_username()
    prompt = "东南大学一卡通号"
    if previous:
        prompt += f" [{previous}]"
    username = input(f"{prompt}: ").strip() or (previous or "")
    if not username:
        raise ValueError("一卡通号不能为空。")

    password = _masked_password("校园网密码（输入内容显示为 *）: ")
    if not password:
        raise ValueError("校园网密码不能为空。")

    stored = store(username, password)
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
