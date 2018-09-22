import base64
import unittest
from unittest.mock import MagicMock, patch

from dp_extract.utils.kms_management import KmsManagement


class TestKmsManagement(unittest.TestCase):
    def setUp(self):
        self.kms_path = '_kms_path'
        self.password = 'password'
        self.byte_password = self.password.encode()

        self.patcher = patch('googleapiclient.discovery')
        google_client = self.patcher.start()
        kms_client = MagicMock()
        projects = MagicMock()
        locations = MagicMock()
        keyRings = MagicMock()

        google_client.build.return_value = kms_client
        kms_client.projects.return_value = projects
        projects.locations.return_value = locations
        locations.keyRings.return_value = keyRings
        keyRings.cryptoKeys.return_value = MagicMock()

        self.kms_management = KmsManagement(kms_path=self.kms_path)

    @patch.object(KmsManagement, KmsManagement._execute_request.__name__)
    def test_decrypted_local_password(self, execute_request):
        request = MagicMock()
        self.kms_management.crypto_keys.decrypt.return_value = request
        self.kms_management.decrypted_local_password(str.encode('password'))
        execute_request.assert_called_once()
        self.kms_management.crypto_keys.decrypt.assert_called_once()

    @patch.object(KmsManagement, KmsManagement._execute_request.__name__)
    def test_encrypt_local_password(self, execute_request):
        request = MagicMock()
        self.kms_management.crypto_keys.encrypt.return_value = request
        self.kms_management.encrypt_password_with_kms(str.encode('password'))
        execute_request.assert_called_once()
        self.kms_management.crypto_keys.encrypt.assert_called_once()


    def test__execute_request(self):
        mode = 'plaintext'
        request = MagicMock()
        response = MagicMock()
        request.execute.return_value = response
        response[mode].encode.return_value = 'password'
        result_password = self.kms_management._execute_request(request=request, mode=mode)
        self.assertEqual(result_password, base64.b64decode('password'))


    def tearDown(self):
        self.patcher.stop()