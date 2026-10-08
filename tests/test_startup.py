import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

from seu_wlan import startup


class StartupTests(unittest.TestCase):
    def test_windows_source_install(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            startup_dir = root / "Startup"
            entry = root / "repo" / "autologin.py"
            entry.parent.mkdir(parents=True)
            entry.write_text("# test\n", encoding="utf-8")

            with (
                patch.object(startup, "_startup_dir", return_value=startup_dir),
                patch.object(startup, "is_frozen", return_value=False),
            ):
                target = startup._install_windows(entry)

            content = target.read_text(encoding="utf-8")
            self.assertIn("--watch --quiet", content)
            self.assertIn(str(entry.resolve()), content)

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
                target = startup._install_windows(root / "ignored.py")

            installed = app_dir / startup.EXE_NAME
            self.assertEqual(installed.read_bytes(), b"fake-exe")
            content = target.read_text(encoding="ascii")
            self.assertIn("%LOCALAPPDATA%", content)
            self.assertIn("--watch --quiet", content)
            self.assertNotIn(str(source), content)

    def test_macos_launch_agent_generation(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            launch_dir = root / "LaunchAgents"
            entry = root / "autologin.py"
            entry.write_text("# test\n", encoding="utf-8")
            completed = Mock(returncode=0)

            with (
                patch.object(startup, "_mac_launch_agents_dir", return_value=launch_dir),
                patch.object(startup.subprocess, "run", return_value=completed),
                patch.object(startup.os, "getuid", return_value=501),
            ):
                target = startup._install_macos(entry)

            content = target.read_text(encoding="utf-8")
            self.assertIn("io.github.lynviii.seu-wlan-autologin", content)
            self.assertIn("--watch", content)
            self.assertIn("--quiet", content)

    def test_linux_user_service_generation(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            service_dir = root / "systemd"
            entry = root / "autologin.py"
            entry.write_text("# test\n", encoding="utf-8")

            with (
                patch.object(startup, "_linux_user_service_dir", return_value=service_dir),
                patch.object(startup.shutil, "which", return_value="/usr/bin/systemctl"),
                patch.object(startup.subprocess, "run") as run,
            ):
                target = startup._install_linux(entry)

            content = target.read_text(encoding="utf-8")
            self.assertIn("ExecStart=", content)
            self.assertIn("--watch", content)
            self.assertIn("--quiet", content)
            self.assertGreaterEqual(run.call_count, 2)


if __name__ == "__main__":
    unittest.main()
