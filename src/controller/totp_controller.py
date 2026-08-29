from typing import TYPE_CHECKING

from src.controller.response import Response, ResponseType
from src.model.config.config_manager import ConfigManager
from src.model.logger.logger_manager import LoggerManager
from src.model.qr.qr_manager import QRManager
from src.model.storage.storage_manager import StorageManager
from src.model.totp.totp_manager import TOTPManager

if TYPE_CHECKING:
    from src.controller.master_controller import MasterController


class TOTPController:
    """
    Controller for totpScript.js
    """
    logger: LoggerManager
    config: ConfigManager
    master_controller: "MasterController"
    totp: TOTPManager
    qr: QRManager
    storage: StorageManager

    def __init__(self, master_controller: "MasterController"):
        """
        Storage can be loaded only after user password is provided.
        Class has to be initialized before user password available to register for JS API.
        Rest of the initialization in init_with_user_password.
        """
        self.logger = LoggerManager()
        self.config = ConfigManager()
        self.master_controller = master_controller
        self.totp = TOTPManager()
        self.qr = QRManager()

    def init(self, storage):
        """
        Lazy-loading storage.
        """
        self.storage = storage

    def get_info(self, name, secret=None) -> dict | None:
        """
        Internal method, since used both by get_info_handler and get_all_info_handler.
        """
        if secret is None:
            secret = self.storage.get_secret(name)
        if secret is None:
            return None

        current_code, next_code, expires_at, next_expires_at, interval = (self.totp.get_info(
            secret))
        return {
            "name": name,
            "current_code": current_code,
            "next_code": next_code,
            "expires_at": expires_at,
            "next_expires_at": next_expires_at,
            "interval": interval
        }

    def get_info_handler(self, name) -> ResponseType:
        self.logger.log_enter("get_info_handler")

        info = self.get_info(name)
        if info is None:
            return Response.error(f"TOTP code generation for {name} failed")

        return Response.success(f"Successfully generated TOTP code for {name}", self.get_info(name))

    def get_all_info_handler(self) -> ResponseType:
        self.logger.log_enter("get_all_info_handler")

        storage = self.storage.get_storage()
        all_info = []
        for (name, secret) in storage.items():
            info = self.get_info(name, secret)
            if info is None:
                self.logger.error(f"Failed to generate TOTP code for {name}")
                continue
            all_info.append(self.get_info(name))

        return Response.success("Successfully loaded TOTP codes", all_info)

    def add_secret_handler(self, secret: str, name: str) -> ResponseType:
        self.logger.log_enter("add_secret_handler")

        if not secret and not name:
            return Response.error("Name and secret cannot be empty.")

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

    def add_secret_qr_handler(self) -> ResponseType:
        self.logger.log_enter("add_secret_qr_handler")

        image_path = self.master_controller.open_image_dialog()
        if image_path is None:
            return Response.error("No image selected")

        uri = self.qr.decode(image_path)
        if uri is None:
            return Response.error("QR code image is invalid.")

        parsed_uri = self.totp.parse_provisioning_uri(uri)
        if parsed_uri is None:
            return Response.error("The provisioning URI (encoded by the QR code) is invalid.")
        secret, name = parsed_uri

        added = self.storage.add_secret(secret, name)
        if not added:
            return Response.error(f"Secret for {name} already exists.")

        return Response.success(f"Secret for {name} added successfully", self.get_info(name))

    def remove_secret_handler(self, name) -> ResponseType:
        self.logger.log_enter("remove_secret_handler")
        removed = self.storage.remove_secret(name)
        if not removed:
            return Response.error(f"Secret for {name} does not exist.")

        return Response.success(f"Secret for {name} removed successfully")
