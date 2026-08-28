from typing_extensions import override

from model.logger.logger_manager import LoggerManager
from model.tpm.abstract_tpm import AbstractTPM


class WindowsTPM(AbstractTPM):
    """
    TPM on Windows is (currently) not supported. Identical behavior to NoTPM.
    """
    logger: LoggerManager

    def __init__(self):
        self.logger = LoggerManager()
        self.logger.warning("TPM on Windows is not supported. Identical behavior to NoTPM.")
        self.logger.info("WindowsTPM initialized.")

    @override
    def setup_secret(self) -> None:
        pass

    @override
    def get_secret(self) -> bytes:
        return b"A" * 16
