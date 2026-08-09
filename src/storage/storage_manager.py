import json
import os

from src.config.config_manager import ConfigManager
from src.encryptor.aes_encryptor import AESEncryptor
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

    def __init__(self):
        self.logger = LoggerManager()

        config = ConfigManager()
        encryption_key = config.get("storage.encryption_key")
        self.storage_file_path = config.get("storage.storage_file_path")

        if config.get("tpm.enabled"):
            self.tpm_interface = TPM()
        else:
            self.tpm_interface = None

        if config.get("storage.encryptor") == "AES":
            self.encryptor = AESEncryptor(encryption_key)
        else:
            self.encryptor = None

        if not os.path.exists(self.storage_file_path):
            self.logger.warn(f"Storage file {self.storage_file_path} does not exist, creating it.")
            self.storage = {}
            self.close()

        with open(self.storage_file_path, "rb") as file:
            content_encrypted = file.read()
            if self.encryptor:
                content_decrypted = self.encryptor.decrypt(content_encrypted)
            else:
                content_decrypted = content_encrypted

            self.storage = json.loads(content_decrypted)
            self.logger.error(f"[REMOVE FROM PROD] read storage: {self.storage}")

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
        content_decrypted = json.dumps(self.storage)

        if self.encryptor:
            content_encrypted = self.encryptor.encrypt(content_decrypted)
        else:
            content_encrypted = content_decrypted.encode()

        with open("storage.txt", "wb") as file:
            file.write(content_encrypted)
