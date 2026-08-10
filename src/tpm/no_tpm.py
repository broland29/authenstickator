from src.logger.logger_manager import LoggerManager
from src.tpm.abstract_tpm import AbstractTPM


class NoTPM(AbstractTPM):
    """
    TPM class that does nothing but encode and decode the plaintext.
    """
    logger = LoggerManager()

    def __init__(self):
        self.logger.info("No TPM initialized")

    def encrypt(self, plaintext: str) -> bytes:
        return plaintext.encode()

    def decrypt(self, ciphertext: bytes) -> str:
        return ciphertext.decode()
