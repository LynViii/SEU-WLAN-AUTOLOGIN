import unittest
from pathlib import Path
from unittest.mock import patch

import autologin


class CliTests(unittest.TestCase):
    def test_startup_not_installed_when_password_cannot_persist(self):
        with (
            patch.object(autologin.credentials, "get", return_value=("213000000", "secret")),
            patch.object(autologin.credentials, "has_persisted_password", return_value=False),
            patch.object(autologin.credentials, "store", return_value=False),
            patch.object(autologin.startup, "install") as install,
        ):
            code = autologin.main(["--install-startup"])

        self.assertEqual(code, 1)
        install.assert_not_called()

    def test_startup_installs_after_persistence_check(self):
        fake_path = Path("startup.cmd")
        with (
            patch.object(autologin.credentials, "get", return_value=("213000000", "secret")),
            patch.object(autologin.credentials, "has_persisted_password", return_value=True),
            patch.object(autologin.startup, "install", return_value=fake_path) as install,
            patch.object(autologin.startup, "is_frozen", return_value=False),
        ):
            code = autologin.main(["--install-startup"])

        self.assertEqual(code, 0)
        install.assert_called_once()

    def test_version_option(self):
        with self.assertRaises(SystemExit) as raised:
            autologin.build_parser().parse_args(["--version"])
        self.assertEqual(raised.exception.code, 0)

    def test_diagnose_does_not_read_credentials(self):
        with (
            patch.object(autologin.credentials, "get") as get_credentials,
            patch.object(autologin.client, "status", return_value=autologin.client.Status(True, "10.0.0.1")),
            patch.object(autologin.startup, "is_frozen", return_value=False),
        ):
            code = autologin.main(["--diagnose"])

        self.assertEqual(code, 0)
        get_credentials.assert_not_called()


if __name__ == "__main__":
    unittest.main()
