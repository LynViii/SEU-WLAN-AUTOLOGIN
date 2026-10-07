# Windows

Windows 是当前桌面端自动化程度最高的目标平台。

## 首次安装

```bash
python -m pip install -r requirements/desktop.txt
python autologin.py
```

第一次运行会保存一卡通号，并通过 `keyring` 使用 Windows Credential Manager 保存密码。

## 登录系统后自动守护

```bash
python autologin.py --install-startup
```

以后登录 Windows 后会后台运行：

```text
autologin.py --watch --quiet
```

移除：

```bash
python autologin.py --uninstall-startup
```

启动项记录当前 Python 和仓库路径，移动仓库或更换 Python 后需要重新安装启动项。
