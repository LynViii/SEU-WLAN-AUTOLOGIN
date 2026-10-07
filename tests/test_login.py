import base64
import unittest
from unittest.mock import Mock

import login


class JsonpTests(unittest.TestCase):
    def test_parse_jsonp(self):
        result = login.parse_jsonp('dr1002({"result":0,"v46ip":"10.0.0.1"})')
        self.assertEqual(result["result"], 0)

    def test_parse_jsonp_rejects_invalid_data(self):
        with self.assertRaises(login.GatewayError):
            login.parse_jsonp("not-json")


class GatewayTests(unittest.TestCase):
    def test_status_not_authenticated(self):
        response = Mock()
        response.text = 'dr1002({"result":0,"v46ip":"10.0.0.8"})'
        response.raise_for_status.return_value = None
        session = Mock()
        session.get.return_value = response

        status = login.get_status(session)
        self.assertFalse(status.authenticated)
        self.assertEqual(status.ip, "10.0.0.8")

    def test_auth_success(self):
        response = Mock()
        response.text = 'dr1003({"result":"1","msg":""})'
        response.raise_for_status.return_value = None
        session = Mock()
        session.get.return_value = response
        status = login.NetworkStatus(authenticated=False, ip="10.0.0.8")

        result = login.authenticate("213000000", "secret", session=session, status=status)
        self.assertTrue(result.authenticated)
        _, kwargs = session.get.call_args
        self.assertEqual(kwargs["params"]["user_account"], ",0,213000000")
        self.assertEqual(kwargs["params"]["user_password"], "secret")

    def test_auth_known_password_error(self):
        message = base64.b64encode(b"userid error2").decode()
        response = Mock()
        response.text = f'dr1003({{"result":"0","msg":"{message}"}})'
        response.raise_for_status.return_value = None
        session = Mock()
        session.get.return_value = response
        status = login.NetworkStatus(authenticated=False, ip="10.0.0.8")

        with self.assertRaisesRegex(login.AuthenticationError, "密码错误"):
            login.authenticate("213000000", "bad", session=session, status=status)


if __name__ == "__main__":
    unittest.main()
