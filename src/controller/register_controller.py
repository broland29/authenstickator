from typing import TYPE_CHECKING

from src.controller.errors import Errors
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

        # If there is a leftover storage.txt at the moment of registration, there are two cases:
        #   1. The provided new password combined with the salt matches the old key, in which case,
        #       execution continues like nothing happened. This is desired, since the password is
        #       actually correct, and blocking decryption just because the hashed file is missing
        #       would mean an artificial lockout.
        #   2. The provided new password combined with the salt does not match the old key,
        #       in which case, execution stops with an error suggesting that decryption of the
        #       storage failed. While this error message is not 100% intuitive, it points to the
        #       source of the error: a leftover storage file. Wiping the leftover storage file is
        #       not ok, since the user might "remember" the correct password later, so it is up
        #       to the user to move the file away or delete it.

        result = self.master_controller.init_with_user_password(user_password)
        if result["status"] != Response.STATUS_SUCCESS:
            if result["error_message"] == Errors.ERROR_DECRYPT:
                storage_file_path = self.config.get("storage.storage_file_path")
                return Response.error(
                    f"Previous storage file was found at {storage_file_path}. You can either "
                    f"provide the password it used, or move the storage file to a new location, "
                    f"and try again.")
            return result

        return Response.success("Password is valid", ViewPath.TOTP)
