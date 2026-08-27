from src.config.config_manager import ConfigManager
from src.encryptor.encryptor import Encryptor
from src.hasher.hasher import Hasher
from src.logger.logger_manager import LoggerManager
from src.password.password_manager import PasswordManager
from src.qr.qr_manager import QRManager
from src.storage.storage_manager import StorageManager
from src.totp.totp_manager import TOTPManager
from src.tpm.tpm import TPM


class TestUtils:
    @staticmethod
    def cleanup_singletons():
        """
        Clears all singleton instances. Pytest runs parametrized tests in one session, and without
        explicit clearing, singleton instances are persisted from one run to another.

        This method only works if imports here are identical to imports in the code (i.e. absolute).

        Extracted as a util method so that it can be used in fixtures and also called explicitly in
        tests to simulate a new run of the application.
        """
        singletons = [ConfigManager, Encryptor, Hasher, LoggerManager, PasswordManager, QRManager,
                      StorageManager, TOTPManager, TPM]

        for singleton in singletons:
            singleton.instance = None
