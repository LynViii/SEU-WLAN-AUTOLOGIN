# SEU-WLAN-AUTOLOGIN

[![Python checks](https://github.com/LynViii/SEU-WLAN-AUTOLOGIN/actions/workflows/python.yml/badge.svg)](https://github.com/LynViii/SEU-WLAN-AUTOLOGIN/actions/workflows/python.yml)
[![Build Windows EXE](https://github.com/LynViii/SEU-WLAN-AUTOLOGIN/actions/workflows/build-windows.yml/badge.svg)](https://github.com/LynViii/SEU-WLAN-AUTOLOGIN/actions/workflows/build-windows.yml)
![License](https://img.shields.io/badge/License-MIT-green)

一个轻量的东南大学 `seu-wlan` 自动认证工具：**第一次配置账号密码，之后尽量做到连接校园网后自动认证。**

> Windows 已在真实 SEU `seu-wlan` 环境验证成功。  
> 本项目为非官方开源工具，与东南大学官方无隶属或授权关系。

## 直接选你的平台

| 平台 | 普通用户推荐方式 | 自动化 | 状态 |
| --- | --- | --- | --- |
| **Windows** | 单文件 `SEU-WLAN-AUTOLOGIN.exe` | Startup 后台守护 | **真实校园网已验证** |
| Windows 开发者 | Python 源码 / `seu-wlan` CLI | Startup 后台守护 | **已验证** |
| macOS | Python `seu-wlan` CLI | LaunchAgent | 待真实校园网实测 |
| Linux | Python `seu-wlan` CLI | systemd --user | 待真实校园网实测 |
| Android | Termux + 一键安装脚本 | Termux:Boot / Tasker | 待真机实测 |
| iOS / iPadOS | Scriptable 单文件 JS + Shortcuts | Wi-Fi 自动化 | 待真机实测 |
| HarmonyOS | ArkTS 原生小工具 | 规划中 | Prototype |

完整安装说明：[`docs/INSTALL.md`](docs/INSTALL.md)

## Windows：最简单

公开 Release 后下载：

```text
SEU-WLAN-AUTOLOGIN.exe
```

直接运行即可，不需要 Python，也不需要源码文件夹。

第一次运行：

```text
东南大学一卡通号:
校园网密码（输入内容显示为 *）: ********
正在认证……
✓ 已认证（IP: ...）
```

安装自动守护：

```powershell
.\SEU-WLAN-AUTOLOGIN.exe --install-startup
```

EXE 会把后台使用的副本复制到：

```text
%LOCALAPPDATA%\SEU-WLAN-AUTOLOGIN\SEU-WLAN-AUTOLOGIN.exe
```

所以**你下载到桌面、下载目录或 U 盘的那份 EXE 之后可以随便移动或删除**，已经安装的后台守护不受影响。

## Python / 源码方式

Windows、macOS、Linux 都可以：

```bash
python -m pip install ".[desktop]"
```

安装后统一使用：

```bash
seu-wlan
seu-wlan --status
seu-wlan --setup
seu-wlan --watch
seu-wlan --diagnose
seu-wlan --install-startup
seu-wlan --uninstall-startup
```

不安装包也可以继续：

```bash
python autologin.py
```

## 手机端

### Android

Termux 中运行仓库自带的一键安装脚本：

```bash
bash platforms/android/install-termux.sh
```

详细见 [Android](platforms/android/)。

### iOS / iPadOS

Release 提供单个：

```text
SEU-WLAN-AUTOLOGIN-Scriptable.js
```

导入 Scriptable 后，用 Shortcuts 的 `Wi-Fi → seu-wlan` 自动化触发。账号密码保存在 Scriptable Keychain。

详细见 [iOS](platforms/ios/)。

### HarmonyOS

已经提供 ArkTS 的 SEU 认证核心。最终目标是一个极简 HAP：打开即可登录，密码使用 HarmonyOS Asset Store 保存；系统级冷启动 Wi-Fi 自动触发仍需真机验证。

详细见 [HarmonyOS](platforms/harmonyos/)。

## 核心流程

所有平台都遵循同一条认证逻辑：

```text
chkstatus
→ 已认证：结束
→ 未认证：获取校园网 IP
→ ePortal 登录
→ 再查 chkstatus
→ 复核成功才算认证成功
```

架构说明：[`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md)

## 安全与隐私

- 不包含遥测；
- 不主动上传账号、密码、校园网 IP 或使用记录；
- Windows/macOS/Linux 优先使用系统凭据存储；
- iOS 使用 Scriptable Keychain；
- Android Boot 自动化使用 Termux 应用私有目录中的 `600` 配置文件，并在文档中明确其本地明文属性；
- SEU 当前 ePortal 协议会把密码作为 HTTPS GET 查询参数发送，因此不要公开完整请求 URL 或抓包日志。

详见 [Security Policy](.github/SECURITY.md)。

## Release 内容

正式版本计划统一提供：

```text
SEU-WLAN-AUTOLOGIN.exe              # Windows x64 单文件
SHA256SUMS.txt                      # EXE 校验
seu_wlan_autologin-*.whl           # Python 跨平台包
seu_wlan_autologin-*.tar.gz        # Python 源码包
SEU-WLAN-AUTOLOGIN-Scriptable.js   # iOS / iPadOS
Source code                         # GitHub 自动提供
```

## 来源与许可

SEU Dr.COM / ePortal 的早期认证流程参考并改进自 [NN708/seu-wlan-login](https://github.com/NN708/seu-wlan-login)。当前实现已重新设计凭据存储、异常处理、认证复核、后台守护、日志、测试、打包和多平台入口。

本仓库采用 MIT License，并按 MIT 条款保留相关版权声明。
