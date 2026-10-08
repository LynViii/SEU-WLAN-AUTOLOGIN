import codecs
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

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

    def test_reconnect_never_disconnects_other_wifi(self):
        with (
            patch.object(autologin.os, "name", "nt"),
            patch.object(autologin, "current_windows_ssid", return_value="Home-WiFi"),
            patch.object(autologin.subprocess, "run") as run,
        ):
            result = autologin.reconnect_windows(
                "seu-wlan",
                quiet=True,
                to_log=False,
            )

        self.assertFalse(result)
        run.assert_not_called()


if __name__ == "__main__":
    unittest.main()
