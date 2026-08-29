from pathlib import Path

from src.model.config.config_manager import ConfigManager
from src.model.encryptor.encryptor import Encryptor
from src.model.hasher.hasher import Hasher
from src.model.logger.logger_manager import LoggerManager
from src.model.password.password_manager import PasswordManager
from src.model.qr.qr_manager import QRManager
from src.model.storage.storage_manager import StorageManager
from src.model.totp.totp_manager import TOTPManager
from src.model.tpm.tpm import TPM


class TestUtils:
    """
    Methods which can be used both by conftest and test files. Workaround since fixtures of
    conftest cannot be called explicitly by test methods, and it is desired in some cases,
    for example, when simulating a new session.
    """

    @staticmethod
    def encryptor():
        user_password = "DummyPassword"
        salt = ("A" * 16).encode()
        return Encryptor(user_password, salt)

    @staticmethod
    def storage() -> StorageManager:
        return StorageManager(TestUtils.encryptor())

    @staticmethod
    def cleanup_session():
        TestUtils.cleanup_singletons()
        TestUtils.cleanup_storage()

    @staticmethod
    def cleanup_singletons():
        """
        Clears all singleton instances. Pytest runs parametrized tests in one session, and without
        explicit clearing, singleton instances are persisted from one run to another.

        This method only works if imports here are identical to imports in the code (i.e. absolute).
        """
        singletons = [ConfigManager, Encryptor, Hasher, LoggerManager, PasswordManager, QRManager,
                      StorageManager, TOTPManager, TPM]

        for singleton in singletons:
            singleton.instance = None

    @staticmethod
    def cleanup_storage():
        """
        Deletes the (test) storage file. Shall be called after config is stubbed, so that the right
        storage file path comes from config.get.
        """
        config = ConfigManager()
        try:
            storage_file_path = Path(config.get("storage.storage_file_path"))
            storage_file_path.unlink(missing_ok=True)
        except KeyError:
            return  # No storage file path specified in config => no storage file to clean up.
