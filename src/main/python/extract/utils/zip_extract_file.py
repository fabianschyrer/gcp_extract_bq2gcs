import logging
import pyminizip
import const
import os
from extract.utils.password_util import PasswordUtil


class ZipExtractFile:
    file_list = []
    dir_list = []
    COMPRESS_LEVEL_DEFAULT = 0

    def __init__(self, password_length: int, dir_to_zip: str):
        self.password_len = password_length
        self.dir_to_zip = dir_to_zip

    def __enter__(self):
        return self

    def create_zip_file(self, zip_password) -> str:
        zip_file_name = self.dir_to_zip + const.ZIP_EXTENSION
        logging.info('Zip file {}'.format(zip_file_name))
        for dirname, subdir, filenames in os.walk(self.dir_to_zip):
            for file in filenames:
                self.file_list.append(os.path.join(dirname, file))
                self.dir_list.append(os.path.basename(dirname))

        """"check number of file"""
        if len(self.file_list) > 1:
            pyminizip.compress_multiple(self.file_list, self.dir_list, zip_file_name, zip_password, self.COMPRESS_LEVEL_DEFAULT)
            return zip_file_name

        elif len(self.file_list) == 1:
            pyminizip.compress(self.file_list[0], None, zip_file_name, zip_password, self.COMPRESS_LEVEL_DEFAULT)
            return zip_file_name
        else:
            logging.error("No file in to zip.")

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass
