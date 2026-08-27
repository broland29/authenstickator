import platform

from src.config.config_manager import ConfigManager
from src.logger.logger_manager import LoggerManager
from src.tpm.abstract_tpm import AbstractTPM
from src.tpm.linux_tpm import LinuxTPM
from src.tpm.no_tpm import NoTPM


class TPM:
    """
    Picks the right TPM class based on the current platform and the config file.
    """
    instance: AbstractTPM = None
    logger = LoggerManager()

    def __new__(cls):
        config = ConfigManager()

        if cls.instance is not None:
            return cls.instance

        if not config.get("tpm.enabled"):
            cls.instance = NoTPM()
            return cls.instance

        os_name = platform.system()
        if os_name == "Linux":
            cls.instance = LinuxTPM()
            return cls.instance

        cls.logger.log_error(f"TPM not implemented for OS {os_name}, continuing without TPM")
        cls.instance = NoTPM()
        return cls.instance
