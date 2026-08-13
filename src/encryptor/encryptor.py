from src.config.config_manager import ConfigManager
from src.encryptor.aes_encryptor import AESEncryptor
from src.encryptor.no_encryptor import NoEncryptor
from src.logger.logger_manager import LoggerManager


class Encryptor:
    """
    Picks the right encryptor based on the config file. Default is NoEncryptor.

    TODO: ask for encryption_key as user input.
    """
    instance = None
    logger = LoggerManager()

    def __new__(cls, key: bytes):
        """
        The key is bytes, since it might come from TPM encryption. PDKDF2 accepts bytes as input, for example.
        """
        if cls.instance is not None:
            return cls.instance

        config = ConfigManager()
        encryptor_type = config.get("encryptor.type")
        encryptor_enabled = config.get("encryptor.enabled")

        if not encryptor_enabled:
            cls.instance = NoEncryptor()
            return cls.instance

        if encryptor_type == "AES":
            cls.instance = AESEncryptor(key)
            return cls.instance

        cls.logger.info(f"Invalid encryptor type {encryptor_type}. Defaulting to AES.")
        cls.instance = AESEncryptor(key)
        return cls.instance
