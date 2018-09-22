import base64

import googleapiclient.discovery


class KmsManagement:
    def __init__(self, kms_path: str):
        self.kms_path = kms_path
        kms_client = googleapiclient.discovery.build('cloudkms', 'v1')
        # self.name = self.kms_path
        self.crypto_keys = kms_client.projects().locations().keyRings().cryptoKeys()

    def decrypted_local_password(self, ciphertext: bytes) -> bytes:
        request = self.crypto_keys.decrypt(
            name=self.kms_path,
            body={'ciphertext': base64.b64encode(ciphertext).decode('ascii')})

        return self._execute_request(request=request, mode='plaintext')

    def encrypt_password_with_kms(self, plaintext: bytes) -> bytes:
        request = self.crypto_keys.encrypt(
            name=self.kms_path,
            body={'plaintext': base64.b64encode(plaintext).decode('ascii')})

        return self._execute_request(request=request, mode='ciphertext')

    def _execute_request(self, request, mode: str) -> bytes:
        response = request.execute()
        return base64.b64decode(response[mode].encode('ascii'))
