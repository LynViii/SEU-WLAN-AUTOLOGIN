# Changelog

## Unreleased

- 增加 Windows 单文件 EXE 构建，普通用户无需 Python。
- EXE 安装后台守护时会自复制到 %LOCALAPPDATA% 固定目录，原下载文件可移动或删除。
- 增加标准 Python 包入口和 seu-wlan 命令，统一 Windows/macOS/Linux/Android 的源码体验。
- 增加 macOS LaunchAgent 与 Linux 用户级 systemd 后台守护。
- 增加 Android Termux 一键安装/卸载脚本。
- iOS Scriptable 增加管理菜单、重新配置和清除凭据。
- 增加后台守护单实例锁和 --diagnose 诊断命令。
- 增加自动 Release 流程：Windows EXE、SHA256、Python wheel/sdist、iOS JS。
- 明确 HarmonyOS 最终采用轻量 ArkTS HAP + Asset Store 路线；在真机验证前不提交伪完整工程。

- 公开发布前恢复上游 MIT 版权声明，并在 README 明确项目来源与非官方属性。

- **2026-10-08：Windows 真实 SEU `seu-wlan` 自动认证现场验证成功。**
- Windows 密码输入改为星号掩码，可确认实际输入长度但不泄露真实字符。
- 修复 Windows PowerShell 读取 `autologin.log` 时中文乱码的问题，并兼容已有 UTF-8 日志。
- 日志超过约 512 KB 自动轮转为 `autologin.log.1`。
- `--watch` 只在 `seu-wlan` / Wi-Fi 未连接时参与恢复；连接其他 Wi-Fi 时不再误断当前网络。
- 守护日志改为状态变化时记录，减少重复日志。
- 登录时复用已取得的网关状态，减少一次重复 `chkstatus` 请求。
- JSONP 解析改为首尾花括号定位，避免贪婪正则造成不必要的脆弱性。
- 重整仓库目录：平台实现统一放入 `platforms/`，测试与架构文档统一放入 `docs/`。
- 增加 iOS / iPadOS：Shortcuts + Scriptable 自动认证方案与脚本。
- 增加 HarmonyOS：原生 ArkTS 认证核心 PoC 与能力边界说明。
- Windows Startup 安装前强制确认密码已安全持久化。

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
