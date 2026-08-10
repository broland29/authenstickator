from src.encryptor.abstract_encryptor import AbstractEncryptor
from src.logger.logger_manager import LoggerManager


class NoEncryptor(AbstractEncryptor):
    """
    Encryptor that does nothing but encode and decode the plaintext.
    """
    logger = LoggerManager()

    def __init__(self):
        self.logger.info("NoEncryptor initialized.")

    def encrypt(self, plaintext: str) -> bytes:
        return plaintext.encode()

    def decrypt(self, ciphertext: bytes) -> str:
        return ciphertext.decode()
