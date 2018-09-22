from base64 import b64encode, b64decode

from Crypto.Cipher import AES
from Crypto.Hash import SHA256
from Crypto.Util.Padding import pad, unpad


class AesManagement:
    BLOCK_SIZE = 16

    def __init__(self, key_str: str, fullpath_filename: str, iv_str: str):
        self.key_str = key_str
        self.fullpath_filename = fullpath_filename
        self.iv_bytes = bytes(iv_str,'utf-8')

        self.hash_key = SHA256.new()
        self.hash_key.update(self.key_str.encode())

    def encrypt_file(self, encrypted_filename: str):
        with open(self.fullpath_filename, 'rb') as in_file:
            contents = in_file.read()

        padded_dat = pad(contents, AES.block_size)
        cipher = AES.new(self.hash_key.digest(), AES.MODE_CBC, self.iv_bytes)

        ct_bytes = cipher.encrypt(padded_dat)
        ct = b64encode(ct_bytes).decode('utf-8')

        with open(encrypted_filename, 'wt') as enc_file:
            enc_file.write(ct)

    def decrypt_file(self, decrypt_filename: str):
        with open(decrypt_filename, 'rt') as input_file:
            content = input_file.read()

        ct = b64decode(content)
        cipher = AES.new(self.hash_key.digest(), AES.MODE_CBC,self.iv_bytes)
        pt = unpad(cipher.decrypt(ct), AES.block_size)
        with open(decrypt_filename, 'wb') as decrypt_file:
            decrypt_file.write(pt)






















