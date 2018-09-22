from os.path import join, isfile

import os

import const
from extract.struct.profile_config import ProfileConfig
from extract.utils.aes_management import AesManagement
from extract.utils.password_util import PasswordUtil
from extract.utils.zip_extract_file import ZipExtractFile


class EncryptionManagement:
    def __init__(self, profile_config: ProfileConfig):
        self.local_key_path = profile_config.local_key_path
        self.password_expire_date = profile_config.password_expire_date
        self.kms_path = profile_config.kms_path
        self.iv = profile_config.iv
        self.output_ext_format = profile_config.output_ext_format
        self.content_encryption = profile_config.content_encryption
        self.password_util = PasswordUtil()
        if self.kms_path:
            self._set_key()
        else:
            self.password_util.password = None

    def _set_key(self):
        self.password_util.get_password_from_gcs(gcs_path=self.local_key_path,
                                                            password_expire_date=self.password_expire_date,
                                                            kms_path=self.kms_path)

    def encryption_file(self, dir_to_encrypt):
        if self.content_encryption:
            encryption_path = self._encrypt_file_content(dir_to_encrypt=dir_to_encrypt)
        elif self.output_ext_format == '.zip':
            encryption_path = self._encrypt_zip_file(dir_to_encrypt=dir_to_encrypt)
        else:
            raise Exception('Not found any kms mode.')

        return encryption_path,self.password_util

    def _encrypt_zip_file(self, dir_to_encrypt) -> (str):
        with ZipExtractFile(password_length=const.PASSWORD_LENGTH, dir_to_zip=dir_to_encrypt) as zip_extract_file:
            encryption_path = zip_extract_file.create_zip_file(zip_password=self.password_util.password)

        return encryption_path

    def _encrypt_file_content(self, dir_to_encrypt) -> (str):
        file_list = [join(dir_to_encrypt, file) for file in os.listdir(dir_to_encrypt) if
                     os.path.isfile(join(dir_to_encrypt, file))]
        aes_management = AesManagement(key_str=self.password_util.password, fullpath_filename=file_list[0], iv_str=self.iv)
        encryption_path = file_list[0] + '.encrypt'
        aes_management.encrypt_file(encrypted_filename=encryption_path)

        return encryption_path
