import json
import os
from typing import Final, TYPE_CHECKING

if TYPE_CHECKING:
    from src.logger.logger_manager import LoggerManager


class ConfigManager:
    """
    TODO: add validation of loaded config file, fallback to defaults in case of invalid values from config.json.
    """
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

    CONFIG_PATH: Final[str] = os.path.join(BASE_DIR, "config.json")

    DEFAULT_CONFIG: Final[dict] = {
        "webview": {
            "debug": True,
        },
        "logger": {
            "log_level": "INFO",
            "log_file": "log.txt"
        },
        "storage": {
            "storage_path": "storage.txt",
            "storage_encryptor": "none",
        }
    }

    instance = None

    def __new__(cls):
        if cls.instance is not None:
            return cls.instance

        instance = super().__new__(cls)

        if not os.path.exists(cls.CONFIG_PATH):
            print(f"Config file not found at {cls.CONFIG_PATH}, creating default config.")
            with open(cls.CONFIG_PATH, "w") as file:
                file.write(json.dumps(cls.DEFAULT_CONFIG, indent=4))

        with open(cls.CONFIG_PATH, "r") as file:
            instance.config = json.load(file)

        cls.instance = instance
        return instance

    def log_config(self, logger: "LoggerManager"):
        """
        Need to inject logger, otherwise circular import.
        """
        logger.info(f"Loaded config: {self.config}")

    def get(self, config: str):
        keys = config.split(".")
        value = self.config

        for key in keys:
            if key not in value:
                print(f"Key {key} not found in config.")
                return None
            value = value[key]
        return value
