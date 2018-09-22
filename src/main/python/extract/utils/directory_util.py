import logging
import pathlib

import os

import shutil

class DirectoryUtil():

    @staticmethod
    def create_temp_dir(temp_dir):
        pathlib.Path(temp_dir).mkdir(parents=True, exist_ok=True)
        return temp_dir

    @staticmethod
    def clean_dir(dir):
        if os.path.isdir(dir):
            shutil.rmtree(dir)
        else:
            logging.warning('No directory to clean up: ' + dir)