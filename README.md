# SEU-WLAN-AUTOLOGIN

东南大学 `seu-wlan` 命令行登录与掉线自动重连工具。无需打开校园网认证网页；脚本直接调用 SEU 的 Dr.COM / ePortal 认证接口。

> 本项目仅用于本人或获授权的校园网账号。请勿把一卡通密码写进代码、提交到 Git，或提供给他人。

## 功能

- `python login.py`：检查状态并在需要时完成认证
- 首次运行交互式输入一卡通号和密码
- 密码输入不回显，并优先保存在系统凭据管理器，而不是项目文件
- `python login.py --status`：只查看当前认证状态
- `python login.py --setup`：重新设置账号和密码
- `python login.py --forget`：删除本机保存的账号信息
- `python auto_reconnect.py`：定时检查认证状态，掉线后自动重新认证
- Windows 下连续无法访问认证网关时，可自动重连已保存的 `seu-wlan` Wi-Fi 配置
- 网络请求带超时、有限重试和明确错误信息

## 安装

需要 Python 3.10+。

```bash
git clone https://github.com/LynViii/SEU-WLAN-AUTOLOGIN.git
cd SEU-WLAN-AUTOLOGIN
python -m pip install -r requirements.txt
```

连接 Wi-Fi `seu-wlan` 后运行：

```bash
python login.py
```

首次运行会提示：

```text
首次运行，需要先配置校园网账号。
东南大学一卡通号: 213xxxxxx
校园网密码（输入时不会显示）:
✓ 账号已保存，密码已写入系统凭据管理器。
○ 已连接校园网，但尚未认证（IP: 10.x.x.x）
正在认证……
✓ 已通过 seu-wlan 校园网认证（IP: 10.x.x.x）
```

其中密码输入时终端不会显示字符，这是正常现象。

## 常用命令

```bash
python login.py
python login.py --status
python login.py --setup
python login.py --forget
python auto_reconnect.py
python auto_reconnect.py --profile "seu-wlan"
python auto_reconnect.py --interval 30
```

## 账号密码保存在哪里？

脚本不会在仓库中生成包含明文密码的 `config.json`。

- 一卡通号：保存在用户配置目录下的 `config.json` 中
- 密码：通过 [`keyring`](https://pypi.org/project/keyring/) 写入操作系统提供的凭据存储

Windows 通常使用 Windows Credential Manager；macOS 通常使用 Keychain。若当前系统没有可用的 keyring 后端，脚本不会把密码降级保存为明文，而是下次运行时再次询问密码。

## 工作原理

1. 请求 `https://w.seu.edu.cn/drcom/chkstatus` 获取当前认证状态和校园网 IP。
2. 如果已经认证，直接退出。
3. 如果未认证，向 `https://w.seu.edu.cn:801/eportal/` 发送登录请求。
4. 登录参数使用校园网当前要求的 `user_account=,0,<一卡通号>`、`user_password` 和 `wlan_user_ip`。
5. 解析 Dr.COM 返回的 JSONP 数据并输出结果。

脚本使用 `requests` 的 `params` 参数构造请求，避免手工拼接 URL 时密码中的特殊字符造成编码问题。

## 自动重连说明

`auto_reconnect.py` 不再通过 `ping baidu.com` 判断校园网是否正常，而是直接检查 SEU 认证网关：

- 网关可访问且已认证：保持不动
- 网关可访问但未认证：自动重新认证
- 网关连续无法访问：Windows 下尝试通过 `netsh wlan` 重连指定 Wi-Fi 配置
- 账号密码错误：只报告认证失败，不反复断开 Wi-Fi

## 安全说明

- 不要把密码写到 README、源码或 GitHub Issues 中。
- `.gitignore` 已忽略旧版脚本常见的 `config.json` / `credentials.json`。
- 认证接口本身采用 GET 请求，因此校园网网关协议会把密码作为请求参数发送；脚本不会主动打印、记录或持久化该请求 URL。
- 项目无法在 GitHub Actions 中进行真实校园网登录测试，因此 CI 只做语法检查与模拟网关响应的单元测试。

## 来源与许可

认证流程参考并改进自 [NN708/seu-wlan-login](https://github.com/NN708/seu-wlan-login)。原项目采用 MIT License；本仓库继续保留原作者版权声明，并同样采用 MIT License。
