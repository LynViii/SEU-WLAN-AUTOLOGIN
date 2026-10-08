# Installation Guide

SEU-WLAN-AUTOLOGIN 的目标是让不同平台都尽量使用最轻的入口。

| 平台 | 推荐入口 | 是否需要 Python |
| --- | --- | --- |
| Windows 普通用户 | 单文件 `SEU-WLAN-AUTOLOGIN.exe` | 否 |
| Windows 开发者 | Python 包 / 源码目录 | 是 |
| macOS / Linux | Python 包 / 源码目录 | 是 |
| Android | Termux + Python CLI | Termux 内需要 |
| iOS / iPadOS | Scriptable + Shortcuts | 否 |
| HarmonyOS | ArkTS 小工具 | 否，当前仍为 Prototype |

## Windows：推荐 EXE

Release 中下载：

```text
SEU-WLAN-AUTOLOGIN.exe
```

双击或 PowerShell 运行即可。第一次输入账号密码，之后自动复用凭据。

安装后台自动认证：

```powershell
.\SEU-WLAN-AUTOLOGIN.exe --install-startup
```

程序会把后台使用的副本复制到：

```text
%LOCALAPPDATA%\SEU-WLAN-AUTOLOGIN\SEU-WLAN-AUTOLOGIN.exe
```

因此下载目录里的 EXE 后续可以移动或删除。

## Windows / macOS / Linux：Python 包

下载源码后：

```bash
python -m pip install ".[desktop]"
```

之后统一使用：

```bash
seu-wlan
seu-wlan --status
seu-wlan --setup
seu-wlan --watch
seu-wlan --diagnose
```

也可以不安装包，继续运行：

```bash
python autologin.py
```

## Android

使用 Termux。详见 [Android](../platforms/android/)。

## iOS / iPadOS

只需要 Scriptable 脚本和一个 Shortcuts Wi-Fi 自动化。详见 [iOS](../platforms/ios/)。

## HarmonyOS

当前提供 ArkTS 认证核心；目标是最终提供一个极简 HAP 小工具。详见 [HarmonyOS](../platforms/harmonyos/)。
