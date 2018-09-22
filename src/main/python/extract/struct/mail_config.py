import logging
import os
from base64 import b64decode

import yaml

from extract.struct.profile_config import ProfileConfig

import const
from extract.utils.password_util import PasswordUtil


class MailConfig:
    EMAIL_PASSWORD_EXPIRE_DATE = 0
    def __init__(self):
        self.password_path:str = None
        self.mail_password = None
        self.sender: str = None
        self.receiver: dict = None
        self.subject: str = None
        self.body: str = None
        self.server: str = None
        self.port : str = None
        self.iv: str = None

        self.file_password: str = None

    def load_config(self, profile_config:ProfileConfig, password:str) -> None:
        logging.info('Load mail config file . . .')
        mail_config_path = os.path.join(const.MAIL_PROFILE_DIR, profile_config.mail_env, profile_config.mail_profile + '.yaml')
        with open(mail_config_path, 'rb') as mail_info:
            mail_info = yaml.load(mail_info)


        self.file_password = password

        self.password_path = mail_info.get('password_path')
        self.mail_password = self.get_mail_password(kms_path=profile_config.kms_path)
        self.sender = mail_info.get('sender')
        self.receiver = profile_config.mail_receiver
        self.subject = profile_config.mail_subject
        self.body = os.path.join(const.TEMPLATE_DIR,mail_info.get('body'))
        self.server = mail_info.get('server')
        self.port = mail_info.get('port')
        self.iv = profile_config.iv

        self.validate_config()

    def validate_config(self):
        if not self.password_path:
            raise AttributeError('Please specific mail password path in config file.')

        if not self.sender:
            raise AttributeError('Please specific sender mail in mail config file.')

        if not self.server or not self.port:
            raise AttributeError('Please specific server or port in mail config file.')

        if not self.body:
            raise AttributeError('Please specific email template in mail config')

    def get_mail_password(self, kms_path: str) -> str:
        logging.debug('Get mail password from GCS.')
        password_util = PasswordUtil()
        return password_util.get_password_from_gcs(gcs_path=self.password_path
                                            , password_expire_date=self.EMAIL_PASSWORD_EXPIRE_DATE
                                            , kms_path=kms_path)
