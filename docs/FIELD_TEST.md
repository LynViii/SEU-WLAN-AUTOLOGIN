# Field Test Record

## Windows / 2026-10-08

真实东南大学 `seu-wlan` 现场验证结果：

- [x] Python 环境与依赖正常
- [x] 第一次输入一卡通号和密码
- [x] 真实校园网认证成功
- [x] 再次运行可复用系统凭据
- [x] `--status` 正常
- [x] Wi-Fi 重新连接后可自动认证
- [x] Windows Startup 可安装
- [x] 自动认证成功

现场验证后继续完成：

- 密码输入改为星号掩码；
- 修复 PowerShell 日志中文乱码；
- 收紧 Watch 对非目标 Wi-Fi 的处理；
- 增加日志轮转和状态变化日志。

如后续发现校园网认证接口变化，请优先保留脱敏后的终端输出和 `autologin.log`，再调整协议兼容。
