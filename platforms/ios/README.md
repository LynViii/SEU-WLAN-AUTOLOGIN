# iOS / iPadOS

推荐方案：**Apple Shortcuts + Scriptable**。

Apple Shortcuts 支持“连接指定 Wi‑Fi”作为个人自动化触发器，并允许 Wi‑Fi 自动化在配置后无需再次确认运行。Scriptable 可以从 Shortcuts 执行 JavaScript，并提供 Keychain 和 HTTP Request API，因此可以实现：

```text
连接 seu-wlan
→ Shortcuts 自动触发
→ 运行 Scriptable 脚本
→ 检查 SEU 网关状态
→ 未认证则登录
→ 返回认证结果
```

## 1. 安装脚本

安装 Scriptable，把本目录中的：

```text
scriptable/seu-wlan-autologin.js
```

复制到 Scriptable，新建脚本并命名为：

```text
SEU WLAN AutoLogin
```

第一次请在 Scriptable App 内**手动运行一次**。脚本会提示输入一卡通号和密码，并写入 Scriptable Keychain。

## 2. 建立快捷指令自动化

在“快捷指令 → 自动化”中新建：

1. 触发器选择 **Wi‑Fi**；
2. 网络选择 **seu-wlan**；
3. 添加 Scriptable 的 **Run Script** 动作；
4. 脚本选择 **SEU WLAN AutoLogin**；
5. 开启自动运行 / 关闭运行前询问（具体文案随 iOS 版本变化）；
6. 第一次运行时允许所需网络和自动化权限。

Apple 官方文档说明，Wi‑Fi 可以作为指定网络连接触发器，并属于可以自动运行的个人自动化类型。

## 3. 注意事项

- Scriptable Keychain 用来保存账号密码，不需要把密码写进快捷指令；
- 自动化本身可配置为无需确认，但第三方 App 动作在锁屏、首次授权等场景下仍可能受系统限制，因此需要真机验证；
- 校园网认证接口或证书如果变化，脚本也需要同步适配；
- 不要把填有真实账号密码的脚本导出或上传。

## 官方/项目文档

- Apple Shortcuts：Wi‑Fi 自动化触发器
- Apple Shortcuts：允许个人自动化自动运行
- Scriptable：Siri Shortcuts integration
- Scriptable：Keychain / Request API
