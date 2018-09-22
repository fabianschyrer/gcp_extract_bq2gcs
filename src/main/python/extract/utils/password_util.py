import logging
import secrets

import datetime
import time

from google.cloud.storage import Blob

import const
from extract.utils.kms_management import KmsManagement
from extract.utils.storage_util import StorageUtil
from extract.utils.string_util import StringUtil


class PasswordUtil:

    def __init__(self):
        self.is_new_password = False
        self.password = None

    def generate_password(self,password_length):
        DEFAULT_CHARSET = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*()'
        self.is_new_password = True
        return "".join([secrets.choice(DEFAULT_CHARSET) for _ in range(0, password_length)])


    def get_password_from_gcs(self, gcs_path: str, password_expire_date: int, kms_path: str) -> str:
        logging.info('Checking key . . .')
        kms_management = KmsManagement(kms_path=kms_path)
        bucket_name, file_path = StringUtil.split_bucket_path(gcs_path)

        storage_util = StorageUtil(bucket=bucket_name)
        bucket = storage_util.bucket

        return self._generate_password_if_invalid(kms_management=kms_management
                                                  , bucket=bucket
                                                  , password_expire_date=password_expire_date
                                                  , storage_util= storage_util
                                                  , file_path=file_path)


    def _generate_password_if_invalid(self,kms_management
                                      , bucket
                                      , password_expire_date
                                      , storage_util
                                      , file_path):
        gcs_file_path = self.get_password_file_name(gcs_file_name=file_path
                                                    ,password_expire_date=password_expire_date)


        if self.is_key_not_exist(gcs_file_path=gcs_file_path, bucket=bucket):
            logging.info("No existing key or key expire generate new key.")
            self.password = self.generate_password(password_length=const.PASSWORD_LENGTH)
        else:
            logging.info("Use existing key")
            ciphertext = storage_util.read_text_file_from_gcs(gcs_file_path=gcs_file_path)
            byte_password = kms_management.decrypted_local_password(ciphertext=ciphertext)
            self.password = bytes.decode(byte_password)

        self._write_back_to_gcs(self.password, gcs_path=gcs_file_path, storage_util=storage_util, kms_management=kms_management)
        return self.password

    def _write_back_to_gcs(self, password: str, gcs_path: str, storage_util: StorageUtil, kms_management: KmsManagement):
        byte_password = str.encode(password)
        cypher_text = kms_management.encrypt_password_with_kms(plaintext=byte_password)
        storage_util.write_text_file_to_gcs(text_to_write=cypher_text, gcs_file_path=gcs_path)

    def is_key_not_exist(self, gcs_file_path, bucket):

        blob = Blob(name=gcs_file_path, bucket=bucket)
        return not blob.exists()

    def get_password_file_name(self,gcs_file_name: str, password_expire_date: int):
        if password_expire_date == const.NO_EXPIRED_DATE:
            return gcs_file_name
        else:
            today_date = datetime.date.today()
            expire_date = datetime.date.today().replace(day=password_expire_date)

            if today_date < expire_date:
                this_month = datetime.date.today().replace(day=1)
                lastMonth = this_month - datetime.timedelta(days=1)
                return gcs_file_name.format(lastMonth.strftime('%Y%m'))
            elif today_date >= expire_date:
                return gcs_file_name.format(time.strftime('%Y%m'))
