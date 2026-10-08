# Platform Support

各平台使用尽量轻量、符合系统习惯的入口，认证协议流程保持一致。

| 平台 | 推荐形态 | 自动化方式 |
| --- | --- | --- |
| Windows | 单文件 EXE / Python CLI | Startup 后台守护 |
| macOS | Python CLI | LaunchAgent |
| Linux | Python CLI | systemd --user |
| Android | Termux CLI | Termux:Boot / Tasker |
| iOS / iPadOS | Scriptable JS | Shortcuts Wi-Fi 自动化 |
| HarmonyOS | 原生 ArkTS 小工具 | 原生网络事件 |

目录：

- [Windows](windows/)
- [macOS / Linux](macos-linux/)
- [Android](android/)
- [iOS / iPadOS](ios/)
- [HarmonyOS](harmonyos/)

设计原则：

- 不为了跨平台引入大型 GUI 框架；
- Windows 普通用户不需要 Python；
- Python 平台共用一套核心实现；
- iOS / HarmonyOS 使用各自平台更合适的安全存储与自动化能力；
- 平台能力没有真机验证前，不把推测写成已完成。
