# Installation Guide

## Windows

### 普通用户

Release 下载一个：

~~~text
SEU-WLAN-AUTOLOGIN.exe
~~~

直接运行。

需要后台自动认证：

~~~powershell
.\SEU-WLAN-AUTOLOGIN.exe --install-startup
~~~

安装后后台副本位于：

~~~text
%LOCALAPPDATA%\SEU-WLAN-AUTOLOGIN\SEU-WLAN-AUTOLOGIN.exe
~~~

所以原下载 EXE 可以移动或删除。

### 源码用户

~~~powershell
python -m pip install ".[desktop]"
seu-wlan
~~~

## macOS / Linux

下载源码：

~~~bash
python -m pip install ".[desktop]"
seu-wlan
~~~

后台守护：

~~~bash
seu-wlan --install-startup
~~~

macOS 使用 LaunchAgent；Linux 使用用户级 systemd。

## Android

Termux 中：

~~~bash
pkg update
pkg install python git
git clone https://github.com/LynViii/SEU-WLAN-AUTOLOGIN.git
cd SEU-WLAN-AUTOLOGIN
bash platforms/android/install-termux.sh
~~~

需要更省电时，用 Tasker 在连接 seu-wlan 后执行一次登录，而不是常驻守护。

## iOS / iPadOS

1. 安装 Scriptable；
2. 导入 Release 的 SEU-WLAN-AUTOLOGIN-Scriptable.js；
3. 手动运行一次保存凭据；
4. Shortcuts 创建 Wi-Fi → seu-wlan 自动化；
5. 运行 Scriptable 脚本。

## HarmonyOS

当前还没有正式 HAP Release。仓库提供 ArkTS 登录核心，待真机验证后补原生极简 App。
