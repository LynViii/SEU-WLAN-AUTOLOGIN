# Windows

Windows 是当前主验证平台，**已在真实东南大学 seu-wlan 环境完成自动认证验证**。

## 方案 A：单文件 EXE（推荐）

Release 下载：

~~~text
SEU-WLAN-AUTOLOGIN.exe
~~~

直接双击或 PowerShell 运行，不需要安装 Python。

第一次配置后，安装后台守护：

~~~powershell
.\SEU-WLAN-AUTOLOGIN.exe --install-startup
~~~

程序会把用于 Startup 的副本复制到：

~~~text
%LOCALAPPDATA%\SEU-WLAN-AUTOLOGIN\SEU-WLAN-AUTOLOGIN.exe
~~~

因此最初下载的 EXE 后续可以移动或删除。

移除守护：

~~~powershell
.\SEU-WLAN-AUTOLOGIN.exe --uninstall-startup
~~~

## 方案 B：Python 源码

~~~powershell
python -m pip install ".[desktop]"
seu-wlan
~~~

也可直接：

~~~powershell
python autologin.py
~~~

源码模式安装 Startup 后会记录当前 Python 和源码路径，因此移动源码目录后需要重新安装守护。

## 常用诊断

~~~powershell
.\SEU-WLAN-AUTOLOGIN.exe --diagnose
~~~

日志：

~~~powershell
Get-Content "$env:APPDATA\SEU-WLAN-AUTOLOGIN\autologin.log" -Tail 100
~~~

后台守护具备单实例保护，不会因为 Startup 与手动 --watch 同时启动而重复运行。

后台守护**只负责校园网认证，不负责 Wi-Fi 连接管理**。它不会主动断开、切换或重连 Windows Wi-Fi；只有明确检测到当前 SSID 为 `seu-wlan` 时才会检查并补认证。切换到其他 Wi-Fi、暂时未连接或 SSID 识别失败时，守护只等待。
