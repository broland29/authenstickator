from typing import TYPE_CHECKING

from controller.response import Response
from controller.response import ResponseType
from model.config.config_manager import ConfigManager
from model.encryptor.abstract_encryptor import AbstractEncryptor
from model.encryptor.encryptor import Encryptor
from model.logger.logger_manager import LoggerManager
from model.password.password_manager import PasswordManager
from model.storage.storage_manager import StorageManager
from model.tpm.abstract_tpm import AbstractTPM
from model.tpm.tpm import TPM

if TYPE_CHECKING:
    from controller.master_controller import MasterController


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

        # Encryptor instance has to be changed, since encryption key changed.
        self.encryptor.reinit(new_password, self.tpm.get_secret())

        # The storage has to be re-encrypted, since encryption key changed.
        self.storage.save()

        return Response.success("Password changed successfully.")
