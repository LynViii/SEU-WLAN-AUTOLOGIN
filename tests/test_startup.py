import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from seu_wlan import startup


class StartupTests(unittest.TestCase):
    def test_source_install_and_uninstall(self):
        with tempfile.TemporaryDirectory() as tmp:
            startup_dir = Path(tmp) / "Startup"
            entry = Path(tmp) / "repo" / "autologin.py"
            entry.parent.mkdir(parents=True)
            entry.write_text("# test\n", encoding="utf-8")

            with (
                patch.object(startup, "_startup_dir", return_value=startup_dir),
                patch.object(startup, "is_frozen", return_value=False),
            ):
                target = startup.install(entry)
                self.assertTrue(target.exists())
                content = target.read_text(encoding="utf-8")
                self.assertIn("--watch --quiet", content)
                self.assertIn(str(entry.resolve()), content)
                self.assertTrue(startup.uninstall())
                self.assertFalse(target.exists())

    def test_frozen_install_copies_exe_to_stable_location(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            startup_dir = root / "Startup"
            app_dir = root / "LocalApp" / startup.APP_DIR_NAME
            source = root / "Downloads" / startup.EXE_NAME
            source.parent.mkdir(parents=True)
            source.write_bytes(b"fake-exe")

            with (
                patch.object(startup, "_startup_dir", return_value=startup_dir),
                patch.object(startup, "_local_app_dir", return_value=app_dir),
                patch.object(startup, "is_frozen", return_value=True),
                patch.object(startup.sys, "executable", str(source)),
            ):
                target = startup.install(root / "ignored.py")
                installed = app_dir / startup.EXE_NAME

                self.assertEqual(installed.read_bytes(), b"fake-exe")
                content = target.read_text(encoding="ascii")
                self.assertIn("%LOCALAPPDATA%", content)
                self.assertIn("--watch --quiet", content)
                self.assertNotIn(str(source), content)


if __name__ == "__main__":
    unittest.main()
