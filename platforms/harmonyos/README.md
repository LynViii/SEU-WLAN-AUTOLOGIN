# HarmonyOS

## 定位

HarmonyOS 走**原生 ArkTS 极简小工具**路线，不引入 Python，也不做长期常驻脚本。

目标最终形态：

~~~text
一个 HAP
→ 第一次输入账号密码
→ Asset Store 安全保存
→ 打开 App 即自动认证
→ App 活跃时可监听网络变化自动补登
~~~

当前仓库的 LoginClient.ets 已实现 SEU 状态查询、ePortal 登录和登录后复核的认证核心。

## 为什么使用 Asset Store

HarmonyOS 官方 Asset Store Kit 明确面向密码、Token 等短敏感数据的安全存储，因此正式 App 不应把校园网密码写进 Preferences 或普通文件。

## 自动化能力

### 已有明确实现路径

- 打开 App 后自动认证；
- App 活跃时监听网络 / Wi-Fi 状态变化；
- 连接目标网络后触发认证；
- 使用 Asset Store 保存密码。

### 仍需真机验证

~~~text
App 完全未运行
→ 连接 seu-wlan
→ 系统自动冷启动第三方 App
→ 立刻认证
~~~

HarmonyOS 有 Wi-Fi 连接状态公共事件和后台任务能力，但系统对后台唤醒与调度有限制，因此在真机验证前不承诺与 iOS Shortcuts 完全相同的冷启动行为。

## 当前文件

~~~text
LoginClient.ets
~~~

它是认证核心 PoC，不是可直接安装的 HAP。

下一阶段只在有 HarmonyOS 真机 / DevEco Studio 验证条件时补完整 UIAbility、Asset Store 和打包工程，避免仓库里出现一套“看似完整但未编译验证”的假工程。
