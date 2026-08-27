import logging
from logging.handlers import RotatingFileHandler
from typing import Final

from src.config.config_manager import ConfigManager


class LoggerManager:
    """
    Singleton logger for the whole app.
    """
    CONSOLE_HANDLER_NAME: Final[str] = "console"
    FILE_HANDLER_NAME: Final[str] = "file"
    instance = None

    def __new__(cls):
        if cls.instance is not None:
            return cls.instance

        cls.instance = super().__new__(cls)

        # In some cases (ex: in tests where singleton is cleared to None), the instance is none but
        # the handlers are in place from previous initialization.
        logger = logging.getLogger()
        existing_handler_names = {handler.name for handler in logger.handlers}
        if {cls.CONSOLE_HANDLER_NAME, cls.FILE_HANDLER_NAME}.issubset(existing_handler_names):
            cls.instance.logger = logger
            return cls.instance

        config = ConfigManager()
        log_level = config.get("logger.log_level")
        log_file_path = config.get("logger.log_file_path")

        logger.setLevel(log_level)

        formatter = logging.Formatter(
            "[%(asctime)s] [%(levelname).1s] [%(filename)s:%(lineno)d] [%(name)s] %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )

        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        console_handler.set_name(cls.CONSOLE_HANDLER_NAME)
        logger.addHandler(console_handler)

        file_handler = RotatingFileHandler(log_file_path, maxBytes=1044 * 1024)
        file_handler.setFormatter(formatter)
        file_handler.set_name(cls.FILE_HANDLER_NAME)
        logger.addHandler(file_handler)

        logger.info("Logger configured. Starting the application.")

        logger.info("\n"
                    """
┌─┐╷ ╷╶┬╴╷ ╷┌─╴┌┐╷┌─┐╶┬╴╷┌─╴╷┌ ┌─┐╶┬╴┌─┐┌─┐
├─┤│ │ │ ├─┤├╴ │└┤└─┐ │ ││  ├┴┐├─┤ │ │ │├┬┘
╵ ╵└─┘ ╵ ╵ ╵└─╴╵ ╵└─┘ ╵ ╵└─╴╵ ╵╵ ╵ ╵ └─┘╵└╴
                    """)

        cls.instance.logger = logger
        return cls.instance

    @staticmethod
    def disable_pywebview_logger():
        """
        pywebview has its own logger; without the following lines, logs will be duplicated (if
        pywebview runs in debug mode).
        """
        pywebview_logger = logging.getLogger("pywebview")
        pywebview_logger.handlers.clear()
        pywebview_logger.propagate = True

    def debug(self, msg):
        self.logger.debug(msg, stacklevel=2)

    def info(self, msg):
        self.logger.info(msg, stacklevel=2)

    def warning(self, msg):
        self.logger.warning(msg, stacklevel=2)

    def error(self, msg):
        self.logger.error(msg, stacklevel=2)

    def log_enter(self, method_name: str):
        self.logger.debug(f"Entered {method_name}", stacklevel=2)
