import unittest
from unittest.mock import patch, MagicMock
import datetime

from dp_extract.struct.mail_config import MailConfig
from dp_extract.utils.mail_sender import MailSender

class MailSenderTest(unittest.TestCase):
    def setUp(self):
        mail_config = MailConfig()
        mail_config.sender = '_sender'
        mail_config.file_password = '_file_password'
        mail_config.body = '_%receiver%_%month%_%password%'
        mail_config.port = '_port'
        mail_config.server = '_server'
        mail_config.iv = '_iv'
        mail_config.mail_password = '_password'
        self.mail_sender = MailSender(mail_config=mail_config)

    @patch('dp_extract.utils.mail_sender.datetime')
    def test__get_this_month_name(self,datetime_mock):
        expected = 'June'
        datetime_mock.datetime.now.return_value = datetime.datetime.strptime('2018-06-07','%Y-%m-%d')
        actual = self.mail_sender.get_this_month_name()
        self.assertEqual(expected,actual)

    @patch.object(MailSender, MailSender.get_this_month_name.__name__)
    @patch('codecs.open')
    @patch('email.mime.multipart.MIMEMultipart')
    def test__set_mail_message(self, mime_multipart, codecs_open, _get_this_month_name):
        msg = MagicMock()
        mime_multipart.return_value = msg

        f = MagicMock()
        codecs_open.return_value = f
        f.read.return_value = self.mail_sender.body

        _get_this_month_name.return_value = 'month'
        mock_receiver_name = '_receiver_name'
        mock_receiver_mail = '_receiver_mail'
        result = self.mail_sender.set_mail_message(receiver_name=mock_receiver_name
                                                   ,receiver_mail=mock_receiver_mail)
        actual = result._payload[0]._payload
        expected = '__receiver_name_month__file_password'
        self.assertEqual(actual,expected)
        _get_this_month_name.assert_called_once()

    @patch('smtplib.SMTP')
    @patch.object(MailSender, MailSender.set_mail_message.__name__)
    def test__send_mail(self,set_mail_message, smtp):
        mock_receiver = {
            "mail1":"user1",
            "mail2":"user2",
            "mail3":"user3",
            "mail5":"user4"
        }
        server = MagicMock()
        msg = MagicMock()
        server.sendmail.return_value = MagicMock()
        set_mail_message.return_value = msg
        msg.as_string.return_value = MagicMock()
        self.mail_sender.receiver = mock_receiver
        self.mail_sender.send_mail(server=server)
        assert set_mail_message.call_count == 4

    @patch.object(MailSender, MailSender.send_mail.__name__)
    @patch('smtplib.SMTP')
    def test_execute(self, smtp, send_mail):
        server = MagicMock()
        smtp.return_value =server
        server.starttls.return_value = MagicMock()
        server.login.return_value = MagicMock()
        server.quit.return_value = MagicMock()

        self.mail_sender.execute()
        server.starttls.assert_called_once()
        server.login.assert_called_once()
        server.quit.assert_called_once()
        send_mail.assert_called_once()
        smtp.assert_called_once()



