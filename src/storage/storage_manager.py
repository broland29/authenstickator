import json
import os

from src.config.config_manager import ConfigManager
from src.encryptor.encryptor import Encryptor
from src.logger.logger_manager import LoggerManager
from src.tpm.tpm import TPM


class StorageManager:
    """
    TODO: make it usable with "with", so close called automatically. Handle close in each scenario.

    Storage is a dictionary, where the key is the name, and the value is the secret. Name shall be unique.

    When read from a QR (todo), the QR is an encoded URL, which contains the name and the secret as well, for example:
    https://authenticationtest.com/totp/?secret=I65VU7K5ZQL7WB4E&name=Test => name = authenticationtest, secret = I65VU7K5ZQL7WB4E

    When added manually, name is required to be added as well.
    """
    logger = LoggerManager()

    def __init__(self):
        self.config = ConfigManager()
        storage_file_path = self.config.get("storage.storage_file_path")

        if not self.config.get("encryptor.enabled"):
            self.key = b""  # do not require key if encryptor is disabled, NoEncryptor ignores key
        else:
            tpm = TPM()
            key = self.config.get("encryptor.key")
            self.key = tpm.encrypt(key)

        # The encryptor will use the encrypted key.
        self.encryptor = Encryptor(self.key)

        if not os.path.exists(storage_file_path):
            self.logger.warn(f"Storage file {storage_file_path} does not exist, creating it.")
            self.storage = {}
            self.close()

        with open(storage_file_path, "rb") as file:
            content_encrypted = file.read()
            content = self.encryptor.decrypt(content_encrypted)
            self.storage = json.loads(content)
            self.logger.error(f"[REMOVE FROM PROD] read storage: {self.storage}")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
        return False

    def add_secret(self, secret: str, name: str) -> bool:
        if name in self.storage:
            self.logger.warning(f"Secret for {name} already exists.")
            return False
        self.storage[name] = secret
        return True

    def remove_secret(self, name: str) -> bool:
        if name not in self.storage:
            self.logger.warning(f"Secret for {name} is missing.")
            return False
        self.storage.pop(name)
        return True

    def get_secret(self, name: str) -> str | None:
        if name not in self.storage:
            self.logger.warning(f"Secret for {name} is missing.")
            return None
        return self.storage.get(name)

    def get_all_secrets(self) -> dict[str, str]:
        return self.storage

    def close(self) -> None:
        content = json.dumps(self.storage)
        content_encrypted = self.encryptor.encrypt(content)
        storage_file_path = self.config.get("storage.storage_file_path")
        with open(storage_file_path, "wb") as file:
            file.write(content_encrypted)
