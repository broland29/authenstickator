from typing import TYPE_CHECKING

from src.controller.response import Response, ResponseType
from src.controller.view_path import ViewPath
from src.model.config.config_manager import ConfigManager
from src.model.logger.logger_manager import LoggerManager
from src.model.password.password_manager import PasswordManager

if TYPE_CHECKING:
    from src.controller.master_controller import MasterController


class RegisterController:
    """
    Controller for registerScript.js
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

    def new_password_handler(self, user_password) -> ResponseType:
        self.logger.log_enter("new_password_handler")

        if not user_password:
            return Response.error("New password cannot be empty.")

        if not self.password.set_password(user_password):
            return Response.error(
                f"New password is not acceptable. It shall have between "
                f"{self.password.min_length} and {self.password.max_length} characters.")

        result = self.master_controller.init_with_user_password(user_password)
        if result["status"] == Response.STATUS_ERROR:
            return result
        
        return Response.success("Password is valid", ViewPath.TOTP)
