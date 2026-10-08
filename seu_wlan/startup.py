from __future__ import annotations

import os
import shutil
import sys
from pathlib import Path

APP_DIR_NAME = "SEU-WLAN-AUTOLOGIN"
EXE_NAME = "SEU-WLAN-AUTOLOGIN.exe"
STARTUP_NAME = "SEU-WLAN-AUTOLOGIN.cmd"


def is_frozen() -> bool:
    return bool(getattr(sys, "frozen", False))


def _startup_dir() -> Path:
    if os.name != "nt":
        raise RuntimeError("当前自动启动安装器只支持 Windows。")
    appdata = os.environ.get("APPDATA")
    if not appdata:
        raise RuntimeError("无法定位 Windows Startup 文件夹。")
    return Path(appdata) / "Microsoft" / "Windows" / "Start Menu" / "Programs" / "Startup"


def _local_app_dir() -> Path:
    if os.name != "nt":
        raise RuntimeError("当前应用安装目录只支持 Windows。")
    local_appdata = os.environ.get("LOCALAPPDATA")
    if not local_appdata:
        raise RuntimeError("无法定位 Windows LocalAppData 文件夹。")
    return Path(local_appdata) / APP_DIR_NAME


def startup_file() -> Path:
    return _startup_dir() / STARTUP_NAME


def installed_executable() -> Path:
    return _local_app_dir() / EXE_NAME


def _install_frozen_executable() -> Path:
    source = Path(sys.executable).resolve()
    target = installed_executable()
    target.parent.mkdir(parents=True, exist_ok=True)

    if source != target.resolve():
        shutil.copy2(source, target)

    return target


def install(entry_script: Path) -> Path:
    target = startup_file()
    target.parent.mkdir(parents=True, exist_ok=True)

    if is_frozen():
        _install_frozen_executable()
        # Keep the batch file ASCII-only by using %LOCALAPPDATA%, avoiding
        # code-page issues when a Windows username contains non-ASCII text.
        command = (
            '@echo off\r\n'
            'start "" /min "%LOCALAPPDATA%\\SEU-WLAN-AUTOLOGIN\\'
            'SEU-WLAN-AUTOLOGIN.exe" --watch --quiet\r\n'
        )
    else:
        python = Path(sys.executable)
        pythonw = python.with_name("pythonw.exe")
        executable = pythonw if pythonw.exists() else python
        command = (
            f'@echo off\r\n'
            f'start "" /min "{executable}" "{entry_script.resolve()}" --watch --quiet\r\n'
        )

    target.write_text(command, encoding="ascii" if is_frozen() else "utf-8")
    return target


def uninstall() -> bool:
    target = startup_file()
    if not target.exists():
        return False
    target.unlink()
    return True


def startup_installed() -> bool:
    return startup_file().exists()
