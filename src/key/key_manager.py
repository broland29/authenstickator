from src.config.config_manager import ConfigManager
from src.logger.logger_manager import LoggerManager
from src.tpm.tpm import TPM


class KeyManager:
    instance = None
    logger = LoggerManager()
    config = ConfigManager()

    def __new__(cls):
        if cls.instance is not None:
            return cls.instance

        instance = super().__new__(cls)

        instance.tpm = TPM()

        cls.instance = instance
        return cls.instance

    def read_hashed_key(self) -> str | None:
        """
        Returns the hashed key if it exists, otherwise None.
        """
        try:
            with open(self.config.get("storage.key_file_path"), "r") as file:
                content = file.read()
                return content if content.strip() else None
        except FileNotFoundError:
            return None

    def store_hashed_key(self, hashed_key: str):
        """
        Stores the hashed key.
        """
        with open(self.config.get("storage.key_file_path"), "w") as file:
            file.write(self.config.get("storage.key"))
