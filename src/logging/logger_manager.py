import logging
from logging.handlers import RotatingFileHandler

from src.config.config_manager import ConfigManager

"""
Singleton logger for the whole app. Usual levels: INFO, WARNING, ERROR.
"""
class LoggerManager:
    instance = None

    def __new__(cls):
        if cls.instance is not None:
            return cls.instance

        config = ConfigManager()
        log_level = config.get("logging.log_level")
        log_file_path = config.get("logging.log_file_path")

        logger = logging.getLogger()
        logger.setLevel(log_level)

        formatter = logging.Formatter(
            "[%(asctime)s] [%(levelname).1s] [%(name)s] %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )

        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

        file_handler = RotatingFileHandler(log_file_path, maxBytes = 1044 * 1024)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

        # Pywebview has its own logger; without the following lines, logs will be duplicated (if pywebview runs in debug mode).
        pywebview_logger = logging.getLogger("pywebview")
        pywebview_logger.handlers.clear()
        pywebview_logger.propagate = True

        logger.info("Logger configured. Starting the application. ^.^")

        cls.instance = logger
        return logger
