from typing import override

from logger.logger_manager import LoggerManager
from src.tpm.abstract_tpm import AbstractTPM


class WindowsTPM(AbstractTPM):
    """
    TPM on Windows is currently not supported. Identical behavior to NoTPM.
    """
    logger: LoggerManager

    def __init__(self):
        self.logger = LoggerManager()
        self.logger.info("No TPM initialized")

    @override
    def setup_secret(self) -> None:
        pass

    @override
    def get_secret(self) -> bytes:
        return b"A" * 16
