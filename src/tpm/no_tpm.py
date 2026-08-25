from typing_extensions import override

from src.logger.logger_manager import LoggerManager
from src.tpm.abstract_tpm import AbstractTPM


class NoTPM(AbstractTPM):
    """
    TPM class that does nothing but encode and decode the plaintext.
    """
    logger = LoggerManager()

    def __init__(self):
        self.logger.info("No TPM initialized")

    @override
    def setup_secret(self) -> None:
        pass

    @override
    def get_secret(self) -> bytes:
        return b"A" * 16
