from typing import TYPE_CHECKING

from src.config.config_manager import ConfigManager
from src.logger.logger_manager import LoggerManager
from src.password.password_manager import PasswordManager
from src.ui.controller.response import Response
from src.ui.controller.view import View

if TYPE_CHECKING:
    from src.ui.controller.master_controller import MasterController


class RegisterController:
    logger: LoggerManager
    config: ConfigManager
    master_controller: "MasterController"
    password: PasswordManager

    def __init__(self, master_controller: "MasterController"):
        self.logger = LoggerManager()
        self.config = ConfigManager()
        self.master_controller = master_controller
        self.password = PasswordManager()

    def new_password_handler(self, user_password):
        if not self.password.set_password(user_password):
            return Response.error("Password is not complex enough")

        self.master_controller.init_with_user_password(user_password)
        return Response.success("Password is valid", View.TOTP.value)
