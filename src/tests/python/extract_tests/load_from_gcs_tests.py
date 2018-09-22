import unittest
from unittest.mock import patch, MagicMock

import os

import shutil

import const
from dp_extract.load_from_gcs import LoadFromGCS


class TestLoadFromGcs(unittest.TestCase):

    def setUp(self):
        gcs_path = 'gs://_bucket/_temp'
        file_format = 'csv'
        self.load_from_gcs = LoadFromGCS(gcs_path=gcs_path,
                                         file_format=file_format)

    @patch('google.cloud.storage.Client')
    @patch.object(LoadFromGCS, LoadFromGCS.load_from_list.__name__)
    @patch.object(LoadFromGCS, LoadFromGCS._clean_bucket.__name__)
    @patch.object(LoadFromGCS, LoadFromGCS._create_temp_dir.__name__)
    def test__download_gcs_temp_to_local(self, _create_temp_dir: MagicMock,
                                         _clean_bucket: MagicMock,
                                         load_from_list: MagicMock,
                                         storage_client):

        bucket = MagicMock()
        list_files = MagicMock()
        storage_client.get_bucket.return_value = bucket
        bucket.list_blobs.return_value = list_files

        self.load_from_gcs.download_gcs_temp_to_local()

        _create_temp_dir.assert_called_once()
        _clean_bucket.assert_called_once()
        load_from_list.assert_called_once()

    @patch('google.cloud.storage.Bucket')
    @patch('builtins.open')
    def test__load_from_list(self, open,bucket):
        class File:
            def __init__(self,name):
                self.name = name
            def name(self):
                return self.name
        file_list = [File('test.csv')]
        blob = MagicMock()
        blob.download_to_file = MagicMock()
        bucket.blob.return_value = blob
        self.load_from_gcs.load_from_list(list_files=file_list,bucket=bucket)

        blob.download_to_file.assert_called_once()

    @patch('google.cloud.storage.Bucket')
    @patch('builtins.open')
    def test__load_from_list_multiple_file(self, open, bucket):
        class File:
            def __init__(self, name):
                self.name = name

            def name(self):
                return self.name

        file_list = [File('test.csv'),File('test2.csv'),File('test3.zip')]
        blob = MagicMock()
        blob.download_to_file = MagicMock()
        bucket.blob.return_value = blob
        self.load_from_gcs.load_from_list(list_files=file_list, bucket=bucket)

        assert blob.download_to_file.call_count == 2

    def test__create_temp_dir(self):
        _temp_dir = os.path.join(const.ROOT,'_temp_test')
        result = self.load_from_gcs._create_temp_dir(_temp_dir)
        self.assertTrue(os.path.exists(_temp_dir))
        self.assertTrue(os.path.isdir(_temp_dir))
        self.assertEqual(result, _temp_dir)
        shutil.rmtree(_temp_dir)

    def test__clean_bucket(self):
        bucket = MagicMock()
        bucket.delete_blob = MagicMock()
        self.load_from_gcs._clean_bucket(bucket)
        self.assertEqual(bucket.delete_blob.call_count, 1)