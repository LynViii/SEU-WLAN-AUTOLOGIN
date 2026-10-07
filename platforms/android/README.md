# Android

推荐两种方式：**Termux + Termux:Boot**，或 **Tasker + Termux:Tasker**。

## A. 开机后持续守护

安装 Termux 与 Termux:Boot 后，在 Termux 中：

```bash
pkg update
pkg install python git
git clone https://github.com/LynViii/SEU-WLAN-AUTOLOGIN.git
cd SEU-WLAN-AUTOLOGIN
python -m pip install -r requirements/base.txt
```

创建：

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

部分 Android 厂商需要允许 Termux / Termux:Boot 自启动并关闭对应的电池优化限制。

## B. 连接 seu-wlan 时触发

更省电的长期方案是使用 Tasker + Termux:Tasker，在连接 `seu-wlan` 时执行一次：

```bash
cd "$HOME/SEU-WLAN-AUTOLOGIN"
SEU_WLAN_USERNAME='一卡通号' SEU_WLAN_PASSWORD='密码' python autologin.py --quiet
```

这种方式不需要常驻 Python 循环。

## 说明

Android/Termux 不使用桌面端 keyring 方案。自动化凭据应只放在 Termux 私有目录，不要同步到 Git。
