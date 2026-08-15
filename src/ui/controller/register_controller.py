from typing import TYPE_CHECKING

from src.config.config_manager import ConfigManager
from src.hasher.hasher import Hasher
from src.logger.logger_manager import LoggerManager
from src.ui.controller.response import Response
from src.ui.controller.view import View

if TYPE_CHECKING:
    from src.ui.controller.master_controller import MasterController


class RegisterController:
    logger = LoggerManager()
    config = ConfigManager()

    def __init__(self, master_controller: "MasterController"):
        self.master_controller = master_controller
        self.hasher = Hasher()

    def new_password_handler(self, user_password):
        self.logger.log_enter("new_password_handler")
        if not self.is_password_complex_enough(user_password):
            return Response.error("Password is not complex enough")

        # Password is ok, save hash for next sessions.
        path = self.config.get("storage.hashed_user_password_file_path")
        with open(path, "w") as file:
            hasher = Hasher()
            hashed_password = hasher.hash(user_password)
            file.write(hashed_password)

        self.master_controller.init_totp_controller(user_password)
        return Response.success("Password is valid", View.TOTP.value)

    @staticmethod
    def is_password_complex_enough(password):
        # TODO: add password complexity check.
        return len(password) > 1
