# Field Test Checklist

明天真实连接 `seu-wlan` 时，按以下顺序测试。不要一开始就安装开机自启动。

## A. 环境

记录但不要上传敏感信息：

- 操作系统版本；
- Python 版本：`python --version`；
- 当前连接 Wi‑Fi：`seu-wlan`；
- 浏览器不要提前完成校园网认证。

## B. 首次登录

```bash
python -m pip install -r requirements/desktop.txt
python autologin.py
```

预期：

1. 提示输入一卡通号；
2. 提示输入密码，输入不回显；
3. 输出“正在认证……”；
4. 最终输出 `✓ 已认证（IP: ...）`。

如果失败，完整保留**脱敏后的终端输出**。

## C. 凭据复用

认证成功后再次：

```bash
python autologin.py
```

预期：不再询问账号密码，直接显示已认证。

然后：

```bash
python autologin.py --status
```

预期：显示已认证。

## D. 重新连接

1. 断开 `seu-wlan`；
2. 等待几秒；
3. 再次连接；
4. 不打开浏览器；
5. 运行 `python autologin.py`。

预期：直接使用保存的凭据重新认证。

## E. 守护模式

```bash
python autologin.py --watch
```

保持终端打开，主动制造一次断开 / 重新连接，观察是否能恢复。

## F. Windows Startup

只有 A-E 都通过后再执行：

```bash
python autologin.py --install-startup
```

随后重启电脑并验证：

```text
登录 Windows
→ 自动连接 seu-wlan
→ 不打开浏览器
→ 等待最多约 1 分钟
→ 检查能否直接联网
```

如需查看守护日志，请检查用户配置目录中的 `autologin.log`。

## G. 错误场景（可选）

在确认正常路径稳定后再做：

- `--setup` 测试修改凭据；
- 临时输入错误密码，确认不会反复断开 Wi‑Fi；
- `--forget` 后确认再次运行会重新要求配置。

## 回传给我

只需要告诉我：

- 哪一步成功 / 失败；
- 脱敏后的终端输出；
- 如果失败，是否浏览器手动登录仍然正常。

**不要发真实一卡通号和密码。**
