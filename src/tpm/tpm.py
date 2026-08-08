import platform

from src.logging.logger_manager import LoggerManager
from src.tpm.linux_tpm import LinuxTPM

"""
Picks the right TPM interface for the current platform.
"""
class TPM:
    instance = None
    logger = LoggerManager()

    def __new__(cls):
        if cls.instance is not None:
            return cls.instance

        os_name = platform.system()
        if os_name == "Linux":
            cls.instance = LinuxTPM()
        else:
            cls.logger.log_error(f"TPM not implemented for OS {os_name}, continuing without TPM")

        return cls.instance
