# Windows

Windows 是当前主验证平台，**已在真实东南大学 `seu-wlan` 环境完成自动认证验证**。

## 首次安装

```bash
python -m pip install -r requirements/desktop.txt
python autologin.py
```

第一次运行会输入一卡通号和密码。密码输入时显示 `*`，真实字符不会回显。

一卡通号保存在用户配置目录，密码通过 `keyring` 写入 Windows Credential Manager。

## 登录系统后自动守护

```bash
python autologin.py --install-startup
```

以后登录 Windows 后后台运行：

```text
autologin.py --watch --quiet
```

守护模式只在目标 Wi-Fi 上尝试认证；如果当前连接的是其他 Wi-Fi，不会为了 `seu-wlan` 主动断开现有网络。

日志：

```powershell
Get-Content "$env:APPDATA\SEU-WLAN-AUTOLOGIN\autologin.log" -Tail 100
```

日志使用 Windows PowerShell 可正确识别的 UTF-8，并在超过约 512 KB 时轮转。

移除自动启动：

```bash
python autologin.py --uninstall-startup
```

> Startup 记录当前 Python 和仓库路径。移动仓库或更换 Python 后，应先移除再重新安装 Startup。
