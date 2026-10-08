# macOS / Linux

macOS 与 Linux 使用同一套 Python CLI。

## 安装

下载源码后：

```bash
python -m pip install ".[desktop]"
```

之后统一使用：

```bash
seu-wlan
seu-wlan --status
seu-wlan --setup
seu-wlan --watch
seu-wlan --diagnose
```

也可以不安装命令，直接：

```bash
python autologin.py
```

## 凭据

桌面端通过 Python `keyring` 调用系统凭据存储：

- macOS：通常使用 Keychain；
- Linux：依赖当前桌面环境可用的 keyring 后端。

如果系统没有可用的安全凭据后端，单次登录仍可使用，但后台自动守护不会安装成功，以避免把密码降级保存成普通明文文件。

## 自动守护

完成凭据配置后：

```bash
seu-wlan --install-startup
```

### macOS

会创建用户级 LaunchAgent：

```text
~/Library/LaunchAgents/io.github.lynviii.seu-wlan-autologin.plist
```

### Linux

会创建用户级 systemd service：

```text
~/.config/systemd/user/seu-wlan-autologin.service
```

Linux 需要当前发行版支持用户级 `systemd`。

移除：

```bash
seu-wlan --uninstall-startup
```

> 当前 macOS / Linux 方案代码与自动测试已准备好，但真实 SEU 校园网环境仍待对应平台实测。
