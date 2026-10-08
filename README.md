# SEU-WLAN-AUTOLOGIN

[![Python checks](https://github.com/LynViii/SEU-WLAN-AUTOLOGIN/actions/workflows/python.yml/badge.svg)](https://github.com/LynViii/SEU-WLAN-AUTOLOGIN/actions/workflows/python.yml)
![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![License](https://img.shields.io/badge/License-MIT-green)

东南大学 `seu-wlan` 自动认证工具。第一次配置账号密码后，后续可自动完成校园网认证。

> **Windows + 真实 SEU `seu-wlan` 已于 2026-10-08 完成现场验证，自动认证成功。**

> 本项目为非官方开源工具，与东南大学官方无隶属或授权关系。请仅使用本人或已获授权的校园网账号，并遵守学校校园网相关规定。

## Windows 快速开始

```bash
git clone https://github.com/LynViii/SEU-WLAN-AUTOLOGIN.git
cd SEU-WLAN-AUTOLOGIN
python -m pip install -r requirements/desktop.txt
python autologin.py
```

第一次运行：

```text
东南大学一卡通号:
校园网密码（输入内容显示为 *）: ********
正在认证……
✓ 已认证（IP: ...）
```

密码只显示等量的 `*`，不会显示真实字符。凭据保存后，再次运行不会重复询问账号密码。

## 常用命令

```bash
python autologin.py
python autologin.py --status
python autologin.py --setup
python autologin.py --forget
python autologin.py --watch
python autologin.py --install-startup
python autologin.py --uninstall-startup
```

## 平台支持

| 平台 | 方案 | 当前状态 |
| --- | --- | --- |
| Windows | Python + Credential Manager + Startup | **真实校园网已验证** |
| macOS / Linux | Python + keyring | 待实测 |
| Android | Termux + Termux:Boot / Tasker | 待实测 |
| iOS / iPadOS | Shortcuts + Scriptable | 已完成实现，待真机验证 |
| HarmonyOS | ArkTS 原生方案 | PoC，后台冷启动能力待验证 |

详细说明见 [`platforms/`](platforms/)。

## 核心认证流程

```text
检查 chkstatus
→ 已认证：结束
→ 未认证：取得校园网 IP
→ 调用 ePortal 登录
→ 再次检查状态
→ 只有复核成功才算登录成功
```

架构说明见 [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md)。

## Windows 后台自动认证

完成一次凭据配置后：

```bash
python autologin.py --install-startup
```

以后登录 Windows 后后台运行 `--watch --quiet`。

守护模式会：

- 连接 `seu-wlan` 时自动检查并补登；
- 当前连接其他 Wi-Fi 时保持等待，不会强制断开其他网络；
- 网关暂时不可达时按设定次数尝试恢复；
- 只在状态变化时记录关键日志，避免重复刷屏；
- 日志使用带 BOM 的 UTF-8，兼容 Windows PowerShell `Get-Content`；
- 日志超过约 512 KB 自动轮转。

Windows 说明见 [`platforms/windows/`](platforms/windows/)。

## 仓库结构

```text
SEU-WLAN-AUTOLOGIN/
├── autologin.py
├── seu_wlan/              # Python 核心
├── platforms/             # Windows / Android / iOS / HarmonyOS
├── requirements/          # Python 依赖
├── tests/                 # 自动测试
├── docs/                  # 架构与现场测试记录
├── .github/               # CI / Issue / 维护说明
├── CHANGELOG.md
├── LICENSE
└── README.md
```

## 安全

- 密码不写入仓库；
- Windows / 桌面端通过系统凭据存储保存密码；
- iOS 使用 Scriptable Keychain；
- Android 自动化凭据仅保存在 Termux 私有目录；
- 项目不包含遥测。

安全说明见 [`.github/SECURITY.md`](.github/SECURITY.md)。

## 来源与许可

本项目的 SEU Dr.COM / ePortal 认证流程参考并改进自 [NN708/seu-wlan-login](https://github.com/NN708/seu-wlan-login)。上游项目采用 MIT License；本仓库保留上游版权声明，并继续采用 MIT License。

当前实现已对凭据存储、异常处理、状态复核、Windows 后台守护、日志、测试及多平台方案进行了重新设计和扩展。

## License

MIT License.
