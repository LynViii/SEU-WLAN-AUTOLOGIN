import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from seu_wlan import startup


class StartupTests(unittest.TestCase):
    def test_install_and_uninstall(self):
        with tempfile.TemporaryDirectory() as tmp:
            startup_dir = Path(tmp) / "Startup"
            entry = Path(tmp) / "repo" / "autologin.py"
            entry.parent.mkdir(parents=True)
            entry.write_text("# test\n", encoding="utf-8")

            with patch.object(startup, "_startup_dir", return_value=startup_dir):
                target = startup.install(entry)
                self.assertTrue(target.exists())
                content = target.read_text(encoding="utf-8")
                self.assertIn("--watch --quiet", content)
                self.assertIn(str(entry.resolve()), content)
                self.assertTrue(startup.uninstall())
                self.assertFalse(target.exists())


if __name__ == "__main__":
    unittest.main()
