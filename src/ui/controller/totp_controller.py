from typing import TYPE_CHECKING

from src.logger.logger_manager import LoggerManager
from src.qr.qr_manager import QRManager
from src.storage.storage_manager import StorageManager
from src.totp.totp_manager import TOTPManager
from src.ui.controller.response import Response

if TYPE_CHECKING:
    from src.ui.controller.master_controller import MasterController


class TOTPController:
    """
    We have a lazy-loading like initialization (with method init), since:
    - at startup we need to register the controller (for the API)
    - but full initialization can be done only with user password provided
    """
    logger = LoggerManager()

    def __init__(self, master_controller: "MasterController"):
        self.master_controller = master_controller
        self.totp = TOTPManager()
        self.qr = QRManager()
        self.storage = None

    def init(self, user_password: str):
        self.setup_storage_manager(user_password)

    def setup_storage_manager(self, user_password: str):
        self.storage = StorageManager(user_password)

    def get_info(self, name, secret=None) -> dict | None:
        """
        Internal method, since used by get_info_handler and get_all_info_handler as well.
        """
        if secret is None:
            secret = self.storage.get_secret(name)
        if secret is None:
            return None

        current_code, next_code, expires_at, next_expires_at = (self.totp.get_info(secret))
        return {
            "name": name,
            "current_code": current_code,
            "next_code": next_code,
            "expires_at": expires_at,
            "next_expires_at": next_expires_at
        }

    def get_info_handler(self, name) -> dict:
        self.logger.log_enter("get_info_handler")

        info = self.get_info(name)
        if info is None:
            return Response.error(f"TOTP code generation for {name} failed")

        return Response.success(f"Successfully generated TOTP code for {name}", self.get_info(name))

    def get_all_info_handler(self) -> list[dict]:
        self.logger.log_enter("get_all_info_handler")

        storage = self.storage.get_storage()
        all_info = []
        for (name, secret) in storage.items():
            info = self.get_info(name, secret)
            if info is None:
                # TODO: Response.warning? one/more TOTP code generation fails, but i do not want
                #  to halt the rest.
                self.logger.error(f"Failed to generate TOTP code for {name}")
                continue
            all_info.append(self.get_info(name))

        return Response.success("Successfully loaded TOTP codes", all_info)

    def add_secret_handler(self, secret: str, name: str):
        self.logger.log_enter("add_secret_handler")

        if not secret:
            return Response.error("Secret cannot be empty.")

        if not name:
            return Response.error("Name cannot be empty.")

        secret = self.totp.parse_secret(secret)
        if secret is None:
            return Response.error("Secret is invalid.")

        added = self.storage.add_secret(secret, name)
        if not added:
            return Response.error(f"Secret for {name} already exists.")

        return Response.success(f"Secret for {name} added successfully", self.get_info(name))

    def add_secret_qr_handler(self):
        self.logger.log_enter("add_secret_qr_handler")

        image_path = self.master_controller.open_image_dialog()
        if image_path is None:
            return Response.error("No image selected")

        uri = self.qr.decode(image_path)
        if uri is None:
            return Response.error("QR code image is invalid.")

        secret, name = self.totp.parse_provisioning_uri(uri)
        if secret is None or name is None:
            return Response.error("Secret is invalid.")

        added = self.storage.add_secret(secret, name)
        if not added:
            return Response.error(f"Secret for {name} already exists.")

        return Response.success(f"Secret for {name} added successfully", self.get_info(name))

    def remove_secret_handler(self, name):
        self.logger.log_enter("remove_secret_handler")
        removed = self.storage.remove_secret(name)
        if not removed:
            return Response.error(f"Secret for {name} does not exist.")

        return Response.success(f"Secret for {name} removed successfully")
