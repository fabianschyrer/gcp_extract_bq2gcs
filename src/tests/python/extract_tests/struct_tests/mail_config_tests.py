import unittest
from unittest.mock import patch, mock_open, MagicMock
from dp_extract.struct.mail_config import MailConfig
import const
import builtins


class TestMailConfig(unittest.TestCase):
    def setUp(self):
        self.mail_config = MailConfig()

    @patch.object(MailConfig, MailConfig.get_mail_password.__name__)
    @patch('dp_extract.struct.mail_config.ProfileConfig')
    def test_load_config(self, profile_config, _get_mail_password):
        mock_profile_config = MagicMock()
        profile_config.return_value = mock_profile_config
        mock_profile_config.mail_env = '_env'
        mock_profile_config.mail_profile = '_profile'

        yaml_data = '''
password_path: _password/_path
sender: _sender
body: _body
server: _server
port: _port
        '''
        with patch.object(builtins, open.__name__, new_callable=mock_open, read_data=yaml_data) as _open:
            mail_config = MailConfig()
            mail_config.load_config(mock_profile_config, '_password')
            expected_body = const.TEMPLATE_DIR + '/' + '_body'
            _open.assert_called_once()
            self.assertEqual(mail_config.password_path, '_password/_path')
            self.assertEqual(mail_config.sender, '_sender')
            self.assertEqual(mail_config.body, expected_body)
            self.assertEqual(mail_config.server, '_server')
            self.assertEqual(mail_config.port, '_port')
            self.assertEqual(mail_config.file_password, '_password')
            _get_mail_password.assert_called_once()

    @patch('dp_extract.struct.mail_config.PasswordUtil')
    def test_get_mail_password(self, password_util):
        mock_password_util = MagicMock()
        password_util.return_value = mock_password_util
        mock_password_util.get_password_from_gcs.return_value = 'password'
        result = self.mail_config.get_mail_password('_kms')
        self.assertEqual(result, 'password')

    def test_validate_config_password_path(self):
        mail_config = MailConfig()
        mail_config.password_path = None
        mail_config.sender = '_sender'
        mail_config.subject = '_subject'
        mail_config.body = '_body'
        mail_config.server = '_server'
        mail_config.port = '_port'
        with self.assertRaises(AttributeError):
            mail_config.validate_config()

    def test_validate_config_sender(self):
        mail_config = MailConfig()
        mail_config.password_path = '_password_path'
        mail_config.sender = None
        mail_config.subject = '_subject'
        mail_config.body = '_body'
        mail_config.server = '_server'
        mail_config.port = '_port'
        with self.assertRaises(AttributeError):
            mail_config.validate_config()

    def test_validate_config_body(self):
        mail_config = MailConfig()
        mail_config.password_path = '_password_path'
        mail_config.sender = '_sender'
        mail_config.subject = '_subject'
        mail_config.body = None
        mail_config.server = '_server'
        mail_config.port = '_port'

        with self.assertRaises(AttributeError):
            mail_config.validate_config()

    def test_validate_config_server(self):
        mail_config = MailConfig()
        mail_config.password_path = '_password_path'
        mail_config.sender = '_sender'
        mail_config.subject = '_subject'
        mail_config.body = '_body'
        mail_config.server = None
        mail_config.port = '_port'

        with self.assertRaises(AttributeError):
            mail_config.validate_config()

