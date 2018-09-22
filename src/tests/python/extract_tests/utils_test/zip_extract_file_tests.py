import unittest

from unittest.mock import patch, MagicMock, ANY

from dp_extract.utils.zip_extract_file import ZipExtractFile


class TestZipExtractFile(unittest.TestCase):

    def setUp(self):
        self.password_length = 16
        self.temp_file = "_dir/_to/_file"
        self.zip_extract_file = ZipExtractFile(password_length=self.password_length
                                          , dir_to_zip=self.temp_file)

    @patch('pyminizip.compress_multiple')
    @patch('os.walk')
    def test__make_zip_file_multiple_file_with_password(self,os_walk, compress_multiple):
        compress_multiple.return_value = MagicMock()
        password = 'password'
        self.zip_extract_file.dir_list = []
        self.zip_extract_file.file_list = []

        os_walk.return_value = [
            ('path1', ('subdir1'), ['file1.csv','file2.csv'])
        ]
        compress_multiple.return_value = MagicMock()
        expected = self.temp_file+'.zip'
        actual = self.zip_extract_file.create_zip_file(zip_password=password)
        compress_multiple.assert_called_once()
        self.assertEqual(actual,expected)

    @patch('pyminizip.compress_multiple')
    @patch('os.walk')
    def test__make_zip_file_multiple_file_without_password(self, os_walk, compress_multiple):
        compress_multiple.return_value = MagicMock()
        self.zip_extract_file.dir_list = []
        self.zip_extract_file.file_list = []

        os_walk.return_value = [
            ('path1', ('subdir1'), ['file1.csv', 'file2.csv'])
        ]
        compress_multiple.return_value = MagicMock()
        expected = self.temp_file + '.zip'
        actual = self.zip_extract_file.create_zip_file(zip_password=None)
        compress_multiple.assert_called_once()
        self.assertEqual(actual, expected)

    @patch('pyminizip.compress')
    @patch('os.walk')
    def test__make_zip_file_single_file_with_password(self, os_walk, compress):
        compress.return_value = MagicMock()

        password = 'password'

        os_walk.return_value = [
            ('path1', ('subdir1'), ['file1.csv'])
        ]
        compress.return_value = MagicMock()
        expected = self.temp_file+'.zip'
        self.zip_extract_file.file_list = []
        self.zip_extract_file.dir_list = []
        actual = self.zip_extract_file.create_zip_file(zip_password=password)
        compress.assert_called_once()
        self.assertEqual(actual,expected)

    @patch('pyminizip.compress_multiple')
    @patch('pyminizip.compress')
    @patch('os.walk')
    def test__make_zip_file_no_file_with_password(self,os_walk,compress,compress_multiple):
        os_walk.return_value = [
            ('path1', ('subdir1'), [])
        ]
        self.zip_extract_file.create_zip_file(zip_password=None)
        assert not compress.called
        assert not compress_multiple.called

    @patch('pyminizip.compress')
    @patch('os.walk')
    def test__make_zip_file_single_file_without_password(self, os_walk, compress):
        compress.return_value = MagicMock()

        os_walk.return_value = [
            ('path1', ('subdir1'), ['file1.csv'])
        ]
        compress.return_value = MagicMock()
        expected = self.temp_file + '.zip'
        self.zip_extract_file.file_list = []
        self.zip_extract_file.dir_list = []
        actual = self.zip_extract_file.create_zip_file(zip_password=None)
        compress.assert_called_once()
        self.assertEqual(actual, expected)