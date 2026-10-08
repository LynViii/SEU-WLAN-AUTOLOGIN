# Architecture

核心原则：**各平台遵循同一套 SEU 认证协议行为，但使用适合各自系统的轻量入口、凭据存储和自动化方式。**

```text
                         SEU WLAN Gateway
                  ┌─────────────────────────┐
                  │ chkstatus               │
                  │ ePortal login           │
                  └────────────▲────────────┘
                               │
                    common protocol behavior
                               │
          ┌────────────────────┼───────────────────┐
          │                    │                   │
      Python core         iOS Scriptable      HarmonyOS ArkTS
          │                    │                   │
 Windows / macOS /        Shortcuts Wi-Fi      Native UI /
 Linux / Android          automation            network events
```

## 认证流程

1. 查询 `chkstatus`；
2. 已认证则直接返回；
3. 未认证则获取当前校园网 IP；
4. 调用 ePortal 登录；
5. 再次查询 `chkstatus`；
6. 只有状态复核成功才返回成功。

这样不会把“登录接口返回成功”直接当作最终成功。

## Python 核心

```text
autologin.py
└── seu_wlan/
    ├── client.py       # SEU 网关协议
    ├── credentials.py  # 凭据读取与安全存储
    └── startup.py      # Windows/macOS/Linux 后台守护安装
```

Windows EXE 只是把这套 Python 核心打包成单文件；Android Termux 直接复用同一套 Python 实现。

## 移动平台

iOS 和 HarmonyOS 不嵌入 Python runtime，而是按相同协议流程分别用 JavaScript / ArkTS 实现，从而保持安装体积和依赖最小。

## 数据边界

项目本地只需要：

- 一卡通号；
- 校园网密码；
- 自动守护所需的本地配置与日志。

项目不包含遥测，也不需要远程服务或自建服务器。
