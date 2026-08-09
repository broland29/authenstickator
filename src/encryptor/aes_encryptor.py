from Crypto.Cipher import AES

from encryptor.abstract_encryptor import AbstractEncryptor


class AESEncryptor(AbstractEncryptor):

    def __init__(self, key: str):
        self.key = key

    def encrypt(self, plaintext: str) -> bytes:
        if not self.key:
            return plaintext.encode()

        cipher = AES.new(self.key.encode(), AES.MODE_EAX)
        ciphertext, tag = cipher.encrypt_and_digest(plaintext.encode())
        return cipher.nonce + tag + ciphertext

    def decrypt(self, ciphertext: bytes) -> str:
        if not self.key:
            return ciphertext.decode()

        nonce = ciphertext[:16]
        tag = ciphertext[16:32]
        actual_ciphertext = ciphertext[32:]

        cipher = AES.new(self.key.encode(), AES.MODE_EAX, nonce=nonce)
        return cipher.decrypt_and_verify(actual_ciphertext, tag).decode()
