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

v1.0 正式发布前曾发现一个 Windows 守护逻辑问题：在 Wi-Fi 切换过程中，SSID 暂时识别失败时，旧逻辑可能把认证网关不可达误判为 `seu-wlan` 掉线，并尝试重连 Wi-Fi。

当前实现已经移除守护进程的 Wi-Fi 控制能力：

- 当前 SSID 是 `seu-wlan`：只检查并补认证；
- 当前是其他 Wi-Fi：等待，不修改网络；
- 当前未连接：等待，不修改网络；
- SSID 暂时无法识别：等待，不修改网络。

因此后台守护不再调用 `netsh wlan disconnect` 或 `netsh wlan connect`。

如果本机仍出现自动切网，说明正在运行旧版本守护进程。停止旧守护、更新程序后重新安装 Startup。

## 学校认证接口变化

如果浏览器还能正常登录，而工具突然失败，请提交 Issue，并附：

- 平台和版本；
- 工具版本；
- seu-wlan --diagnose 输出；
- 脱敏后的日志。

不要上传完整登录 URL、密码或抓包中的 user_password。
