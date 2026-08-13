from src.config.config_manager import ConfigManager
from src.hasher.argon2_hasher import Argon2Hasher
from src.logger.logger_manager import LoggerManager


class Hasher:
    """
    Picks the right hasher based on the configuration. The default is Argon2.
    """
    instance = None
    logger = LoggerManager()
    config = ConfigManager()

    def __new__(cls):
        if cls.instance is not None:
            return cls.instance

        cls.instance = Argon2Hasher()
        return cls.instance
