import codecs
import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

import autologin


class RuntimeTests(unittest.TestCase):
    def setUp(self):
        self.original_log = autologin.credentials.LOG_FILE
        self.tempdir = tempfile.TemporaryDirectory()
        autologin.credentials.LOG_FILE = Path(self.tempdir.name) / "autologin.log"

    def tearDown(self):
        autologin.credentials.LOG_FILE = self.original_log
        self.tempdir.cleanup()

    def test_log_uses_utf8_bom_for_windows_powershell(self):
        autologin._append_log("后台守护已启动。")
        data = autologin.credentials.LOG_FILE.read_bytes()

        self.assertTrue(data.startswith(codecs.BOM_UTF8))
        self.assertIn("后台守护已启动。", data.decode("utf-8-sig"))

    def test_existing_utf8_log_is_upgraded_without_losing_content(self):
        autologin.credentials.LOG_FILE.write_bytes("旧日志\n".encode("utf-8"))
        autologin._append_log("新日志")

        data = autologin.credentials.LOG_FILE.read_bytes()
        self.assertTrue(data.startswith(codecs.BOM_UTF8))
        text = data.decode("utf-8-sig")
        self.assertIn("旧日志", text)
        self.assertIn("新日志", text)

    def test_log_rotates_when_size_limit_is_reached(self):
        autologin.credentials.LOG_FILE.write_bytes(
            codecs.BOM_UTF8 + b"x" * autologin.MAX_LOG_BYTES
        )
        autologin._append_log("new")

        backup = autologin.credentials.LOG_FILE.with_suffix(".log.1")
        self.assertTrue(backup.exists())
        self.assertIn("new", autologin.credentials.LOG_FILE.read_text(encoding="utf-8-sig"))

    def test_current_windows_ssid_parses_target_without_text_mode(self):
        netsh = Mock(
            returncode=0,
            stdout=(
                b"\r\n"
                b"    Name                   : WLAN\r\n"
                b"    State                  : connected\r\n"
                b"    SSID                   : seu-wlan\r\n"
                b"    BSSID                  : 00:11:22:33:44:55\r\n"
            ),
        )
        with (
            patch.object(autologin, "is_windows", return_value=True),
            patch.object(autologin.subprocess, "run", return_value=netsh),
        ):
            self.assertEqual(autologin.current_windows_ssid(), "seu-wlan")

    def test_watch_lock_allows_only_one_instance(self):
        lock_dir = Path(self.tempdir.name) / "lock"
        with patch.object(autologin.credentials, "config_dir", return_value=lock_dir):
            first = autologin.WatchLock()
            second = autologin.WatchLock()

            self.assertTrue(first.acquire())
            self.assertFalse(second.acquire())

            first.release()
            self.assertTrue(second.acquire())
            second.release()

    def test_watch_ignores_other_wifi(self):
        lock = Mock()
        lock.acquire.return_value = True

        with (
            patch.object(autologin, "WatchLock", return_value=lock),
            patch.object(autologin, "is_windows", return_value=True),
            patch.object(autologin, "current_windows_ssid", return_value="Home-WiFi"),
            patch.object(autologin, "ensure_authenticated") as authenticate,
            patch.object(autologin.time, "sleep", side_effect=KeyboardInterrupt),
        ):
            with self.assertRaises(KeyboardInterrupt):
                autologin.watch(60, "seu-wlan", True)

        authenticate.assert_not_called()
        lock.release.assert_called_once()

    def test_watch_waits_when_ssid_is_unknown(self):
        lock = Mock()
        lock.acquire.return_value = True

        with (
            patch.object(autologin, "WatchLock", return_value=lock),
            patch.object(autologin, "is_windows", return_value=True),
            patch.object(autologin, "current_windows_ssid", return_value=None),
            patch.object(autologin, "ensure_authenticated") as authenticate,
            patch.object(autologin.time, "sleep", side_effect=KeyboardInterrupt),
        ):
            with self.assertRaises(KeyboardInterrupt):
                autologin.watch(60, "seu-wlan", True)

        authenticate.assert_not_called()
        lock.release.assert_called_once()

    def test_watch_authenticates_only_on_target_wifi(self):
        lock = Mock()
        lock.acquire.return_value = True

        with (
            patch.object(autologin, "WatchLock", return_value=lock),
            patch.object(autologin, "is_windows", return_value=True),
            patch.object(autologin, "current_windows_ssid", return_value="seu-wlan"),
            patch.object(
                autologin,
                "ensure_authenticated",
                return_value=autologin.client.Status(True, "10.0.0.8"),
            ) as authenticate,
            patch.object(autologin.time, "sleep", side_effect=KeyboardInterrupt),
        ):
            with self.assertRaises(KeyboardInterrupt):
                autologin.watch(60, "seu-wlan", True)

        authenticate.assert_called_once()
        lock.release.assert_called_once()


if __name__ == "__main__":
    unittest.main()
