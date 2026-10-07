import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

from seu_wlan import credentials


class CredentialsTests(unittest.TestCase):
    def setUp(self):
        self.original_config = credentials.CONFIG_FILE
        self.tempdir = tempfile.TemporaryDirectory()
        credentials.CONFIG_FILE = Path(self.tempdir.name) / "config.json"

    def tearDown(self):
        credentials.CONFIG_FILE = self.original_config
        self.tempdir.cleanup()

    def test_store_writes_username_and_keyring_password(self):
        fake_keyring = Mock()
        with patch.object(credentials, "keyring", fake_keyring):
            self.assertTrue(credentials.store("213000000", "secret"))

        data = json.loads(credentials.CONFIG_FILE.read_text(encoding="utf-8"))
        self.assertEqual(data["username"], "213000000")
        fake_keyring.set_password.assert_called_once_with(
            credentials.SERVICE_NAME, "213000000", "secret"
        )

    def test_store_refuses_plaintext_fallback_without_keyring(self):
        with patch.object(credentials, "keyring", None):
            self.assertFalse(credentials.store("213000000", "secret"))

        data = json.loads(credentials.CONFIG_FILE.read_text(encoding="utf-8"))
        self.assertEqual(data, {"username": "213000000"})
        self.assertNotIn("secret", credentials.CONFIG_FILE.read_text(encoding="utf-8"))

    def test_environment_credentials_take_priority(self):
        with patch.dict(
            os.environ,
            {
                credentials.ENV_USERNAME: "env-user",
                credentials.ENV_PASSWORD: "env-pass",
            },
            clear=False,
        ):
            self.assertEqual(credentials.get(interactive=False), ("env-user", "env-pass"))


if __name__ == "__main__":
    unittest.main()
