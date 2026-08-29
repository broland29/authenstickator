import platform

from src.model.config.config_manager import ConfigManager
from src.model.logger.logger_manager import LoggerManager
from src.model.tpm.abstract_tpm import AbstractTPM
from src.model.tpm.no_tpm import NoTPM
from src.model.tpm.windows_tpm import WindowsTPM


class TPM:
    """
    Picks the right TPM class based on the current platform and the config file.
    """
    instance: AbstractTPM = None

    def __new__(cls):
        """
        TPM initialization. Returns None if TPM raises exception.
        """
        config = ConfigManager()
        logger = LoggerManager()

        if cls.instance is not None:
            return cls.instance

        if not config.get("tpm.enabled"):
            cls.instance = NoTPM()
            return cls.instance

        os_name = platform.system()
        if os_name == "Linux":
            # Imports for Linux only. Avoid putting them in areas where it runs on other platforms.
            from src.model.tpm.linux_tpm import LinuxTPM
            from tpm2_pytss import TSS2_Exception
            try:
                cls.instance = LinuxTPM()
            except TSS2_Exception as e:
                logger.error(f"FAPI threw exception {e}.")
                return None
            return cls.instance

        if os_name == "Windows":
            cls.instance = WindowsTPM()
            return cls.instance

        logger.error(f"TPM not implemented for OS {os_name}, continuing without TPM")
        cls.instance = NoTPM()
        return cls.instance
