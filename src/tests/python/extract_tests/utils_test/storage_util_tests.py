import unittest
from unittest.mock import patch, MagicMock, Mock, ANY
from dp_extract.utils.storage_util import StorageUtil

class StorageUtilTest(unittest.TestCase):

    def setUp(self):
        client = MagicMock()
        self.bucket = MagicMock()
        self.patcher = patch('google.cloud.storage.Client')
        self.storage_client = self.patcher.start()
        self.storage_client.return_value = client
        client.get_bucket.return_value = self.bucket
        self.storage_util = StorageUtil('_bucket')


    def test__read_text_file_from_gcs(self):
        blob = MagicMock()
        self.bucket.get_blob.return_value = blob
        blob.download_as_string.return_value = MagicMock()

        self.storage_util.read_text_file_from_gcs('_gcs_file_name')
        blob.download_as_string.assert_called_once()

    @patch('dp_extract.utils.storage_util.Blob')
    def test__write_file_to_gcs(self, blob):
        mock_blob = MagicMock()
        blob.return_value = mock_blob
        mock_blob.upload_from_string.return_value = MagicMock()
        self.storage_util.write_text_file_to_gcs(ANY,ANY)
        assert mock_blob.upload_from_string.called_once()

    def tearDown(self):
        self.patcher.stop()