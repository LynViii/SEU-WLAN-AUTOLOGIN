# -*- mode: python ; coding: utf-8 -*-
import os

from PyInstaller.utils.hooks import collect_all, copy_metadata

keyring_datas, keyring_binaries, keyring_hiddenimports = collect_all("keyring")
keyring_datas += copy_metadata("keyring", recursive=True)

a = Analysis(
    ["autologin.py"],
    pathex=["."],
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
    version=os.path.join(SPECPATH, "version_info.txt"),
)
