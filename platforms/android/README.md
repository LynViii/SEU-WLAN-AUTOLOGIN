# Android

Android 推荐使用 **Termux**。它复用同一套 Python 核心，不需要维护第二套 Android 登录协议实现。

## 最简单安装

先从 F-Droid 安装：

- Termux
- Termux:Boot（需要开机自动认证时）

公开仓库后，可以在 Termux 中直接下载安装脚本：

~~~bash
pkg update
pkg install python git curl
curl -fsSLo install-seu-wlan.sh https://raw.githubusercontent.com/LynViii/SEU-WLAN-AUTOLOGIN/main/platforms/android/install-termux.sh
bash install-seu-wlan.sh
~~~

安装脚本本身可以独立运行，会从 GitHub 安装最新 Python CLI。

如果你本来就 clone 了仓库，也可以：

~~~bash
git clone https://github.com/LynViii/SEU-WLAN-AUTOLOGIN.git
cd SEU-WLAN-AUTOLOGIN
bash platforms/android/install-termux.sh
~~~

脚本会：

1. 安装 seu-wlan CLI；
2. 用星号掩码输入一卡通号和密码；
3. 把自动化凭据写入 Termux 私有目录；
4. 创建 Termux:Boot 守护脚本。

立即测试：

~~~bash
. "$HOME/.config/seu-wlan-autologin/termux.env"
python -m seu_wlan
~~~

## 更省电：Wi-Fi 事件触发

如果使用 Tasker + Termux:Tasker，可以在连接 seu-wlan 时只执行一次：

~~~bash
. "$HOME/.config/seu-wlan-autologin/termux.env"
python -m seu_wlan --quiet
~~~

这样不需要长期运行 Python 守护循环。

## 凭据说明

Termux 没有与桌面端完全相同的通用 keyring 后端。安装脚本会把账号密码保存到：

~~~text
~/.config/seu-wlan-autologin/termux.env
~~~

文件权限设为 600，目录位于 Termux 的 Android 应用私有存储中。它仍属于**本地明文凭据**；如果你不接受这种方式，不要启用 Boot 自动化，只在需要时手动运行并输入凭据。

## 卸载

仓库方式：

~~~bash
bash platforms/android/uninstall-termux.sh
~~~

如果只下载了独立安装脚本，可手动删除 Boot 文件和私有配置，再执行：

~~~bash
python -m pip uninstall -y seu-wlan-autologin
~~~

部分 Android 厂商还需要允许 Termux / Termux:Boot 自启动，并关闭对应的电池优化限制。
