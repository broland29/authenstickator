import json
from pathlib import Path
from typing import Final, TYPE_CHECKING

if TYPE_CHECKING:
    from src.logger.logger_manager import LoggerManager


class ConfigManager:
    # The config file path is hardcoded.
    BASE_DIR: Final[Path] = Path(__file__).parent
    CONFIG_FILE_PATH: Final[Path] = BASE_DIR / "config.json"
    LOCAL_CONFIG_FILE_PATH: Final[Path] = BASE_DIR / "config-local.json"

    instance = None
    config_file_path: Path = None

    def __new__(cls):
        if cls.instance is not None:
            return cls.instance

        instance = super().__new__(cls)

        if cls.LOCAL_CONFIG_FILE_PATH.exists():
            cls.config_file_path = cls.LOCAL_CONFIG_FILE_PATH
        elif cls.CONFIG_FILE_PATH.exists():
            cls.config_file_path = cls.CONFIG_FILE_PATH
        else:
            raise FileNotFoundError(f"No config file found! Searched at"
                                    f" {cls.LOCAL_CONFIG_FILE_PATH} and {cls.CONFIG_FILE_PATH}")

        with open(cls.config_file_path, "r") as file:
            instance.config = json.load(file)

        cls.instance = instance
        return instance

    def log_config(self, logger: "LoggerManager"):
        """
        Logger needs config, so config cannot require logger (circular import). Instead,
        pass logger as argument here, and raise clear exceptions if configs not found.
        """
        logger.info(f"Loaded config from {self.config_file_path}: {self.config}")

    def get(self, config: str):
        keys = config.split(".")
        value = self.config

        for key in keys:
            if key not in value:
                raise KeyError(f"Config {config} not found. Consider adding it to "
                               f"{self.config_file_path} with an appropriate value.")
            value = value[key]
        return value
