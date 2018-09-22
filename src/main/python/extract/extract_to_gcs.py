import logging

import os

from google.cloud import bigquery, storage

from extract.encryption_management import EncryptionManagement
from extract.struct.mail_config import MailConfig
from extract.utils.directory_util import DirectoryUtil
from extract.utils.mail_sender import MailSender
from extract.utils.string_util import StringUtil

import const
from extract.bq_client import BqClient
from extract.struct.inputs import Inputs
from extract.struct.profile_config import ProfileConfig
from extract.load_from_gcs import LoadFromGCS


class ExtractToGcs:
    DEFAULT_TEMP_TABLE = '__temp'
    DATE_FORMAT = {
        const.Mode.DAILY: '%Y%m%d',
        const.Mode.MONTHLY: '%Y%m',
        const.Mode.HISTORICAL: '%Y%m%d'
    }
    DATE_PATH_PREFIX = {
        const.Mode.DAILY: '%Y/%m',
        const.Mode.MONTHLY: '%Y',
        const.Mode.HISTORICAL: '%Y'
    }
    OUTPUT_PATH = '{gcs}/{profile}/{date_path_prefix}'
    # OUTPUT_FILE_FORMAT = '{profile}_{date_format}{file_extension}'

    password_generator = None

    def __init__(self, inputs: Inputs, profile: ProfileConfig):
        self.inputs = inputs
        self.profile = profile

    def __enter__(self):
        return self

    def upload_to_gcs(self, file_path: str, des_path: str):
        logging.info("Uploading file to gcs")
        bucket_name, des_path = StringUtil.split_bucket_path(des_path)

        client = storage.Client(project=self.profile.project)
        bucket = client.get_bucket(bucket_name=bucket_name)

        blob = bucket.blob(des_path)
        blob.upload_from_filename(file_path)

    def extract(self):
        query_str = self._get_query()
        logging.info('query : ' + query_str)
        bq_client = BqClient(self.profile.project, self.profile.temp_dataset, self.profile.temp_table)
        logging.info('temp table : ' + bq_client.get_table_path())

        logging.info('Start querying ...')
        query_state = bq_client.query_data(query_str, self.profile.is_legacy_sql)
        logging.info('Query state : ' + query_state)
        if self.profile.kms_path or self.profile.output_ext_format == '.zip':
            self._extract_to_gcs_with_encryption(bq_client)
        else:
            logging.info("Extracting directly from BQ to GCS")
            self._extract_to_gcs(bq_client=bq_client, gcs_path=self.inputs.gcs_path)

        if self.profile.additional_file_ext:
            self.upload_additional_file()

    def _extract_to_gcs_with_encryption(self, bq_client):
        logging.info("Found Kms : Extract to GCS with encryption mode ...")
        logging.info("Extract to temp bucket {}.".format(self.profile.gcs_temp_bucket))
        temp_output_path = self._extract_to_gcs(bq_client=bq_client, gcs_path=self.profile.gcs_temp_bucket)
        local_temp_dir = self._load_from_gcs(temp_output_path=temp_output_path
                                             , file_format=self.profile.format)
        encryption_management = EncryptionManagement(self.profile)
        encrypt_file_path, self.password_generator = encryption_management.encryption_file(
            dir_to_encrypt=local_temp_dir)

        des_path = self._get_output_file_path(self.inputs.gcs_path)
        self.upload_to_gcs(file_path=encrypt_file_path, des_path=des_path)

    def _load_from_gcs(self, temp_output_path, file_format):
        logging.debug("Load extract file to local . . .")
        with LoadFromGCS(gcs_path=temp_output_path, file_format=file_format) as load_from_gcs:
            return load_from_gcs.download_gcs_temp_to_local()

    def _extract_to_gcs(self, bq_client: BqClient, gcs_path: str):
        logging.info('Start extracting ...')
        job_config = self._get_extract_job_config()
        output_path = self._get_output_file_path(gcs_path=gcs_path)
        logging.info('extract to : ' + output_path)
        extract_job = bq_client.client.extract_table(
            source=bq_client.table,
            destination_uris=output_path,
            job_config=job_config)
        extract_job.result()
        logging.info('extract state : ' + extract_job.state)

        return output_path

    def _get_extract_job_config(self):
        job_config = bigquery.job.ExtractJobConfig()
        if self.profile.format == const.FileFormat.AVRO:
            job_config.destination_format = bigquery.job.DestinationFormat.AVRO

        elif self.profile.format == const.FileFormat.CSV:
            job_config.destination_format = bigquery.job.DestinationFormat.CSV
            job_config.print_header = self.profile.header

            if self.profile.delimiter:
                job_config.field_delimiter = self.profile.delimiter

        else:
            raise ValueError('unknown file format: {}'.format(self.profile.format))

        if self.profile.compress:
            job_config.compression = bigquery.job.Compression.GZIP

        return job_config

    def _get_query(self) -> str:
        if self.inputs.mode == const.Mode.DAILY:
            query = self.profile.daily
        elif self.inputs.mode == const.Mode.MONTHLY:
            query = self.profile.monthly
        elif self.inputs.mode == const.Mode.HISTORICAL:
            query = self.profile.historical
        else:
            raise NotImplementedError

        return query.format(startDate=self.inputs.start_date, endDate=self.inputs.end_date)

    def _get_file_name(self, file_ext: str, file_format: str):
        output_date = self.inputs.start_date.strftime(self._get_date_format())
        return file_format.format(profile=self.inputs.profile,
                                              date_format=output_date,
                                              file_extension=file_ext)

    def _get_output_file_path(self, gcs_path: str):
        output_path = self._get_output_path(gcs_path=gcs_path)
        if self._is_temp(self.inputs.gcs_path, gcs_path):
            file_extension = '.' + self.profile.format
        else:
            file_extension = self.profile.output_ext_format if self.profile.output_ext_format else '.' + self.profile.format

        file_name = self._get_file_name(file_ext=file_extension, file_format=self.profile.output_file_format)
        output_file_path = os.path.join(output_path, file_name)
        return output_file_path

    def _is_temp(self, input_des: str, des_path: str) -> bool:
        if input_des == des_path:
            return False
        else:
            return True

    def _get_date_format(self):
        if self.profile.output_date_format:
            return self.profile.output_date_format
        else:
            return self.DATE_FORMAT[self.inputs.mode]

    def _get_output_path(self, gcs_path):
        date_format = self._get_date_format()
        date_path_prefix = self.DATE_PATH_PREFIX[self.inputs.mode]

        output_path = self.OUTPUT_PATH.format(
            gcs=gcs_path,
            profile=self.inputs.profile,
            date_path_prefix=self.inputs.start_date.strftime(date_path_prefix),
            date_format=self.inputs.start_date.strftime(date_format),
        )
        return output_path

    def _send_mail(self, profile_config, password):
        logging.info('Send new password to receiver.')
        mail_config = MailConfig()
        mail_config.load_config(profile_config=profile_config
                                , password=password)
        mail_sender = MailSender(mail_config=mail_config)
        mail_sender.execute()

    def __exit__(self, exc_type, exc_val, exc_tb):
        DirectoryUtil.clean_dir(const.TEMP_DIR)
        if self.password_generator is not None:
            if self.password_generator.is_new_password:
                logging.info('Using new password send an email.')
                self._send_mail(self.profile, self.password_generator.password)

            else:
                logging.info('Using existing password not send an email.')

    def upload_additional_file(self):
        logging.info("Have additional file to create . . .")
        temp_path = self.create_additional_file()
        file_name = os.path.basename(temp_path)
        des_path = os.path.join(self._get_output_path(gcs_path=self.inputs.gcs_path), file_name)

        self.upload_to_gcs(file_path=temp_path, des_path=des_path)

    def create_additional_file(self):
        logging.info("Create additional file.")
        file_name = self._get_file_name(file_ext=self.profile.additional_file_ext, file_format=self.profile.output_file_format)
        DirectoryUtil.create_temp_dir(const.TEMP_DIR)
        file_path = os.path.join(const.TEMP_DIR, file_name)
        open(file_path, 'a').close()

        return file_path
