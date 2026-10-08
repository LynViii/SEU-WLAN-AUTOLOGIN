import base64
import unittest
from unittest.mock import Mock, patch

from seu_wlan import client


class JsonpTests(unittest.TestCase):
    def test_parse_jsonp(self):
        data = client.parse_jsonp('dr1002({"result":0,"v46ip":"10.0.0.1"})')
        self.assertEqual(data["v46ip"], "10.0.0.1")

    def test_invalid_jsonp(self):
        with self.assertRaises(client.GatewayUnavailable):
            client.parse_jsonp("oops")


class ClientTests(unittest.TestCase):
    def test_status_not_authenticated(self):
        response = Mock(text='dr1002({"result":0,"v46ip":"10.0.0.8"})')
        response.raise_for_status.return_value = None
        session = Mock()
        session.get.return_value = response
        result = client.status(session)
        self.assertFalse(result.authenticated)
        self.assertEqual(result.ip, "10.0.0.8")

    @patch("seu_wlan.client.time.sleep", return_value=None)
    def test_login_success_and_verify(self, _sleep):
        first = Mock(text='dr1002({"result":0,"v46ip":"10.0.0.8"})')
        login = Mock(text='dr1003({"result":"1","msg":""})')
        verified = Mock(text='dr1002({"result":1,"v46ip":"10.0.0.8"})')
        for response in (first, login, verified):
            response.raise_for_status.return_value = None
        session = Mock()
        session.get.side_effect = [first, login, verified]

        result = client.login("213000000", "p@ss&word", session=session)
        self.assertTrue(result.authenticated)
        _, kwargs = session.get.call_args_list[1]
        self.assertEqual(kwargs["params"]["user_account"], ",0,213000000")
        self.assertEqual(kwargs["params"]["user_password"], "p@ss&word")

    @patch("seu_wlan.client.time.sleep", return_value=None)
    def test_known_status_avoids_duplicate_status_request(self, _sleep):
        login = Mock(text='dr1003({"result":"1","msg":""})')
        verified = Mock(text='dr1002({"result":1,"v46ip":"10.0.0.8"})')
        login.raise_for_status.return_value = None
        verified.raise_for_status.return_value = None
        session = Mock()
        session.get.side_effect = [login, verified]

        result = client.login(
            "213000000",
            "secret",
            session=session,
            known_status=client.Status(False, "10.0.0.8"),
        )

        self.assertTrue(result.authenticated)
        self.assertEqual(session.get.call_count, 2)
        self.assertEqual(session.get.call_args_list[0].args[0], client.LOGIN_URL)

    def test_password_error(self):
        encoded = base64.b64encode(b"userid error2").decode()
        first = Mock(text='dr1002({"result":0,"v46ip":"10.0.0.8"})')
        rejected = Mock(text=f'dr1003({{"result":"0","msg":"{encoded}"}})')
        first.raise_for_status.return_value = None
        rejected.raise_for_status.return_value = None
        session = Mock()
        session.get.side_effect = [first, rejected]

        with self.assertRaisesRegex(client.AuthenticationRejected, "密码错误"):
            client.login("213000000", "bad", session=session)


if __name__ == "__main__":
    unittest.main()
