from Crypto.Cipher import AES
from Crypto.Hash import SHA256
from Crypto.Protocol.KDF import PBKDF2

from src.config.config_manager import ConfigManager
from src.encryptor.abstract_encryptor import AbstractEncryptor
from src.logger.logger_manager import LoggerManager


class AESEncryptor(AbstractEncryptor):
    """
    Encrypts and decrypts data using AES algorithm.
    """
    logger = LoggerManager()
    config = ConfigManager()

    def __init__(self, user_password: str, salt: bytes):
        # With the help of the Password-Based Key Derivation Function 2, convert the key. The
        # result has 32 bytes, which is accepted by the AES algorithm. This way, user_password
        # may be of any length.
        self.key = PBKDF2(
            password=user_password,
            salt=salt,
            dkLen=32,
            count=100_000,
            hmac_hash_module=SHA256
        )

        self.logger.info("AESEncryptor initialized.")

    def encrypt(self, plaintext: str) -> bytes:
        cipher = AES.new(
            key=self.key,
            mode=AES.MODE_EAX
        )
        ciphertext, tag = cipher.encrypt_and_digest(plaintext.encode())
        return cipher.nonce + tag + ciphertext

    def decrypt(self, ciphertext: bytes) -> str:
        nonce = ciphertext[:16]
        tag = ciphertext[16:32]
        actual_ciphertext = ciphertext[32:]

        cipher = AES.new(
            self.key,
            AES.MODE_EAX,
            nonce=nonce
        )
        return cipher.decrypt_and_verify(actual_ciphertext, tag).decode()
