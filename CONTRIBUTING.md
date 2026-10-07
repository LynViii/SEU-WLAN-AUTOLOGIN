# Contributing

欢迎提交 Bug、兼容性问题和改进建议。这个项目保持“小而直接”：优先解决真实的 SEU WLAN 登录与自动认证问题，不为了工程化而增加不必要的依赖。

## 本地开发

```bash
git clone https://github.com/LynViii/SEU-WLAN-AUTOLOGIN.git
cd SEU-WLAN-AUTOLOGIN
python -m pip install -r requirements-desktop.txt
```

运行检查：

```bash
python -m py_compile autologin.py seu_wlan/*.py
python -m unittest discover -s tests -v
```

## 提交问题时请提供

- 操作系统与版本；
- Python 版本；
- 是否已连接 `seu-wlan`；
- 执行的命令；
- 完整错误信息或脱敏后的终端输出；
- 问题是否可稳定复现。

**不要提交一卡通号、校园网密码、Cookie、凭据文件或任何其他敏感信息。**

## Pull Request

建议一个 PR 只解决一个明确问题。涉及认证协议变化时，请同时补充或更新测试；涉及用户行为变化时，请同步更新 README。
