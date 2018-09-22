import unittest
from datetime import datetime
from unittest.mock import patch, MagicMock, ANY

import const
import dp_extract
from dp_extract.bq_client import BqClient
from dp_extract.extract_to_gcs import ExtractToGcs
from dp_extract.struct.inputs import Inputs
from dp_extract.struct.profile_config import ProfileConfig
from dp_extract.utils.directory_util import DirectoryUtil
from dp_extract.utils.string_util import StringUtil


class TestExtractToGcs(unittest.TestCase):
    def setUp(self):
        # start_date = datetime(2018, 5, 1)
        # end_date = datetime(2018, 5, 2)
        start_date = '2018-05-01'
        end_date = '2018-05-02'
        inputs = Inputs('_env', '_profile', 'gs://_gcs_path', '_mode', start_date, end_date)
        inputs.set_default_date(now=MagicMock, timezone=0)
        profile = ProfileConfig()
        self.extract = ExtractToGcs(inputs, profile)

    @patch.object(ExtractToGcs, ExtractToGcs._get_query.__name__)
    @patch.object(ExtractToGcs, ExtractToGcs._get_output_file_path.__name__)
    @patch.object(ExtractToGcs, ExtractToGcs._get_extract_job_config.__name__)
    @patch.object(dp_extract.extract_to_gcs, BqClient.__name__)
    def test_extract(self,
                     bq_client: BqClient,
                     _get_extract_job_config: MagicMock,
                     _get_output_path: MagicMock,
                     _get_query: MagicMock
                     ):
        self.extract.extract()

        _get_query.assert_called_once()
        _get_output_path.assert_called_once()
        _get_extract_job_config.assert_called_once()

    @patch.object(ExtractToGcs, ExtractToGcs._extract_to_gcs_with_encryption.__name__)
    @patch.object(ExtractToGcs, ExtractToGcs._get_query.__name__)
    @patch.object(dp_extract.extract_to_gcs, BqClient.__name__)
    def test_extract_with_kms(self, bq_client, get_query, extract_to_gcs_with_kms):
        self.extract.profile.kms_path = True
        self.extract.extract()
        get_query.assert_called_once()
        extract_to_gcs_with_kms.assert_called_once()

    @patch.object(ExtractToGcs, ExtractToGcs.upload_to_gcs.__name__)
    @patch.object(ExtractToGcs, ExtractToGcs._get_output_file_path.__name__)
    @patch('dp_extract.extract_to_gcs.EncryptionManagement')
    @patch.object(ExtractToGcs, ExtractToGcs._load_from_gcs.__name__)
    @patch.object(ExtractToGcs, ExtractToGcs._extract_to_gcs.__name__)
    def test_extract_to_gcs_with_encryption(self, _load_from_gcs, _extract_to_gcs, _encryption_management,
                                            _get_output_file_path, _upload_to_gcs):
        bq_client = MagicMock()
        encryption_management = MagicMock()
        _encryption_management.return_value = encryption_management
        encryption_management.encryption_file.return_value = MagicMock(), MagicMock()
        self.extract._extract_to_gcs_with_encryption(bq_client=bq_client)
        self.assertEqual(_load_from_gcs.call_count, 1)
        self.assertEqual(_extract_to_gcs.call_count, 1)
        self.assertEqual(_get_output_file_path.call_count, 1)
        self.assertEqual(_upload_to_gcs.call_count, 1)
        self.assertEqual(encryption_management.encryption_file.call_count, 1)


    @patch.object(ExtractToGcs, ExtractToGcs.upload_additional_file.__name__)
    @patch.object(ExtractToGcs, ExtractToGcs._extract_to_gcs.__name__)
    @patch.object(dp_extract.extract_to_gcs, BqClient.__name__)
    @patch.object(ExtractToGcs, ExtractToGcs._get_query.__name__)
    def test_extract_to_gcs_with_additional_file(self, get_query, bq_client, extract_to_gcs, upload_additional_file):
        self.extract.profile.additional_file_ext = ".csv"
        self.extract.profile.kms_path = False
        self.extract.extract()
        get_query.assert_called_once()
        extract_to_gcs.assert_called_once()
        upload_additional_file.assert_called_once()

    @patch.object(StringUtil, StringUtil.split_bucket_path.__name__)
    @patch.object(ExtractToGcs, ExtractToGcs._get_output_file_path.__name__)
    @patch('google.cloud.storage.Client')
    def test__upload_to_gcs(self, storage_client, _get_output_path: MagicMock, split_bucket_path):
        client = MagicMock()
        bucket = MagicMock()
        blob = MagicMock()
        split_bucket_path.return_value = MagicMock, MagicMock
        storage_client.return_value = client
        client.get_bucket.return_value = bucket
        bucket.blob.return_value = blob
        blob.upload_from_filename.return_value = MagicMock()

        self.extract.upload_to_gcs(ANY, ANY)

        split_bucket_path.assert_called_once()
        blob.upload_from_filename.assert_called_once()

    def test__get_extract_job_config__avro(self):
        self.extract.profile.format = const.FileFormat.AVRO

        result = self.extract._get_extract_job_config()

        self.assertEqual(result.destination_format, 'AVRO')
        self.assertEqual(result.print_header, None)
        self.assertEqual(result.field_delimiter, None)
        self.assertEqual(result.compression, None)

    def test__get_extract_job_config__csv_with_delimiter(self):
        self.extract.profile.format = const.FileFormat.CSV
        self.extract.profile.delimiter = ','

        result = self.extract._get_extract_job_config()

        self.assertEqual(result.destination_format, 'CSV')
        self.assertEqual(result.print_header, False)
        self.assertEqual(result.field_delimiter, ',')
        self.assertEqual(result.compression, None)

    def test__get_extract_job_config__csv_with_compress(self):
        self.extract.profile.format = const.FileFormat.CSV
        self.extract.profile.compress = True

        result = self.extract._get_extract_job_config()

        self.assertEqual(result.destination_format, 'CSV')
        self.assertEqual(result.print_header, False)
        self.assertEqual(result.field_delimiter, None)
        self.assertEqual(result.compression, 'GZIP')

    def test__get_extract_job_config__error_format(self):
        self.extract.profile.format = 'unknown'

        with self.assertRaises(ValueError):
            self.extract._get_extract_job_config()

    def test__get_query__daily(self):
        self.extract.profile.daily = '_daily'
        self.extract.profile.monthly = '_monthly'
        self.extract.inputs.mode = const.Mode.DAILY

        result = self.extract._get_query()

        self.assertEqual(result, '_daily')

    def test__get_query__monthly(self):
        self.extract.profile.daily = '_daily'
        self.extract.profile.monthly = '_monthly'
        self.extract.inputs.mode = const.Mode.MONTHLY

        result = self.extract._get_query()

        self.assertEqual(result, '_monthly')

    def test__get_query__historical(self):
        self.extract.profile.historical = '_historical'
        self.extract.profile.monthly = '_monthly'
        self.extract.inputs.mode = const.Mode.HISTORICAL

        result = self.extract._get_query()
        self.assertEqual(result, '_historical')

    def test__get_query__error(self):
        self.extract.profile.daily = '_daily'
        self.extract.profile.monthly = '_monthly'
        self.extract.inputs.mode = 'unknown_mode'

        with self.assertRaises(NotImplementedError):
            self.extract._get_query()

    def test__get_output_path(self):
        self.extract.inputs.mode = const.Mode.DAILY
        result = self.extract._get_output_path(gcs_path='gs://_gcs_path')

        self.assertEqual(result, 'gs://_gcs_path/_profile/2018/05')

    @patch.object(ExtractToGcs, ExtractToGcs._is_temp.__name__)
    @patch.object(ExtractToGcs, ExtractToGcs._get_date_format.__name__)
    @patch.object(ExtractToGcs, ExtractToGcs._get_output_path.__name__)
    def test__get_output_file_path_temp(self, _get_output_path, _get_date_format, is_temp):
        _get_output_path.return_value = 'gs://temp_bucket/profile/2018/05'
        _get_date_format.return_value = '%d%m%Y'
        self.extract.profile.format = 'csv'
        self.extract.profile.output_ext_format = '.txt.gz'
        self.extract.profile.output_file_format = '{profile}_{date_format}{file_extension}'
        is_temp.return_value = True
        result = self.extract._get_output_file_path(self.extract.inputs.gcs_path)
        self.assertEqual(result, 'gs://temp_bucket/profile/2018/05/_profile_01052018.csv')

    @patch.object(ExtractToGcs, ExtractToGcs._get_date_format.__name__)
    @patch.object(ExtractToGcs, ExtractToGcs._get_output_path.__name__)
    def test__get_output_file_path_non_temp(self, _get_output_path, _get_date_format):
        _get_output_path.return_value = 'gs://temp_bucket/profile/2018/05'
        _get_date_format.return_value = '%d%m%Y'
        self.extract.profile.output_file_format = '{profile}_{date_format}{file_extension}'
        self.extract.profile.format = 'csv'
        self.extract.profile.output_ext_format = '.txt.gz'
        result = self.extract._get_output_file_path(self.extract.inputs.gcs_path)
        self.assertEqual(result, 'gs://temp_bucket/profile/2018/05/_profile_01052018.txt.gz')

    def test__get_date_format(self):
        self.extract.profile.output_date_format = '%m%d%Y'

        result = self.extract._get_date_format()

        self.assertEqual(result, '%m%d%Y')

    def test__get_date_format__not_specific(self):
        self.extract.profile.output_date_format = None
        self.extract.inputs.mode = const.Mode.DAILY

        result = self.extract._get_date_format()

        self.assertEqual(result, '%Y%m%d')

    def test__check_is_temp_false(self):
        input_des = '_des'
        des_path = '_des'
        result = self.extract._is_temp(input_des=input_des, des_path=des_path)
        assert result is False

    def test__check_is_temp_true(self):
        input_des = '_des'
        des_path = '_temp_des'
        result = self.extract._is_temp(input_des=input_des, des_path=des_path)
        assert result is True

    @patch('dp_extract.extract_to_gcs.LoadFromGCS.download_gcs_temp_to_local')
    def test__load_from_gcs(self, download_gcs_temp_to_local):
        local_file = MagicMock()
        download_gcs_temp_to_local.return_value = local_file
        result = self.extract._load_from_gcs('gs://temp/out', ANY)
        assert download_gcs_temp_to_local.called
        self.assertEqual(result, local_file)

    @patch('dp_extract.extract_to_gcs.MailSender')
    @patch('dp_extract.extract_to_gcs.MailConfig')
    def test__send_mail(self, _mail_config, _mail_sender):
        mail_config = MagicMock()
        mail_sender = MagicMock()
        _mail_config.return_value = mail_config
        _mail_sender.return_value = mail_sender
        mail_config.load_config = MagicMock()
        mail_sender.execute = MagicMock()

        self.extract._send_mail(MagicMock, MagicMock)

        self.assertEqual(mail_config.load_config.call_count, 1)
        self.assertEqual(mail_sender.execute.call_count, 1)


    @patch.object(ExtractToGcs, ExtractToGcs.upload_to_gcs.__name__)
    @patch.object(ExtractToGcs, ExtractToGcs._get_output_path.__name__)
    @patch.object(ExtractToGcs, ExtractToGcs.create_additional_file.__name__)
    def test__upload_additional_file(self, create_additional_file, _get_output_path, upload_to_gcs):
        create_additional_file.return_value = '_temp_path/_temp_file.csv'
        _get_output_path.return_value = 'gs://_temp_bucket/_profile/2018/05'
        self.extract.upload_additional_file()
        assert upload_to_gcs.assert_called_once

    @patch('builtins.open')
    @patch.object(DirectoryUtil, DirectoryUtil.create_temp_dir.__name__)
    @patch.object(ExtractToGcs, ExtractToGcs._get_file_name.__name__)
    def test_create_additional_file(self, _get_file_name, create_temp_dir, open):
        const.TEMP_DIR = '_output'
        _get_file_name.return_value = 'temp.txt.gz.ctrl'
        self.extract.profile.additional_file_ext = '.txt.gz.ctrl'
        result = self.extract.create_additional_file()
        self.assertEqual('_output/temp.txt.gz.ctrl', result)
        _get_file_name.assert_called_once()
        create_temp_dir.assert_called_once()
        open.assert_called_once()

    @patch.object(ExtractToGcs, ExtractToGcs._get_date_format.__name__)
    def test_get_file_name(self, _get_date_format):
        _get_date_format.return_value = '%m%d%Y'

        result = self.extract._get_file_name('.txt.gz', '{profile}_{date_format}{file_extension}')
        self.assertEqual(result, '_profile_05012018.txt.gz')
        _get_date_format.assert_called_once()
