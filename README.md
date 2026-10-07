# SEU-WLAN-AUTOLOGIN

[![Python checks](https://github.com/LynViii/SEU-WLAN-AUTOLOGIN/actions/workflows/python.yml/badge.svg)](https://github.com/LynViii/SEU-WLAN-AUTOLOGIN/actions/workflows/python.yml)
![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![License](https://img.shields.io/badge/License-MIT-green)

东南大学 `seu-wlan` 自动认证工具。核心目标只有一个：**第一次配置账号密码后，以后尽可能自动完成校园网认证。**

> 当前代码、模拟网关测试与 CI 已通过；真实 SEU 校园网链路将在现场完成最终验证。

## Desktop 快速开始

```bash
git clone https://github.com/LynViii/SEU-WLAN-AUTOLOGIN.git
cd SEU-WLAN-AUTOLOGIN
python -m pip install -r requirements/desktop.txt
python autologin.py
```

第一次运行输入一卡通号和密码；以后再次运行 `python autologin.py` 会直接读取本机保存的凭据并自动判断是否需要认证。

常用命令：

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
| Windows | Python + Credential Manager + Startup | 待现场验证 |
| macOS / Linux | Python + keyring | 待现场验证 |
| Android | Termux + Termux:Boot / Tasker | 待现场验证 |
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

## Windows 自动认证

第一次完成凭据配置后：

```bash
python autologin.py --install-startup
```

以后登录 Windows 后后台启动守护，连接到 `seu-wlan` 时自动检查并补登。具体见 [`platforms/windows/`](platforms/windows/)。

## 明天现场验证

请严格按 [`docs/FIELD_TEST.md`](docs/FIELD_TEST.md) 的顺序测试：先单次登录，再凭据复用，再断线重连，再守护，最后才安装 Startup。

## 仓库结构

```text
SEU-WLAN-AUTOLOGIN/
├── autologin.py
├── seu_wlan/              # Python 核心
├── platforms/             # Windows / Android / iOS / HarmonyOS
├── requirements/          # Python 依赖
├── tests/                 # 自动测试
├── docs/                  # 架构与现场测试
├── .github/               # CI / Issue / 维护说明
├── CHANGELOG.md
├── LICENSE
└── README.md
```

## 安全

- 不把密码写入仓库；
- 桌面端使用系统凭据存储；
- iOS 使用 Scriptable Keychain；
- Android 自动化凭据仅保存在 Termux 私有目录；
- 项目不包含遥测。

安全说明见 [`.github/SECURITY.md`](.github/SECURITY.md)。

## License

MIT License.
