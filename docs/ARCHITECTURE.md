# Architecture

核心原则：**所有平台共享同一套 SEU 认证流程，平台层只负责“何时触发”和“如何保存凭据”。**

```text
                         SEU WLAN Gateway
                         ┌───────────────┐
                         │ chkstatus      │
                         │ eportal login  │
                         └───────▲───────┘
                                 │
                    shared authentication flow
                                 │
       ┌─────────────────────────┼────────────────────────┐
       │                         │                        │
   Desktop Python            iOS Scriptable        HarmonyOS ArkTS
       │                         │                        │
Windows Startup /          Shortcuts Wi-Fi        Native event /
watch mode                 automation             app lifecycle
       │
Android Termux reuses
the Python implementation
```

认证流程固定为：

1. 查询 `chkstatus`；
2. 如果已认证，直接返回；
3. 获取当前校园网 IP；
4. 调用 ePortal 登录；
5. 再次查询状态进行复核。

不把“HTTP 返回成功”直接当作最终成功，避免假阳性。
