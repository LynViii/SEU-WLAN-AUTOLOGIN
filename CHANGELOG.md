# Changelog

## Unreleased

### Added

- Windows 单文件 EXE 构建与 SHA256 校验；
- 标准 Python 包入口与 `seu-wlan` CLI；
- macOS LaunchAgent、Linux 用户级 systemd 后台守护；
- Android Termux 安装 / 卸载脚本；
- iOS Scriptable 管理菜单、Shortcuts 自动化入口；
- HarmonyOS ArkTS 认证核心；
- `--diagnose` 脱敏诊断命令；
- 后台守护单实例锁；
- 自动 Release：EXE、wheel、sdist、iOS JS、Android helper scripts。

### Changed

- Windows EXE 安装守护时自复制到 `%LOCALAPPDATA%` 固定目录；
- 密码输入使用星号掩码；
- Windows 日志改为 PowerShell 兼容 UTF-8，并增加轮转；
- Windows 守护模式彻底取消 Wi-Fi 断开/重连控制：仅在明确检测到 `seu-wlan` 时执行认证，其他 Wi-Fi、未连接或 SSID 识别失败时均只等待；
- 守护日志只记录状态变化；
- 登录流程复用首次状态查询，减少重复网关请求；
- JSONP 解析改为更稳健的首尾花括号定位；
- 依赖和 Python 包配置统一到 `pyproject.toml`；
- 仓库按 core / platforms / packaging / docs / tests 分层整理。

### Security

- 桌面端密码优先使用系统凭据存储；
- iOS 使用 Scriptable Keychain；
- Android 自动化凭据限制在 Termux 应用私有目录并明确本地明文属性；
- README / Security Policy 明确 ePortal GET 查询参数可能包含密码；
- 恢复并保留上游 MIT 版权声明。

### Validation

- 2026-10-08：Windows 在真实 SEU `seu-wlan` 环境完成认证、凭据复用、重连和 Startup 自动认证验证；
- CI 覆盖 Python 3.10 / 3.12 / 3.13、wheel/sdist、Android shell、iOS JS 和 Windows EXE。

## 0.1.0 - 2026-10-07

- 建立 SEU WLAN Python 自动认证核心；
- 支持状态查询、凭据保存、掉线补登与基础 CI。
