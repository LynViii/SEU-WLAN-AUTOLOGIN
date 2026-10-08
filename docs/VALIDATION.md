# Validation

这里记录已经完成的真实环境验证，和自动测试分开保存。

## Windows / 2026-10-08

真实东南大学 `seu-wlan` 环境已验证：

- [x] 首次输入一卡通号和密码；
- [x] 校园网认证成功；
- [x] 再次运行可复用系统凭据；
- [x] `--status` 状态查询正常；
- [x] Wi-Fi 重新连接后可再次自动认证；
- [x] Windows Startup 可安装；
- [x] 后台自动认证成功。

现场验证后继续完成并由 CI 覆盖：

- 密码输入星号掩码；
- PowerShell UTF-8 日志兼容；
- 日志轮转；
- 非目标 Wi-Fi 不误断；
- 后台守护单实例；
- Windows 单文件 EXE 构建与启动 smoke test。

## 自动化验证

GitHub Actions 当前覆盖：

- Python 3.10 / 3.12 / 3.13；
- Python 编译与单元测试；
- 标准 Python 包安装；
- `seu-wlan` 与 `python -m seu_wlan` CLI；
- wheel / sdist 构建；
- Android shell 脚本语法；
- iOS Scriptable JavaScript 语法；
- Windows PyInstaller 单文件 EXE；
- EXE `--version` / `--help` smoke test；
- SHA256 生成。

如果后续学校认证接口发生变化，请优先保留脱敏后的 `--diagnose` 输出和日志，再调整兼容。
