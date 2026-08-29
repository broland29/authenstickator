from typing_extensions import override

from src.model.logger.logger_manager import LoggerManager
from src.model.tpm.abstract_tpm import AbstractTPM


class NoTPM(AbstractTPM):
    """
    TPM class that returns a hardcoded secret without actually using the TPM. To be used when the
    configs opt out of TPM usage.
    """
    logger: LoggerManager

    def __init__(self):
        self.logger = LoggerManager()
        self.logger.info("NoTPM initialized")

    @override
    def setup_secret(self) -> bytes | None:
        return b"A" * 16

    @override
    def get_secret(self) -> bytes | None:
        return b"A" * 16
