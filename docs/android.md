# Android 自动认证

推荐先用 **Termux + Termux:Boot** 复用本仓库同一套认证核心，不需要维护单独 APK。Termux:Boot 会执行放在 `~/.termux/boot/` 中的脚本。

## 方案 A：开机后持续守护

1. 从 F-Droid 安装 Termux 与 Termux:Boot，并各打开一次。
2. 在 Termux 中执行：

```bash
pkg update
pkg install python git
git clone https://github.com/LynViii/SEU-WLAN-AUTOLOGIN.git
cd SEU-WLAN-AUTOLOGIN
python -m pip install -r requirements.txt
```

Android/Termux 通常没有桌面系统那样稳定的 keyring 后端，因此自动启动时通过 Termux 私有脚本提供环境变量。该脚本位于应用私有目录，不要同步或提交到 Git。

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

Android 启动后，Termux:Boot 会启动守护；连接到 `seu-wlan` 后脚本会自动补登。部分厂商系统需要允许 Termux / Termux:Boot 自启动并关闭电池优化。

如果后台仍被系统休眠，可以在启动脚本前增加 `termux-wake-lock`，但这会增加耗电。

## 方案 B：连接 seu-wlan 时才触发（更省电）

更推荐长期使用事件触发：利用 Tasker + Termux:Tasker（或其他支持 Wi-Fi 连接事件的自动化工具），在连接到 `seu-wlan` 时执行一次：

```bash
cd "$HOME/SEU-WLAN-AUTOLOGIN"
SEU_WLAN_USERNAME='一卡通号' SEU_WLAN_PASSWORD='密码' python autologin.py --quiet
```

这种方式不需要每分钟保持一个后台 Python 循环，手机上更省电。

## 轻量一键方案

HTTP Shortcuts 也可以做桌面快捷方式/快捷设置按钮来发送 HTTP 请求，并支持 JavaScript 与 Tasker 等集成。它适合“一键认证”；但要完整实现“先读当前 IP → 判断状态 → 登录 → 复核”时，Termux 直接复用本仓库代码更容易维护。
