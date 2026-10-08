# SEU-WLAN-AUTOLOGIN

[![Python checks](https://github.com/LynViii/SEU-WLAN-AUTOLOGIN/actions/workflows/python.yml/badge.svg)](https://github.com/LynViii/SEU-WLAN-AUTOLOGIN/actions/workflows/python.yml)
[![Build Windows EXE](https://github.com/LynViii/SEU-WLAN-AUTOLOGIN/actions/workflows/build-windows.yml/badge.svg)](https://github.com/LynViii/SEU-WLAN-AUTOLOGIN/actions/workflows/build-windows.yml)
![License](https://img.shields.io/badge/License-MIT-green)

一个轻量的东南大学 `seu-wlan` 自动认证工具：第一次配置账号密码后，后续尽量做到连接校园网即可自动认证。

> Windows 已在真实 SEU `seu-wlan` 环境完成自动认证验证。  
> 本项目为非官方开源工具，与东南大学官方无隶属或授权关系。

## 选择你的平台

| 平台 | 推荐方式 | 自动化方式 |
| --- | --- | --- |
| **Windows** | 单文件 `SEU-WLAN-AUTOLOGIN.exe` | Startup 后台守护 |
| Windows 源码 | Python `seu-wlan` CLI | Startup 后台守护 |
| macOS | Python `seu-wlan` CLI | LaunchAgent |
| Linux | Python `seu-wlan` CLI | systemd --user |
| Android | Termux + 安装脚本 | Termux:Boot / Tasker |
| iOS / iPadOS | Scriptable JS + Shortcuts | Wi-Fi 自动化 |
| HarmonyOS | ArkTS 原生小工具 | 原生网络事件 |

**文档入口：** [安装](docs/INSTALL.md) · [平台说明](platforms/) · [常见问题](docs/TROUBLESHOOTING.md) · [架构](docs/ARCHITECTURE.md) · [验证记录](docs/VALIDATION.md)

## Windows：下载一个 EXE

Release 下载：

```text
SEU-WLAN-AUTOLOGIN.exe
```

直接运行，不需要 Python，也不需要保留源码文件夹。

第一次运行：

```text
东南大学一卡通号:
校园网密码（输入内容显示为 *）: ********
正在认证……
✓ 已认证（IP: ...）
```

安装后台自动认证：

```powershell
.\SEU-WLAN-AUTOLOGIN.exe --install-startup
```

程序会把后台副本复制到：

```text
%LOCALAPPDATA%\SEU-WLAN-AUTOLOGIN\SEU-WLAN-AUTOLOGIN.exe
```

因此最初下载的 EXE 后续可以移动或删除。

Windows 后台守护只负责 `seu-wlan` 认证，**不会主动断开、切换或重连其他 Wi-Fi**。

## Python / 源码方式

Windows、macOS、Linux 均可：

```bash
python -m pip install ".[desktop]"
```

安装后：

```bash
seu-wlan
seu-wlan --status
seu-wlan --setup
seu-wlan --watch
seu-wlan --diagnose
seu-wlan --install-startup
seu-wlan --uninstall-startup
```

不安装包也可以：

```bash
python autologin.py
```

## 手机端

**Android** 使用 Termux 安装脚本，复用 Python 核心；需要省电时可以用 Tasker 在连接 `seu-wlan` 时仅触发一次认证。详见 [Android](platforms/android/)。

**iOS / iPadOS** 使用一个 Scriptable JS，通过 Shortcuts 的 `Wi-Fi → seu-wlan` 自动化触发，凭据保存在 Scriptable Keychain。详见 [iOS](platforms/ios/)。

**HarmonyOS** 使用 ArkTS 原生实现，当前仓库提供认证核心，后续 HAP 使用 Asset Store 保存敏感凭据。详见 [HarmonyOS](platforms/harmonyos/)。

## 核心流程

所有实现遵循相同的认证协议流程：

```text
chkstatus
→ 已认证：结束
→ 未认证：获取校园网 IP
→ ePortal 登录
→ 再查 chkstatus
→ 复核成功才算认证成功
```

## 安全与隐私

- 不包含遥测；
- 不主动上传账号、密码、校园网 IP 或使用记录；
- Windows/macOS/Linux 优先使用系统凭据存储；
- iOS 使用 Scriptable Keychain；
- Android Boot 自动化使用 Termux 应用私有目录中的 `600` 配置文件，并明确其本地明文属性；
- SEU 当前 ePortal 协议会把密码作为 HTTPS GET 查询参数发送，因此不要公开完整请求 URL 或抓包日志。

详见 [Security Policy](.github/SECURITY.md)。

## Release 内容

正式版本由 GitHub Actions 自动生成：

```text
SEU-WLAN-AUTOLOGIN.exe
SHA256SUMS.txt
seu_wlan_autologin-*.whl
seu_wlan_autologin-*.tar.gz
SEU-WLAN-AUTOLOGIN-Scriptable.js
SEU-WLAN-AUTOLOGIN-Termux-install.sh
SEU-WLAN-AUTOLOGIN-Termux-uninstall.sh
Source code
```

## 项目结构

```text
SEU-WLAN-AUTOLOGIN/
├── autologin.py       # Python CLI 主入口
├── seu_wlan/          # 认证、凭据、后台守护核心
├── platforms/         # 各平台入口与安装方案
├── packaging/         # Windows EXE 打包
├── docs/              # 安装、架构、排障、验证记录
├── tests/             # 单元与回归测试
├── .github/           # CI、Release、Issue 模板、安全说明
├── pyproject.toml     # Python 包与依赖唯一配置
├── CHANGELOG.md
└── LICENSE
```

## 来源与许可

SEU Dr.COM / ePortal 的早期认证流程参考并改进自 [NN708/seu-wlan-login](https://github.com/NN708/seu-wlan-login)。当前实现已重新设计凭据存储、异常处理、认证复核、后台守护、日志、测试、打包和多平台入口。

本仓库采用 MIT License，并按 MIT 条款保留相关版权声明。
