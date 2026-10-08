# -*- mode: python ; coding: utf-8 -*-
import os

from PyInstaller.utils.hooks import collect_all, copy_metadata

ROOT = os.path.abspath(os.path.join(SPECPATH, ".."))
ENTRY = os.path.join(ROOT, "autologin.py")
VERSION_FILE = os.path.join(SPECPATH, "version_info.txt")

keyring_datas, keyring_binaries, keyring_hiddenimports = collect_all("keyring")
keyring_datas += copy_metadata("keyring", recursive=True)

a = Analysis(
    [ENTRY],
    pathex=[ROOT],
    binaries=keyring_binaries,
    datas=keyring_datas,
    hiddenimports=keyring_hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name="SEU-WLAN-AUTOLOGIN",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    version=VERSION_FILE,
)
