import logging
import smtplib
import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from extract.struct.mail_config import MailConfig
import codecs


class MailSender:
    def __init__(self, mail_config: MailConfig):
        self.sender = mail_config.sender
        self.subject = mail_config.subject
        self.file_password = mail_config.file_password
        self.body = mail_config.body
        self.port = mail_config.port
        self.server = mail_config.server
        self.mail_password = mail_config.mail_password
        self.receiver = mail_config.receiver
        self.iv = mail_config.iv

    def set_mail_message(self, receiver_mail, receiver_name):
        msg = MIMEMultipart()
        msg['From'] = self.sender
        msg['To'] = receiver_mail
        msg['Subject'] = self.subject

        f = codecs.open(self.body, 'r')
        body = f.read() \
            .replace('%receiver%', receiver_name) \
            .replace('%month%', self.get_this_month_name()) \
            .replace('%password%', self.file_password) \
            .replace('%iv%', self.iv)
        msg.attach(MIMEText(body, 'html'))
        return msg

    def get_this_month_name(self):
        mydate = datetime.datetime.now()
        return mydate.strftime("%B")

    def send_mail(self, server):
        for receiver_mail, receiver_name in self.receiver.items():
            msg = self.set_mail_message(receiver_mail=receiver_mail
                                        , receiver_name=receiver_name)
            text = msg.as_string()
            logging.info('send mail to {}'.format(receiver_name))
            server.sendmail(self.sender, receiver_mail, text)

    def execute(self):
        server = smtplib.SMTP(self.server, self.port)
        server.starttls()
        server.login(self.sender, self.mail_password)
        logging.info('Start send mail . . .')
        self.send_mail(server=server)
        logging.info('Send mail done.')
        server.quit()
