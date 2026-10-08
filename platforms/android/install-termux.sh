#!/data/data/com.termux/files/usr/bin/bash
set -euo pipefail

if [ ! -f "pyproject.toml" ]; then
  echo "请在 SEU-WLAN-AUTOLOGIN 仓库根目录运行此脚本。"
  exit 1
fi

echo "[1/4] 安装 Python CLI..."
python -m pip install --upgrade .

CONFIG_DIR="$HOME/.config/seu-wlan-autologin"
ENV_FILE="$CONFIG_DIR/termux.env"
BOOT_DIR="$HOME/.termux/boot"
BOOT_FILE="$BOOT_DIR/seu-wlan-autologin"

mkdir -p "$CONFIG_DIR" "$BOOT_DIR"
chmod 700 "$CONFIG_DIR" "$BOOT_DIR"

echo
read -r -p "东南大学一卡通号: " USERNAME
read -r -s -p "校园网密码（输入不会显示）: " PASSWORD
echo

if [ -z "$USERNAME" ] || [ -z "$PASSWORD" ]; then
  echo "账号和密码不能为空。"
  exit 1
fi

USERNAME_Q=$(python -c 'import shlex,sys; print(shlex.quote(sys.argv[1]))' "$USERNAME")
PASSWORD_Q=$(python -c 'import shlex,sys; print(shlex.quote(sys.argv[1]))' "$PASSWORD")

cat > "$ENV_FILE" <<EOF
export SEU_WLAN_USERNAME=$USERNAME_Q
export SEU_WLAN_PASSWORD=$PASSWORD_Q
EOF
chmod 600 "$ENV_FILE"

cat > "$BOOT_FILE" <<'EOF'
#!/data/data/com.termux/files/usr/bin/sh
. "$HOME/.config/seu-wlan-autologin/termux.env"
exec python -m seu_wlan --watch --quiet
EOF
chmod 700 "$BOOT_FILE"

echo "[2/4] 已保存 Termux 私有配置：$ENV_FILE"
echo "[3/4] 已创建 Termux:Boot 脚本：$BOOT_FILE"
echo "[4/4] 安装完成。"
echo
echo "现在可执行："
echo "  . "$ENV_FILE""
echo "  python -m seu_wlan"
echo
echo "若已安装 Termux:Boot，并在 Android 中允许后台运行，下次开机后会自动守护。"
