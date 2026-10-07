# Platform Support

| 平台 | 当前方案 | 自动化程度 | 状态 |
| --- | --- | --- | --- |
| Windows | Python + Credential Manager + Startup | 登录系统后后台守护 | Ready for field test |
| macOS / Linux | Python + keyring | 一次运行 / 持续守护 | Ready for field test |
| Android | Termux + Termux:Boot / Tasker | 开机守护或 Wi-Fi 事件触发 | Ready for field test |
| iOS / iPadOS | Shortcuts + Scriptable | 连接 `seu-wlan` 自动触发 | Ready for field test |
| HarmonyOS | ArkTS 原生实现 | 一键登录明确可行；冷启动自动唤醒仍需设备验证 | Prototype |

平台实现细节分别放在对应目录中。
