# Changelog

## Unreleased

- 重整仓库目录：平台实现统一放入 `platforms/`，测试与架构文档统一放入 `docs/`。
- 增加 iOS / iPadOS：Shortcuts + Scriptable 自动认证方案与脚本。
- 增加 HarmonyOS：原生 ArkTS 认证核心 PoC 与能力边界说明。
- 增加 Windows / Android 独立平台文档。
- Windows Startup 安装前强制确认密码已安全持久化。
- 增加真实校园网测试清单。
- 等待 SEU 校园网真实环境验证。

## 0.1.0 - 2026-10-07

- 完成独立的 SEU WLAN 自动认证实现。
- 统一桌面入口为 `autologin.py`。
- 首次运行交互式保存账号密码，后续自动认证。
- 桌面端密码通过系统凭据存储保存。
- 支持状态检查、重新配置和清除凭据。
- 支持持续守护与掉线自动补登。
- 支持 Windows 登录系统后自动启动守护。
- 增加 Android Termux 自动认证方案。
- 增加 GitHub Actions，对 Python 3.10、3.12、3.13 执行编译和单元测试。
