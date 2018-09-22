import unittest
from unittest.mock import patch, MagicMock

from dp_extract.encryption_management import EncryptionManagement
from dp_extract.struct.profile_config import ProfileConfig


class TestEncryptionManagement(unittest.TestCase):

    def setUp(self):
        profile_config = ProfileConfig()
        self.encryption_management = EncryptionManagement(profile_config=profile_config)


    def test__set_key(self):
        password_util = MagicMock()
        self.encryption_management.password_util = password_util
        password_util.get_password_from_gcs = MagicMock()
        self.encryption_management._set_key()
        self.assertEqual(password_util.get_password_from_gcs.call_count, 1)

    @patch.object(EncryptionManagement, EncryptionManagement._encrypt_file_content.__name__)
    def test_encryption_file_content_encrypt(self, _encryption_file_content):
        self.encryption_management.content_encryption = True
        self.encryption_management.password_util = '_password_util'
        _encryption_file_content.return_value = '_encrypt_file_path'
        expected_1 = '_encrypt_file_path'
        expected_2 = '_password_util'
        result1, result2 = self.encryption_management.encryption_file('_dir')
        self.assertEqual(result1, expected_1)
        self.assertEqual(result2, expected_2)
        self.assertEqual(_encryption_file_content.call_count,1)

    @patch.object(EncryptionManagement, EncryptionManagement._encrypt_zip_file.__name__)
    def test_encryption_file_content_zip_file(self, _encryption_zip_file):
        self.encryption_management.output_ext_format = '.zip'
        self.encryption_management.password_util = '_password_util'
        _encryption_zip_file.return_value = '_encryption_zip_file'
        expected_1 = '_encryption_zip_file'
        expected_2 = '_password_util'
        result1, result2 = self.encryption_management.encryption_file('_dir')
        self.assertEqual(result1, expected_1)
        self.assertEqual(result2, expected_2)
        self.assertEqual(_encryption_zip_file.call_count,1)

    @patch('dp_extract.encryption_management.ZipExtractFile.create_zip_file')
    def test_encrypt_zip_file(self,_zip_extract_file):
        _zip_extract_file.return_value = '_dir'
        result = self.encryption_management._encrypt_zip_file('_dir')
        self.assertEqual(result, '_dir')
        self.assertEqual(_zip_extract_file.call_count, 1)

    @patch('os.path.isfile')
    @patch('dp_extract.encryption_management.AesManagement')
    @patch('dp_extract.encryption_management.os')
    def test_encrypt_file_content(self,os, aes_management, isfile):
        dir_to_encrypt = '_dir'
        isfile.return_value = True
        os.listdir.return_value = ['file1.csv']
        aes_management.encrypt_file = MagicMock()
        result = self.encryption_management._encrypt_file_content(dir_to_encrypt=dir_to_encrypt)
        self.assertEqual(result, '_dir/file1.csv.encrypt')


