# Android 自动认证

推荐方案：**Termux + Termux:Boot**。它可以复用本仓库同一套认证核心，不需要单独维护 Android APK。

## 一次性准备

1. 从 F-Droid 安装 Termux 与 Termux:Boot，并各打开一次。
2. 在 Termux 中执行：

```bash
pkg update
pkg install python git
git clone https://github.com/LynViii/SEU-WLAN-AUTOLOGIN.git
cd SEU-WLAN-AUTOLOGIN
python -m pip install -r requirements.txt
```

Android/Termux 通常没有桌面系统那样稳定的 keyring 后端，因此自动启动时推荐通过 Termux 私有脚本设置环境变量。该脚本位于应用私有目录，不要同步或提交到 Git。

```bash
mkdir -p ~/.termux/boot
nano ~/.termux/boot/seu-wlan-autologin
```

内容：

```sh
#!/data/data/com.termux/files/usr/bin/sh
export SEU_WLAN_USERNAME='你的一卡通号'
export SEU_WLAN_PASSWORD='你的校园网密码'
cd "$HOME/SEU-WLAN-AUTOLOGIN"
python autologin.py --watch --quiet
```

然后：

```bash
chmod 700 ~/.termux/boot/seu-wlan-autologin
```

以后 Android 启动后，Termux:Boot 会运行这个脚本。`--watch` 会等待/检查校园网网关；连接到 `seu-wlan` 后即可自动补登。

> 不同 Android 厂商的后台限制差异很大。若系统会杀后台任务，需要允许 Termux / Termux:Boot 自启动，并关闭对应的电池优化限制。

## 更轻量的一键方案

如果不要求“开机后台自动”，可以使用 Android 的 HTTP Shortcuts 一类应用直接构造校园网请求。但完整自动认证需要先读取当前校园网 IP、判断登录状态再发登录请求，因此 Termux 方案更容易复用和维护。
