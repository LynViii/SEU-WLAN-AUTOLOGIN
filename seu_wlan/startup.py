from __future__ import annotations

import os
import sys
from pathlib import Path

STARTUP_NAME = "SEU-WLAN-AUTOLOGIN.cmd"


def _startup_dir() -> Path:
    if os.name != "nt":
        raise RuntimeError("当前自动启动安装器只支持 Windows。")
    appdata = os.environ.get("APPDATA")
    if not appdata:
        raise RuntimeError("无法定位 Windows Startup 文件夹。")
    return Path(appdata) / "Microsoft" / "Windows" / "Start Menu" / "Programs" / "Startup"


def startup_file() -> Path:
    return _startup_dir() / STARTUP_NAME


def install(entry_script: Path) -> Path:
    target = startup_file()
    target.parent.mkdir(parents=True, exist_ok=True)
    python = Path(sys.executable)
    pythonw = python.with_name("pythonw.exe")
    executable = pythonw if pythonw.exists() else python
    command = f'@echo off\r\nstart "" /min "{executable}" "{entry_script.resolve()}" --watch --quiet\r\n'
    target.write_text(command, encoding="utf-8")
    return target


def uninstall() -> bool:
    target = startup_file()
    if not target.exists():
        return False
    target.unlink()
    return True
