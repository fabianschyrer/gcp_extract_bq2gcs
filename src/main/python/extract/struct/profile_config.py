import logging
import os

import yaml

import const


class ProfileConfig:
    DEFAULT_TEMP_TABLE = '__temp'

    def __init__(self):
        self.project: str = None
        self.daily: str = None
        self.monthly: str = None
        self.historical: str = None
        self.is_legacy_sql: bool = None
        self.temp_dataset: str = None
        self.temp_table: str = None
        self.format: str = None
        self.delimiter: str = None
        self.output_ext_format: str = None
        self.output_date_format: str = None
        self.output_file_format: str = None
        self.compress: bool = None
        self.timezone: bool = None
        self.kms_path: str = None
        self.local_key_path: str = None
        self.gcs_temp_bucket: str = None
        self.header: bool = False
        self.password_expire_date: int = None
        self.mail_env: str = None
        self.mail_profile: str = None
        self.mail_receiver: dict = None
        self.mail_subject: str = None
        self.additional_file_ext: str = None
        self.content_encryption: bool = None
        self.iv: bytes =None

    def load_config(self, env: str, profile: str) -> None:
        profile_path = os.path.join(const.PROFILE_DIR, env, profile + '.yaml')

        with open(profile_path, 'rb') as profile_info:
            profile_info = yaml.load(profile_info)

        self.env = env
        self.profile = profile

        self.project = profile_info.get('project')
        self.daily = profile_info.get('daily')
        self.monthly = profile_info.get('monthly')
        self.historical = profile_info.get('historical')
        self.is_legacy_sql = profile_info.get('is_legacy_sql')
        self.temp_dataset = profile_info.get('temp_dataset')
        self.temp_table = profile_info.get('temp_table')
        self.format = profile_info.get('format')
        self.delimiter = profile_info.get('delimiter')
        self.output_ext_format = profile_info.get('output_ext_format')
        self.output_date_format = profile_info.get('output_date_format')
        self.output_file_format = profile_info.get('output_file_format')
        self.compress = profile_info.get('compress')
        self.timezone = profile_info.get('timezone')
        self.kms_path = profile_info.get('kms_path')
        self.local_key_path = profile_info.get('local_key_path')
        self.gcs_temp_bucket = profile_info.get('gcs_temp_bucket')
        self.header = profile_info.get('header')
        self.password_expire_date = profile_info.get('password_expire_date')
        self.mail_env = profile_info.get('mail_env')
        self.mail_profile = profile_info.get('mail_profile')
        self.mail_receiver = profile_info.get('mail_receiver')
        self.mail_subject = profile_info.get('mail_subject')
        self.additional_file_ext = profile_info.get('additional_file_ext')
        self.content_encryption = profile_info.get('content_encryption')
        self.iv = profile_info.get('iv')

        self.validate_config()

    def validate_config(self):
        KEY_FILE_NAME_FORMAT = self.profile + '_{}.txt'

        if not self.format:
            raise AttributeError('press specify "format" in profile config (.yaml), e.g. "format : csv"')
        elif self.format.upper() not in const.FileFormat.__dict__:
            raise ValueError('unknown or not implemented file format.')

        if not self.temp_dataset:
            raise AttributeError(
                'press specify "temp_dataset" in profile config (.yaml), e.g. "temp_dataset : temp_auto_delete"')

        if not self.temp_table:
            logging.warning('not specific temp_table, use "<PROFILE>__temp" for temp_table')
            self.temp_table = self.profile + self.DEFAULT_TEMP_TABLE
        else:
            self.temp_table = self.temp_table + self.DEFAULT_TEMP_TABLE

        if self.format != const.FileFormat.CSV and self.delimiter:
            raise AttributeError('"delimiter" use with "format : csv" only')
        """""validate kms mode"""
        if self.local_key_path:
            self.local_key_path = os.path.join(self.local_key_path, self.profile.lower(), KEY_FILE_NAME_FORMAT)

        if self.kms_path and (not self.local_key_path or not self.gcs_temp_bucket):
            raise AttributeError('Please specific local key and gcs_temp_bucket path if use KMS mode.')

        if self.mail_env and (not self.mail_profile or not self.mail_receiver or not self.mail_subject):
            raise AttributeError('Please specific mail config [mail_env, mail_profile, mail_receiver, mail_subject]')

        if self.iv is None:
            self.iv = ''

        if self.output_file_format is None:
            self.output_file_format = const.DEFAULT_OUTPUT_FILE_FORMAT