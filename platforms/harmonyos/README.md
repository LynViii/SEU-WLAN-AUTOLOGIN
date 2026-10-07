# HarmonyOS

## 结论

**能做类似功能，但建议先做原生 ArkTS 小应用，而不是尝试长期常驻后台脚本。**

当前公开 HarmonyOS 能力已经足够完成核心认证逻辑：

- NetworkKit 可以直接发送 HTTP 请求；
- Connectivity Kit / 系统公共事件可以感知 Wi‑Fi / 网络连接状态变化；
- 当前连接 Wi‑Fi 信息可由 WLAN 能力获取；
- Background Tasks Kit 提供短时、长时和延迟任务机制。

因此“打开 App → 自动检查 → 登录”明确可行；“App 仍在运行时，连接 seu-wlan 后自动认证”也有明确实现路径。

真正需要谨慎的是：

> **App 完全未运行时，是否能像 iOS Shortcuts 一样在连接某个 SSID 的瞬间被第三方应用稳定唤醒。**

HarmonyOS 对后台运行和任务调度有资源限制。延迟任务虽然可以设置 Wi‑Fi 网络条件，但系统决定实际调度时机，而且重复任务存在较长的最小间隔，因此它不适合直接当作“连接 seu-wlan 立刻登录”的精确触发器。

## 推荐实现层级

### Level 1：一键登录

原生 ArkTS App，用户打开后：

```text
读取安全保存的账号密码
→ 查询校园网认证状态
→ 获取校园网 IP
→ HTTP 登录
→ 复核
```

这是第一阶段最稳的方案。

### Level 2：前台 / 活跃进程自动登录

App 活跃时订阅网络可用、Wi‑Fi 连接状态变化；一旦检测到目标网络，再执行认证。

### Level 3：真正系统级自动化

目标是：

```text
连接 seu-wlan
→ 即使 App 未打开也被系统唤醒
→ 自动认证
```

公开 API 中存在 Wi‑Fi 连接状态公共事件和开机完成事件，但第三方应用能否在实际 HarmonyOS 设备、当前 API Level、后台限制下稳定完成冷启动唤醒，需要真机 + DevEco 工程验证后才能承诺。

因此仓库当前把鸿蒙标记为 **Prototype**，不把未验证能力写成已完成。

## PoC

`LoginClient.ets` 提供认证核心的 ArkTS 参考实现，用于后续 DevEco Studio 工程。

正式 App 还需要：

- Preferences / Asset Store 保存账号；
- INTERNET 等权限配置；
- UIAbility；
- 网络/Wi‑Fi 状态订阅；
- 目标设备 API Level 兼容验证；
- 后台触发策略验证。

## 参考能力

- NetworkKit HTTP 请求
- Connectivity Kit WLAN / Wi‑Fi 信息
- Common Event：Wi‑Fi connection state
- Background Tasks Kit：短时/延迟任务
