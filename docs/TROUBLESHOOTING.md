# Troubleshooting

## Windows 提示“未知发布者”或 SmartScreen

当前开源 EXE 没有商业代码签名证书，因此 Windows 可能显示“未知发布者”或 SmartScreen 提示。

建议：

1. 只从本仓库的 GitHub Release 下载；
2. 使用同一 Release 的 SHA256SUMS.txt 校验；
3. 哈希不一致时不要运行。

这不影响 Python 源码方式。

## EXE 被杀毒软件误报

PyInstaller 单文件程序偶尔可能触发启发式误报。遇到这种情况：

- 不要直接关闭杀毒软件；
- 先核对 Release SHA256；
- 可以改用源码方式；
- 如确认是误报，再向安全软件厂商提交误报样本。

## 显示“无法访问 SEU 校园网认证网关”

先确认设备当前连接的是：

~~~text
seu-wlan
~~~

不要先用浏览器完成认证，再测试脚本。

## 查看诊断

~~~bash
seu-wlan --diagnose
~~~

Windows EXE：

~~~powershell
.\SEU-WLAN-AUTOLOGIN.exe --diagnose
~~~

诊断不会输出校园网密码。

## Windows 查看日志

~~~powershell
Get-Content "$env:APPDATA\SEU-WLAN-AUTOLOGIN\autologin.log" -Tail 100
~~~

## 源码模式无法保存密码

安装桌面依赖：

~~~bash
python -m pip install ".[desktop]"
~~~

Linux 还需要桌面环境提供可用的 keyring 后端。若系统没有安全凭据后端，程序不会自动降级为普通明文密码文件。

## 移动源码后 Startup 失效

源码模式的后台守护记录当前 Python 与源码路径。移动源码目录后：

~~~bash
seu-wlan --uninstall-startup
seu-wlan --install-startup
~~~

Windows EXE 模式没有这个问题，因为安装守护时会复制到固定 LocalAppData 目录。

## 切换到其他 Wi-Fi 后网络被断开

v1.0 正式发布前曾存在一个 Windows 守护逻辑问题：SSID 暂时识别失败时可能误把“当前不是 seu-wlan”当成校园网掉线，并尝试重连 seu-wlan。

修复后的守护模式不会再控制 Wi-Fi 连接：

- 当前是 seu-wlan：只执行认证检查；
- 当前是其他 Wi-Fi：等待，不做任何网络操作；
- 当前未连接或 SSID 暂时识别不到：等待，不做任何网络操作。

如果本机仍出现自动切网，先确认运行的是最新版本，并重新安装后台守护。

## 学校认证接口变化

如果浏览器还能正常登录，而工具突然失败，请提交 Issue，并附：

- 平台和版本；
- 工具版本；
- seu-wlan --diagnose 输出；
- 脱敏后的日志。

不要上传完整登录 URL、密码或抓包中的 user_password。
