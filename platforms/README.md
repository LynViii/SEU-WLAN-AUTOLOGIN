# Platform Support

SEU-WLAN-AUTOLOGIN 尽量让每个平台都使用最轻的原生入口，而认证流程保持一致。

| 平台 | 推荐形态 | 自动化方式 | 当前状态 |
| --- | --- | --- | --- |
| Windows | 单文件 EXE / Python 源码 | Startup 后台守护 | **真实 SEU WLAN 已验证** |
| macOS | Python CLI | LaunchAgent | 代码完成，待实测 |
| Linux | Python CLI | systemd --user | 代码完成，待实测 |
| Android | Termux CLI | Termux:Boot / Tasker | 安装脚本完成，待真机实测 |
| iOS / iPadOS | 单文件 Scriptable JS | Shortcuts Wi-Fi 自动化 | 脚本完成，待真机实测 |
| HarmonyOS | 原生 ArkTS 小工具 | 前台/网络事件；冷启动待验证 | Prototype |

设计原则：

- 不为了跨平台引入大型 GUI 框架；
- Windows 普通用户不需要 Python；
- Python 平台共用一套核心实现；
- iOS / HarmonyOS 使用各自平台原生安全存储；
- 每个平台未实测的能力都明确标注，不把 PoC 写成已完成。
