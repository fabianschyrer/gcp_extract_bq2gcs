import logging

from google.cloud import storage
from google.cloud.storage import Blob

class StorageUtil:

    def __init__(self,bucket):
        storage_client = storage.Client()
        self.bucket = storage_client.get_bucket(bucket_name=bucket)

    def read_text_file_from_gcs(self,gcs_file_path):
        blob = self.bucket.get_blob(gcs_file_path)
        try:
            return blob.download_as_string()
        except:
            logging.error('No encryption file')
            raise FileNotFoundError

    def write_text_file_to_gcs(self, text_to_write, gcs_file_path):
        blob = Blob(name=gcs_file_path,bucket=self.bucket)
        blob.upload_from_string(text_to_write)

