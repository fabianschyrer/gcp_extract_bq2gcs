import os

ROOT = os.path.dirname(os.path.realpath(__file__))
PROFILE_DIR = os.path.join(ROOT, 'profiles')
MAIL_PROFILE_DIR = os.path.join(ROOT,'mail_profile')
TEMPLATE_DIR = os.path.join(ROOT, 'template')

TEMP_DIR = os.path.join(ROOT, '_outputs')
PASSWORD_LENGTH = 16
ZIP_DIR = os.path.join(ROOT, 'temp_tozip')

INPUT_DATE_FORMAT = '%Y-%m-%d'
DEFAULT_OUTPUT_FILE_FORMAT = '{profile}_{date_format}{file_extension}'

START_YESTERDAY = 'yesterday'
END_TODAY = 'today'

DATE_TODAY = 'today'
DATE_YESTERDAY = 'yesterday'

LOCAL_ENCRYPTED_FILE = os.path.join(ROOT, 'encryped_password')
ZIP_EXTENSION = '.zip'

NO_EXPIRED_DATE = 0

class Mode:
    DAILY = 'daily'
    MONTHLY = 'monthly'
    HISTORICAL = 'historical'


class FileFormat:
    AVRO = 'avro'
    CSV = 'csv'

