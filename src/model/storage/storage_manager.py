import json
import os

from src.model.config.config_manager import ConfigManager
from src.model.encryptor.abstract_encryptor import AbstractEncryptor
from src.model.logger.logger_manager import LoggerManager


class StorageManager:
    """
    Singleton responsible for storing secrets and names.

    Storage is a dictionary (JSON), where the key is the name, and the value is the secret. Name
    shall be unique.

    Instead of using the Context Manager Protocol (Python "with" syntax), the file is saved after
    each modification. This way, there is no need to do cleanup, and if the app crashes, the file is
    still up to date. Adds/ deletes are not that frequent, so the performance impact is negligible.
    """
    instance = None
    logger: LoggerManager
    config: ConfigManager
    encryptor: AbstractEncryptor
    storage: dict[str, str]

    def __new__(cls, encryptor):
        """
        Storage initialization. Returns None if storage decryption failed.

        While Storage is a singleton, encryptor is set at each call, since it might change (if
        encryption key changes), and in practice, each time the constructor is called, key changed.
        """
        if cls.instance is not None:
            cls.instance.encryptor = encryptor
            cls.instance.save()  # re-encrypt (re-save) storage file, since encryptor changed
            return cls.instance

        cls.instance = super().__new__(cls)
        cls.instance.logger = LoggerManager()
        cls.instance.config = ConfigManager()
        cls.instance.encryptor = encryptor

        storage_file_path = cls.instance.config.get("storage.storage_file_path")

        if not os.path.exists(storage_file_path):
            cls.instance.logger.warning(f"File {storage_file_path} not found, no secrets loaded.")
            cls.instance.storage = {}
            return cls.instance

        with open(storage_file_path, "rb") as file:
            content_encrypted = file.read()
            content = cls.instance.encryptor.decrypt(content_encrypted)
            if content is None:  # storage decryption failed
                cls.instance = None
                return cls.instance
            cls.instance.storage = json.loads(content)
            return cls.instance

    def add_secret(self, secret: str, name: str) -> bool:
        """
        Add a new secret to storage. Returns True on success, False on failure.
        """
        if name in self.storage:
            self.logger.warning(f"Secret for {name} already exists.")
            return False
        self.storage[name] = secret
        self.save()
        return True

    def remove_secret(self, name: str) -> bool:
        """
        Remove an existing secret from storage. Returns True on success, False on failure.
        """
        if name not in self.storage:
            self.logger.warning(f"Secret for {name} does not exist.")
            return False
        self.storage.pop(name)
        self.save()
        return True

    def get_secret(self, name: str) -> str | None:
        """
        Retrieve secret with the specified name. Returns True on success, False on failure.
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
