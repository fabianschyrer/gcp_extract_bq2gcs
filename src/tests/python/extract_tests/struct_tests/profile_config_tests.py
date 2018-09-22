import builtins
import unittest
from unittest.mock import patch, MagicMock, mock_open

import const
from dp_extract.struct.profile_config import ProfileConfig


class TestProfileConfig(unittest.TestCase):
    def test_load_config(self):
        expected_receiver = {
            'mail1': 'user1',
            'mail2': 'user2'
        }
        yaml_data = '''
project : _project

daily : _daily
is_legacy_sql : true

temp_dataset : _temp
format : csv
delimiter : '|'
output_ext_format : .txt.gz
output_date_format : '%d%m%Y'
compress : true

local_key_path : gs://_dir
gcs_temp_bucket : gs://_temp_bucket
password_expire_date : 1

mail_env : _mail_env
mail_profile : _PROFILE
mail_receiver:
  mail1 : user1
  mail2 : user2

mail_subject: _mail_subject
        '''
        with patch.object(builtins, open.__name__, new_callable=mock_open, read_data=yaml_data) as _open:
            profile_config = ProfileConfig()
            profile_config.load_config('_env', '_profile')

            _open.assert_called_once()
            self.assertEqual(profile_config.project, '_project')
            self.assertEqual(profile_config.daily, '_daily')
            self.assertEqual(profile_config.monthly, None)
            self.assertEqual(profile_config.is_legacy_sql, True)
            self.assertEqual(profile_config.temp_dataset, '_temp')
            self.assertEqual(profile_config.temp_table, '_profile__temp')
            self.assertEqual(profile_config.format, 'csv')
            self.assertEqual(profile_config.delimiter, '|')
            self.assertEqual(profile_config.output_ext_format, '.txt.gz')
            self.assertEqual(profile_config.output_date_format, '%d%m%Y')
            self.assertEqual(profile_config.compress, True)
            self.assertEqual(profile_config.timezone, None)

            self.assertEqual(profile_config.local_key_path, 'gs://_dir/_profile/_profile_{}.txt')
            self.assertEqual(profile_config.gcs_temp_bucket, 'gs://_temp_bucket')
            self.assertEqual(profile_config.password_expire_date, 1)
            self.assertEqual(profile_config.mail_env, '_mail_env')
            self.assertEqual(profile_config.mail_profile, '_PROFILE')
            self.assertEqual(profile_config.mail_subject, '_mail_subject')

    def test_load_config_non_kms(self):
        yaml_data = '''
        project : _project

        daily : _daily
        is_legacy_sql : true

        temp_dataset : _temp
        format : csv
        delimiter : '|'
        output_ext_format : .txt.gz
        output_date_format : '%d%m%Y'
        compress : true
                '''
        with patch.object(builtins, open.__name__, new_callable=mock_open, read_data=yaml_data) as _open:
            profile_config = ProfileConfig()
            profile_config.load_config('_env', '_profile')

            _open.assert_called_once()
            self.assertEqual(profile_config.project, '_project')
            self.assertEqual(profile_config.daily, '_daily')
            self.assertEqual(profile_config.monthly, None)
            self.assertEqual(profile_config.is_legacy_sql, True)
            self.assertEqual(profile_config.temp_dataset, '_temp')
            self.assertEqual(profile_config.temp_table, '_profile__temp')
            self.assertEqual(profile_config.format, 'csv')
            self.assertEqual(profile_config.delimiter, '|')
            self.assertEqual(profile_config.output_ext_format, '.txt.gz')
            self.assertEqual(profile_config.output_date_format, '%d%m%Y')
            self.assertEqual(profile_config.compress, True)
            self.assertEqual(profile_config.timezone, None)

    def test_validate_config__no_format(self):
        profile = ProfileConfig()
        profile.format = None

        with self.assertRaises(AttributeError):
            profile.validate_config()

    def test_validate_config__unknown_format(self):
        profile = ProfileConfig()
        profile.profile = '_profile'
        profile.format = 'unknown'

        with self.assertRaises(ValueError):
            profile.validate_config()

    def test_validate_config__no_temp_dataset(self):
        profile = ProfileConfig()
        profile.format = const.FileFormat.CSV
        profile.temp_dataset = None

        with self.assertRaises(AttributeError):
            profile.validate_config()

    def test_validate_config__temp_table(self):
        profile = ProfileConfig()
        profile.profile = '_profile'
        profile.format = const.FileFormat.CSV
        profile.temp_dataset = '_temp_dataset'
        profile.temp_table = '_temp_table'

        profile.validate_config()

        self.assertEqual(profile.temp_table, '_temp_table__temp')

    def test_validate_config__no_temp_table(self):
        profile = ProfileConfig()
        profile.profile = '_profile'
        profile.format = const.FileFormat.CSV
        profile.temp_dataset = '_temp_dataset'
        profile.temp_table = None

        profile.validate_config()

        self.assertEqual(profile.temp_table, '_profile__temp')

    def test_validate_config__delimiter(self):
        profile = ProfileConfig()
        profile.profile = '_profile'
        profile.format = const.FileFormat.AVRO
        profile.temp_dataset = '_temp_dataset'
        profile.delimiter = '_delimiter'

        with self.assertRaises(AttributeError):
            profile.validate_config()

    def test_validate_config__kms_path(self):
        profile = ProfileConfig()
        profile.format = const.FileFormat.CSV
        profile.temp_dataset = '_temp_dataset'
        profile.kms_path = '_temp_path'
        profile.temp_table = '_temp_table'
        profile.local_key_path = '_local_key'

        with self.assertRaises(AttributeError):
            profile.validate_config()

    def test_calidate_config_mail_config(self):
        profile = ProfileConfig()
        profile.mail_env = '_env'
        profile.mail_profile = '_profile'

        with self.assertRaises(AttributeError):
            profile.validate_config()
