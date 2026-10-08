# iOS / iPadOS

推荐方案：**Apple Shortcuts + Scriptable**。不需要 Python，也不需要安装自定义 App。

```text
连接 seu-wlan
→ Shortcuts Wi-Fi 自动化触发
→ Scriptable 运行单个 JS
→ 自动检查 / 登录 / 复核
```

## 安装

1. 安装 Scriptable；
2. 将 Release 中的 `SEU-WLAN-AUTOLOGIN-Scriptable.js` 导入 Scriptable，或复制本目录的脚本；
3. 在 Scriptable 中手动运行一次；
4. 输入一卡通号和密码，凭据保存到 Scriptable Keychain；
5. 在“快捷指令 → 自动化”中新建 **Wi-Fi → seu-wlan**；
6. 添加 Scriptable 的 **Run Script** 动作，选择该脚本；
7. 配置为自动运行。

之后连接 `seu-wlan` 时即可自动调用。

## 日常管理

直接在 Scriptable 中运行脚本，会显示：

- 立即认证
- 重新配置账号
- 清除凭据

Shortcuts 调用默认只执行认证，不弹管理菜单。

如果需要从其他 Shortcut 控制，也可以向 Scriptable 的 Run Script 动作传入文本参数：

```text
setup
forget
```

## 安全

账号密码保存在 Scriptable Keychain，而不是 JS 文件中。Scriptable 官方文档将 Keychain 定义为用于凭据等信息的加密安全存储。

> iOS 自动化实现已经完成，但仍需要真实 SEU 网络 + iPhone/iPad 真机验证锁屏和后台触发行为。
