from typing import TYPE_CHECKING

from src.config.config_manager import ConfigManager
from src.hasher.hasher import Hasher
from src.logger.logger_manager import LoggerManager
from src.ui.controller.response import Response
from src.ui.controller.view import View

if TYPE_CHECKING:
    from src.ui.controller.master_controller import MasterController


class LoginController:
    logger = LoggerManager()
    config = ConfigManager()

    def __init__(self, master_controller: "MasterController"):
        self.master_controller = master_controller

    def verify_password_handler(self, user_password):
        self.logger.debug("Entered verify_password_handler")
        path = self.config.get("storage.hashed_user_password_file_path")
        with open(path, "r") as file:
            hashed_password = file.read()
            hasher = Hasher()
            if not hasher.verify(user_password, hashed_password):
                return Response.error("Password is incorrect. Try again.")

        self.master_controller.init_totp_controller(user_password)
        return Response.success("Password is correct.", View.TOTP.value)
