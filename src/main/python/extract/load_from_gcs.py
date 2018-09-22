import logging
import os

import pathlib
from google.cloud import storage
from google.cloud.exceptions import NotFound
from google.cloud.storage import Bucket

from dp_extract.utils.string_util import StringUtil
import const


class LoadFromGCS:

    def __init__(self,gcs_path: str, file_format: str):
        self.bucket_name, self.bucket_prefix = StringUtil.split_bucket_path(gcs_path)
        self.file_format = file_format
        self.local_temp_path = os.path.join(const.TEMP_DIR,StringUtil.get_path_basename(gcs_path))

    def __enter__(self):
        return self


    def download_gcs_temp_to_local(self):
        storage_client = storage.Client()
        bucket = storage_client.get_bucket(bucket_name=self.bucket_name)
        list_files = bucket.list_blobs(prefix=self.bucket_prefix)

        self._create_temp_dir(self.local_temp_path)
        self.load_from_list(list_files=list_files,bucket=bucket)

        self._clean_bucket(bucket=bucket)
        return self.local_temp_path

    def load_from_list(self,list_files,bucket: Bucket):
        for file in list_files:
            file_name, file_extension = os.path.splitext(file.name)
            if file_extension != '.' + self.file_format:
                continue

            logging.info('Load file {}.'.format(file.name))
            blob = bucket.blob(file.name)

            to_download = os.path.join(self.local_temp_path, os.path.basename(file.name))
            with open(to_download, 'wb') as file_obj:
                self.temp = blob.download_to_file(file_obj)

    def _create_temp_dir(self,temp_dir) -> str:
        pathlib.Path(temp_dir).mkdir(parents=True, exist_ok=True)
        return temp_dir

    def _clean_bucket(self,bucket: Bucket):
        blobs = self.bucket_prefix
        try:
            logging.info('Clean temp bucket.')
            bucket.delete_blob(blobs)
        except NotFound:
            logging.error('No file in bucket')

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass




