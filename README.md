# SEU-WLAN-AUTOLOGIN

东南大学 `seu-wlan` 自动认证工具。第一次配置账号密码后，后续直接运行脚本即可：**已认证则退出，未认证则自动登录**。Windows 还可以安装为登录系统后自动后台守护。

## 快速开始

需要 Python 3.10+。

```bash
git clone https://github.com/LynViii/SEU-WLAN-AUTOLOGIN.git
cd SEU-WLAN-AUTOLOGIN
python -m pip install -r requirements-desktop.txt
python autologin.py
```

第一次运行时会提示：

```text
东南大学一卡通号: 213xxxxxx
校园网密码（输入时不会显示）:
正在认证……
✓ 已认证（IP: 10.x.x.x）
```

之后再次运行：

```bash
python autologin.py
```

不会再询问账号密码，而是直接检查并认证。若已经在线，会直接显示 `✓ 已认证` 并退出。

## 常用命令

```bash
python autologin.py                  # 自动判断并确保已认证
python autologin.py --status         # 只看状态
python autologin.py --setup          # 修改账号密码
python autologin.py --forget         # 删除本机保存的账号信息
python autologin.py --watch          # 持续守护，掉线后自动补登
```

### Windows 开机后自动认证

首次先手动运行一次 `python autologin.py` 完成凭据配置，然后执行：

```bash
python autologin.py --install-startup
```

它会在当前 Windows 用户的 Startup 目录创建启动项。以后每次**登录 Windows 后**，后台自动运行：

```text
autologin.py --watch --quiet
```

连接到 `seu-wlan` 后会自动检查并认证；掉线后也会尝试重新认证。移除：

```bash
python autologin.py --uninstall-startup
```

> 启动项记录的是当前 Python 和仓库路径。如果以后移动仓库或更换 Python，重新执行一次 `--install-startup` 即可。

## 账号密码

桌面端安装 `requirements-desktop.txt` 后：

- 一卡通号保存在本机用户配置目录；
- 密码通过 `keyring` 保存到操作系统凭据存储；
- 密码不会写进仓库，也不会出现在日志里；
- `--setup` 可以随时重新配置。

还支持环境变量 `SEU_WLAN_USERNAME` / `SEU_WLAN_PASSWORD`，主要用于 Termux 等自动化环境。

## 自动守护

`--watch` 默认每 60 秒检查一次 SEU 认证状态：

- 已认证：保持不动；
- 未认证：直接使用保存的凭据补登；
- Windows 下连续无法访问认证网关：尝试重新连接已保存的 `seu-wlan` Wi-Fi 配置；
- 凭据错误：只报告错误，不反复断开 Wi-Fi。

守护模式日志保存在用户配置目录的 `autologin.log`，不会记录密码。

## Android

Android 推荐 **Termux + Termux:Boot**，可在开机后运行同一套 Python 认证逻辑。完整步骤见 [`docs/android.md`](docs/android.md)。

## 项目结构

```text
SEU-WLAN-AUTOLOGIN/
├── autologin.py              # 唯一主入口
├── seu_wlan/
│   ├── client.py             # SEU 网关状态与认证
│   ├── credentials.py        # 本机凭据
│   └── startup.py            # Windows 自动启动
├── docs/
│   └── android.md
├── tests/
├── requirements.txt
└── requirements-desktop.txt
```

## 说明

认证请求直接发送给东南大学校园网门户。项目不会绕过账号权限，也不会尝试获取任何非本人授权的网络访问。校园网认证接口未来如果调整，可能需要同步更新请求参数。

## License

MIT License.
