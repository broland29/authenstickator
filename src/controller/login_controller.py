from typing import TYPE_CHECKING

from controller.response import Response, ResponseType
from controller.view_path import ViewPath
from model.config.config_manager import ConfigManager
from model.logger.logger_manager import LoggerManager
from model.password.password_manager import PasswordManager

if TYPE_CHECKING:
    from controller.master_controller import MasterController


class LoginController:
    """
    Controller for loginScript.js
    """
    logger: LoggerManager
    config: ConfigManager
    master_controller: "MasterController"
    password: PasswordManager

    def __init__(self, master_controller: "MasterController"):
        self.logger = LoggerManager()
        self.config = ConfigManager()
        self.master_controller = master_controller
        self.password = PasswordManager()

    def verify_password_handler(self, user_password) -> ResponseType:
        self.logger.log_enter("verify_password_handler")

        if not user_password or not self.password.password_matches(user_password):
            return Response.error("Password is incorrect. Try again.")

        self.master_controller.init_with_user_password(user_password)
        return Response.success("Password is correct.", ViewPath.TOTP)
