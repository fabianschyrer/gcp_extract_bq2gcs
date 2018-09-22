import os


class StringUtil:

    @staticmethod
    def split_bucket_path(path: str) -> (str,str):
        return path.split(sep='://')[-1].split(sep='/', maxsplit=1)

    @staticmethod
    def get_path_basename(path: str) -> (str):
        return os.path.splitext(os.path.basename(path))[0]