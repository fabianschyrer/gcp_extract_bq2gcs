import unittest
from unittest.mock import patch, MagicMock, ANY

from dp_extract.utils.directory_util import DirectoryUtil


class DirectoryUtilTest(unittest.TestCase):

    @patch('pathlib.Path')
    def test_create_temp_dir(self,pathlib_path):
        pathlib_path.return_value = MagicMock()
        result = DirectoryUtil.create_temp_dir('_temp/_output')
        pathlib_path.assert_called()
        self.assertEqual(result, '_temp/_output')

    @patch('shutil.rmtree')
    @patch('os.path.isdir')
    def test_clean_dir_isdir(self, is_dir, rmtree):
        dir = '_temp'
        is_dir.return_value = True
        DirectoryUtil.clean_dir(dir)
        rmtree.assert_called_once()

    @patch('shutil.rmtree')
    @patch('os.path.isdir')
    def test_clean_dir_not_dir(self, is_dir, rmtree):
        dir = '_temp'
        is_dir.return_value = False
        DirectoryUtil.clean_dir(dir)
        assert not rmtree.called
