from __future__ import annotations

import html
import os
import shutil
import subprocess
import sys
from pathlib import Path

APP_DIR_NAME = "SEU-WLAN-AUTOLOGIN"
EXE_NAME = "SEU-WLAN-AUTOLOGIN.exe"
WINDOWS_STARTUP_NAME = "SEU-WLAN-AUTOLOGIN.cmd"
MAC_LAUNCH_AGENT = "io.github.lynviii.seu-wlan-autologin.plist"
LINUX_SERVICE_NAME = "seu-wlan-autologin.service"


def is_frozen() -> bool:
    return bool(getattr(sys, "frozen", False))


def _startup_dir() -> Path:
    if os.name != "nt":
        raise RuntimeError("当前平台不是 Windows。")
    appdata = os.environ.get("APPDATA")
    if not appdata:
        raise RuntimeError("无法定位 Windows Startup 文件夹。")
    return Path(appdata) / "Microsoft" / "Windows" / "Start Menu" / "Programs" / "Startup"


def _local_app_dir() -> Path:
    if os.name != "nt":
        raise RuntimeError("当前平台不是 Windows。")
    local_appdata = os.environ.get("LOCALAPPDATA")
    if not local_appdata:
        raise RuntimeError("无法定位 Windows LocalAppData 文件夹。")
    return Path(local_appdata) / APP_DIR_NAME


def _mac_launch_agents_dir() -> Path:
    return Path.home() / "Library" / "LaunchAgents"


def _linux_user_service_dir() -> Path:
    return Path.home() / ".config" / "systemd" / "user"


def startup_file() -> Path:
    if os.name == "nt":
        return _startup_dir() / WINDOWS_STARTUP_NAME
    if sys.platform == "darwin":
        return _mac_launch_agents_dir() / MAC_LAUNCH_AGENT
    return _linux_user_service_dir() / LINUX_SERVICE_NAME


def installed_executable() -> Path:
    return _local_app_dir() / EXE_NAME


def _install_frozen_executable() -> Path:
    source = Path(sys.executable).resolve()
    target = installed_executable()
    target.parent.mkdir(parents=True, exist_ok=True)

    if source != target.resolve():
        shutil.copy2(source, target)

    return target


def _source_command(entry_script: Path) -> list[str]:
    return [str(Path(sys.executable).resolve()), str(entry_script.resolve()), "--watch", "--quiet"]


def _install_windows(entry_script: Path) -> Path:
    target = startup_file()
    target.parent.mkdir(parents=True, exist_ok=True)

    if is_frozen():
        _install_frozen_executable()
        command = (
            '@echo off\r\n'
            'start "" /min "%LOCALAPPDATA%\\SEU-WLAN-AUTOLOGIN\\'
            'SEU-WLAN-AUTOLOGIN.exe" --watch --quiet\r\n'
        )
        target.write_text(command, encoding="ascii")
        return target

    python = Path(sys.executable)
    pythonw = python.with_name("pythonw.exe")
    executable = pythonw if pythonw.exists() else python
    command = (
        f'@echo off\r\n'
        f'start "" /min "{executable}" "{entry_script.resolve()}" --watch --quiet\r\n'
    )
    target.write_text(command, encoding="utf-8")
    return target


def _install_macos(entry_script: Path) -> Path:
    target = startup_file()
    target.parent.mkdir(parents=True, exist_ok=True)
    args = _source_command(entry_script)

    arg_xml = "\n".join(f"      <string>{html.escape(arg)}</string>" for arg in args)
    plist = f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>Label</key>
  <string>io.github.lynviii.seu-wlan-autologin</string>
  <key>ProgramArguments</key>
  <array>
{arg_xml}
  </array>
  <key>RunAtLoad</key>
  <true/>
  <key>KeepAlive</key>
  <true/>
</dict>
</plist>
"""
    target.write_text(plist, encoding="utf-8")

    domain = f"gui/{os.getuid()}"
    subprocess.run(["launchctl", "bootout", domain, str(target)], check=False, capture_output=True)
    result = subprocess.run(["launchctl", "bootstrap", domain, str(target)], check=False, capture_output=True)
    if result.returncode != 0:
        raise RuntimeError("LaunchAgent 已写入，但 launchctl 启动失败。请检查系统权限。")
    return target


def _systemd_quote(value: str) -> str:
    return '"' + value.replace("\\", "\\\\").replace('"', '\\"') + '"'


def _install_linux(entry_script: Path) -> Path:
    if not shutil.which("systemctl"):
        raise RuntimeError("当前 Linux 环境未找到 systemctl，无法安装用户级 systemd 守护。")

    target = startup_file()
    target.parent.mkdir(parents=True, exist_ok=True)
    command = " ".join(_systemd_quote(arg) for arg in _source_command(entry_script))
    unit = f"""[Unit]
Description=SEU WLAN AutoLogin
After=network-online.target

[Service]
Type=simple
ExecStart={command}
Restart=on-failure
RestartSec=10

[Install]
WantedBy=default.target
"""
    target.write_text(unit, encoding="utf-8")

    subprocess.run(["systemctl", "--user", "daemon-reload"], check=True)
    subprocess.run(["systemctl", "--user", "enable", "--now", LINUX_SERVICE_NAME], check=True)
    return target


def install(entry_script: Path) -> Path:
    if os.name == "nt":
        return _install_windows(entry_script)
    if sys.platform == "darwin":
        return _install_macos(entry_script)
    return _install_linux(entry_script)


def uninstall() -> bool:
    target = startup_file()
    existed = target.exists()

    if os.name == "nt":
        if existed:
            target.unlink()
        return existed

    if sys.platform == "darwin":
        domain = f"gui/{os.getuid()}"
        subprocess.run(["launchctl", "bootout", domain, str(target)], check=False, capture_output=True)
        if existed:
            target.unlink()
        return existed

    if shutil.which("systemctl"):
        subprocess.run(["systemctl", "--user", "disable", "--now", LINUX_SERVICE_NAME], check=False)
        subprocess.run(["systemctl", "--user", "daemon-reload"], check=False)
    if existed:
        target.unlink()
    return existed


def startup_installed() -> bool:
    return startup_file().exists()
