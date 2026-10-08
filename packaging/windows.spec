# -*- mode: python ; coding: utf-8 -*-
import os
import re

from PyInstaller.utils.hooks import collect_all, copy_metadata

ROOT = os.path.abspath(os.path.join(SPECPATH, ".."))
ENTRY = os.path.join(ROOT, "autologin.py")


def read_version():
    init_file = os.path.join(ROOT, "seu_wlan", "__init__.py")
    with open(init_file, "r", encoding="utf-8") as handle:
        text = handle.read()
    match = re.search(r'__version__\s*=\s*["\']([^"\']+)["\']', text)
    if not match:
        raise RuntimeError("Unable to read seu_wlan.__version__")
    return match.group(1)


VERSION = read_version()
version_parts = [int(item) for item in re.findall(r"\d+", VERSION)[:4]]
version_parts += [0] * (4 - len(version_parts))
version_tuple = tuple(version_parts[:4])

version_dir = os.path.join(ROOT, "build")
os.makedirs(version_dir, exist_ok=True)
VERSION_FILE = os.path.join(version_dir, "version_info.txt")

with open(VERSION_FILE, "w", encoding="utf-8") as handle:
    handle.write(
        f"""VSVersionInfo(
  ffi=FixedFileInfo(
    filevers={version_tuple},
    prodvers={version_tuple},
    mask=0x3f,
    flags=0x0,
    OS=0x40004,
    fileType=0x1,
    subtype=0x0,
    date=(0, 0)
  ),
  kids=[
    StringFileInfo(
      [
        StringTable(
          '040904B0',
          [
            StringStruct('CompanyName', 'LynViii'),
            StringStruct('FileDescription', 'SEU seu-wlan automatic login tool'),
            StringStruct('FileVersion', '{VERSION}'),
            StringStruct('InternalName', 'SEU-WLAN-AUTOLOGIN'),
            StringStruct('LegalCopyright', 'Copyright (c) 2019 NN708; Copyright (c) 2026 LynViii'),
            StringStruct('OriginalFilename', 'SEU-WLAN-AUTOLOGIN.exe'),
            StringStruct('ProductName', 'SEU-WLAN-AUTOLOGIN'),
            StringStruct('ProductVersion', '{VERSION}')
          ]
        )
      ]
    ),
    VarFileInfo([VarStruct('Translation', [1033, 1200])])
  ]
)
"""
    )

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
