#!/data/data/com.termux/files/usr/bin/bash
set -euo pipefail

rm -f "$HOME/.termux/boot/seu-wlan-autologin"
rm -f "$HOME/.config/seu-wlan-autologin/termux.env"
rmdir "$HOME/.config/seu-wlan-autologin" 2>/dev/null || true
python -m pip uninstall -y seu-wlan-autologin || true

echo "SEU-WLAN-AUTOLOGIN 的 Termux 自动化已移除。"
