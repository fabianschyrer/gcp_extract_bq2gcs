import unittest
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock, ANY

from dp_extract.utils.password_util import PasswordUtil

class PasswordUtilTest(unittest.TestCase):

    def setUp(self):
        self.password_util = PasswordUtil()

    def test__generate_password_new(self):
        password_length = 16
        expected_new_password = True

        expect_length = 16
        generate_password = self.password_util.generate_password(password_length=password_length)

        self.assertEqual(self.password_util.is_new_password,expected_new_password)
        self.assertEqual(len(generate_password),expect_length)

    @patch.object(PasswordUtil, PasswordUtil._generate_password_if_invalid.__name__)
    @patch('dp_extract.utils.password_util.StorageUtil')
    @patch('dp_extract.utils.password_util.KmsManagement')
    def test__get_password_from_gcs(self, kms_management, storage_util, _generate_password_if_invalid):
        storage_util.bucket.return_value = MagicMock()
        self.password_util.get_password_from_gcs('gs://_bucket/_file',1,'_kms_path')

        _generate_password_if_invalid.assert_called_once()

    @patch.object(PasswordUtil, PasswordUtil.get_password_file_name.__name__)
    @patch.object(PasswordUtil, PasswordUtil._write_back_to_gcs.__name__)
    @patch.object(PasswordUtil, PasswordUtil.generate_password.__name__)
    @patch.object(PasswordUtil, PasswordUtil.is_key_not_exist.__name__)
    def test__generate_password_if_invalid_invalid(self, is_key_not_exist, generate_password, _write_back_to_gcs,get_password_file_name):
        is_key_not_exist.return_value = True
        generate_password.return_value = 'password'
        get_password_file_name.return_value = '_file_name'
        result_password = self.password_util._generate_password_if_invalid('_kms','_bucket','_password','_storage','_file')
        expected = 'password'
        generate_password.assert_called_once()
        _write_back_to_gcs.assert_called_once()
        self.assertEqual(expected, result_password)

    @patch.object(PasswordUtil, PasswordUtil.get_password_file_name.__name__)
    @patch.object(PasswordUtil, PasswordUtil._write_back_to_gcs.__name__)
    @patch('dp_extract.utils.password_util.StorageUtil')
    @patch('dp_extract.utils.password_util.KmsManagement')
    @patch.object(PasswordUtil, PasswordUtil.is_key_not_exist.__name__)
    def test__generate_password_if_invalid_valid(self, is_key_not_exist, kms_management, storage_util,_write_back_to_gcs, get_password_file_name):
        ciphertext = MagicMock()
        mock_password = 'password'
        byte_mock_password = str.encode(mock_password)
        get_password_file_name.return_value = '_file_name'
        is_key_not_exist.return_value = False
        storage_util.read_text_file_from_gcs.return_value = ciphertext
        kms_management.decrypted_local_password.return_value = byte_mock_password

        result_password = self.password_util._generate_password_if_invalid(kms_management,'_bucket','_password',storage_util,'_file')
        self.assertEqual(result_password, mock_password)
        _write_back_to_gcs.assert_called_once()

    @patch('dp_extract.utils.password_util.StorageUtil')
    @patch('dp_extract.utils.password_util.KmsManagement')
    def test__write_back_to_gcs(self,kms_management, storage_util):
        cypher_text = MagicMock()
        kms_management.encrypt_password_with_kms.return_value = cypher_text
        storage_util.write_text_file_to_gcs.return_value = MagicMock()

        self.password_util._write_back_to_gcs('password',ANY,storage_util,kms_management)
        assert kms_management.encrypt_password_with_kms.called_once()
        assert storage_util.write_text_file_to_gcs.called_once()

    @patch('dp_extract.utils.password_util.Blob')
    def test_is_key_not_exist(self,blob):
        mock_blob = MagicMock()
        blob.return_value = mock_blob
        mock_blob.exists.return_value = True
        self.assertFalse(self.password_util.is_key_not_exist(ANY,ANY))

    @patch('dp_extract.utils.password_util.time')
    @patch('dp_extract.utils.password_util.datetime')
    def test_get_password_file_name(self, datetime_mock, time_mock):
        password_expire_date = 5
        gcs_path = '_gcs_{}'
        mock_today = datetime.strptime('20180501','%Y%m%d').date()
        datetime_mock.date.today.return_value = mock_today
        datetime_mock.timedelta.return_value = timedelta(days=1)
        password_not_expire_result = self.password_util.get_password_file_name(gcs_path,password_expire_date)
        expected = gcs_path.format('201804')
        self.assertEqual(expected, password_not_expire_result)

        time_mock.strftime.return_value = mock_today.strftime('%Y%m')
        password_expire_date = 1
        expected = gcs_path.format('201805')
        password_expire_result = self.password_util.get_password_file_name(gcs_path,password_expire_date)
        self.assertEqual(expected, password_expire_result)

        password_expire_date = 0
        expected = gcs_path
        password_no_expire_date_result = self.password_util.get_password_file_name(gcs_path,password_expire_date)
        self.assertEqual(expected, password_no_expire_date_result)