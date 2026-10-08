# Installation

先选择平台。普通用户只需要看自己对应的一段。

## Windows

### EXE（推荐）

从 GitHub Release 下载：

```text
SEU-WLAN-AUTOLOGIN.exe
```

直接运行即可，不需要 Python。

安装后台自动认证：

```powershell
.\SEU-WLAN-AUTOLOGIN.exe --install-startup
```

后台副本会安装到：

```text
%LOCALAPPDATA%\SEU-WLAN-AUTOLOGIN\SEU-WLAN-AUTOLOGIN.exe
```

之后最初下载的 EXE 可以移动或删除。

### Python / 源码

```powershell
git clone https://github.com/LynViii/SEU-WLAN-AUTOLOGIN.git
cd SEU-WLAN-AUTOLOGIN
python -m pip install -e ".[desktop]"
seu-wlan
```

## macOS / Linux

```bash
git clone https://github.com/LynViii/SEU-WLAN-AUTOLOGIN.git
cd SEU-WLAN-AUTOLOGIN
python -m pip install -e ".[desktop]"
seu-wlan
```

后台守护：

```bash
seu-wlan --install-startup
```

macOS 使用用户级 LaunchAgent；Linux 使用用户级 systemd。

## Android

先安装 Termux；需要开机自动认证时再安装 Termux:Boot。

公开仓库后可直接：

```bash
pkg update
pkg install python git curl
curl -fsSLo install-seu-wlan.sh https://raw.githubusercontent.com/LynViii/SEU-WLAN-AUTOLOGIN/main/platforms/android/install-termux.sh
bash install-seu-wlan.sh
```

也可以 clone 仓库后运行 `platforms/android/install-termux.sh`。

## iOS / iPadOS

1. 安装 Scriptable；
2. 从 Release 获取 `SEU-WLAN-AUTOLOGIN-Scriptable.js`；
3. 导入 Scriptable 并手动运行一次保存凭据；
4. Shortcuts 创建 `Wi-Fi → seu-wlan` 自动化；
5. 动作选择 Scriptable 的 Run Script。

## HarmonyOS

当前仓库提供 ArkTS 认证核心；完整 HAP 在真机和 DevEco Studio 验证后再发布，避免提供未经编译验证的安装包。
