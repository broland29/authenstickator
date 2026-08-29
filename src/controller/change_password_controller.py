from typing import TYPE_CHECKING

from src.controller.response import Response
from src.controller.response import ResponseType
from src.model.config.config_manager import ConfigManager
from src.model.logger.logger_manager import LoggerManager
from src.model.password.password_manager import PasswordManager

if TYPE_CHECKING:
    from src.controller.master_controller import MasterController


class ChangePasswordController:
    """
    Controller for changePasswordScript.js
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

    def change_password_handler(self, old_password: str, new_password: str) -> ResponseType:
        self.logger.log_enter("verify_password_handler")

        if not old_password and not new_password:
            return Response.error("Old and new password cannot be empty.")

        if not old_password:
            return Response.error("Old password cannot be empty.")

        if not new_password:
            return Response.error("New password cannot be empty.")

        if not self.password.password_matches(old_password):
            return Response.error("Old password is incorrect. Try again.")

        if not self.password.set_password(new_password):
            return Response.error(
                f"New password is not acceptable. It shall have between "
                f"{self.password.min_length} and {self.password.max_length} characters.")

        result = self.master_controller.init_with_user_password(new_password)
        if result["status"] != Response.STATUS_SUCCESS:
            return result

        return Response.success("Password changed successfully.")
