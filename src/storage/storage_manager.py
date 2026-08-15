import json
import os

from src.config.config_manager import ConfigManager
from src.encryptor.encryptor import Encryptor
from src.logger.logger_manager import LoggerManager
from src.tpm.tpm import TPM


class StorageManager:
    """
    Storage is a dictionary, where the key is the name, and the value is the secret. Name shall
    be unique.

    When read from a QR (todo), the QR is an encoded URL, which contains the name and the secret
    as well, for example:
    https://authenticationtest.com/totp/?secret=I65VU7K5ZQL7WB4E&name=Test => name =
    authenticationtest, secret = I65VU7K5ZQL7WB4E

    When added manually, name is required to be added as well.

    Instead of using the Context Manager Protocol (Python with syntax), i save the file at each
    modification. This way, there is no need to do cleanup, and if the app crashes, the file is
    still up to date. Adds/ deletes are not that frequent, so the performance impact is negligible.
    """
    logger = LoggerManager()
    config = ConfigManager()

    def __init__(self, user_password: str):
        tpm = TPM()
        self.encryptor = Encryptor(user_password, tpm.get_secret())

        storage_file_path = self.config.get("storage.storage_file_path")

        if not os.path.exists(storage_file_path):
            self.logger.warning(f"Storage file {storage_file_path} not found, no secrets loaded.")
            self.storage = {}
            return

        with open(storage_file_path, "rb") as file:
            content_encrypted = file.read()
            content = self.encryptor.decrypt(content_encrypted)
            self.storage = json.loads(content)
            self.logger.error(f"[REMOVE FROM PROD] read storage: {self.storage}")

    def add_secret(self, secret: str, name: str) -> bool:
        """
        Add a new secret to storage.
        """
        if name in self.storage:
            self.logger.warning(f"Secret for {name} already exists.")
            return False
        self.storage[name] = secret
        self.save()
        return True

    def remove_secret(self, name: str) -> bool:
        """
        Remove an existing secret from storage.
        """
        if name not in self.storage:
            self.logger.warning(f"Secret for {name} does not exist.")
            return False
        self.storage.pop(name)
        self.save()
        return True

    def get_secret(self, name: str) -> str | None:
        """
        Retrieve secret from storage with the specified name.
        """
        if name not in self.storage:
            self.logger.warning(f"Secret for {name} is missing.")
            return None
        return self.storage.get(name)

    def get_storage(self) -> dict[str, str]:
        """
        Retrieve all secrets from storage.
        """
        return self.storage

    def save(self) -> None:
        """
        Save storage to the storage file (and close it).
        """
        content = json.dumps(self.storage)
        content_encrypted = self.encryptor.encrypt(content)
        storage_file_path = self.config.get("storage.storage_file_path")
        with open(storage_file_path, "wb") as file:
            file.write(content_encrypted)
        self.logger.debug("Storage saved.")
