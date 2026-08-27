from typing import TYPE_CHECKING

from src.config.config_manager import ConfigManager
from src.encryptor.abstract_encryptor import AbstractEncryptor
from src.encryptor.encryptor import Encryptor
from src.logger.logger_manager import LoggerManager
from src.password.password_manager import PasswordManager
from src.storage.storage_manager import StorageManager
from src.tpm.abstract_tpm import AbstractTPM
from src.tpm.tpm import TPM
from src.ui.controller.response import Response
from src.ui.controller.response import ResponseType

if TYPE_CHECKING:
    from src.ui.controller.master_controller import MasterController


class ChangePasswordController:
    """
    Controller for changePasswordScript.js
    """
    logger: LoggerManager
    config: ConfigManager
    master_controller: "MasterController"
    password: PasswordManager
    tpm: AbstractTPM
    encryptor: AbstractEncryptor
    storage: StorageManager

    def __init__(self, master_controller: "MasterController"):
        """
        Storage and encryptor can be loaded only after user password is provided.
        Class has to be initialized before user password available to register for JS API.
        Rest of the initialization in init_with_user_password.
        """
        self.logger = LoggerManager()
        self.config = ConfigManager()
        self.master_controller = master_controller
        self.password = PasswordManager()
        self.tpm = TPM()

    def init_with_user_password(self, user_password: str):
        """
        Lazy-loading storage and encryptor.
        """
        self.storage = StorageManager(user_password)
        self.encryptor = Encryptor(user_password, self.tpm.get_secret())

    def change_password_handler(self, old_password: str, new_password: str) -> ResponseType:
        self.logger.log_enter("verify_password_handler")

        if not self.password.password_matches(old_password):
            return Response.error("Old password is incorrect. Try again.")

        if not self.password.set_password(new_password):
            return Response.error(
                f"New password is not acceptable. It shall between "
                f"{self.password.min_length} and {self.password.max_length} characters.")

        # Encryptor instance has to be changed, since encryption key changed.
        self.encryptor.reinit(new_password, self.tpm.get_secret())

        # The storage has to be re-encrypted, since encryption key changed.
        self.storage.save()

        return Response.success("Password changed successfully.")
