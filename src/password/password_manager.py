import os.path
from typing import Final

from src.config.config_manager import ConfigManager
from src.hasher.abstract_hasher import AbstractHasher
from src.hasher.hasher import Hasher
from src.logger.logger_manager import LoggerManager


class PasswordManager:
    # Limits based on NIST SP 800-63B-4, July 2025:
    # https://nvlpubs.nist.gov/nistpubs/SpecialPublications/NIST.SP.800-63B-4.pdf Section 3.1.1.2
    MIN_LENGTH_HARD_LIMIT: Final[int] = 15  # Verifiers SHALL require passwords minimum 15
    MAX_LENGTH_HARD_LIMIT: Final[int] = 100  # Verifiers SHOULD permit at least 64 chars

    instance = None
    logger: LoggerManager
    config: ConfigManager
    hasher: AbstractHasher
    min_length: int
    max_length: int

    def __new__(cls):
        if cls.instance is not None:
            return cls.instance

        cls.instance = super().__new__(cls)
        cls.logger = LoggerManager()
        cls.config = ConfigManager()
        cls.hasher = Hasher()

        min_length = cls.config.get("password.min_length")
        if min_length < cls.MIN_LENGTH_HARD_LIMIT:
            cls.logger.warning(
                f"Overriding min_length parameter {min_length} with {cls.MIN_LENGTH_HARD_LIMIT}")
            min_length = cls.MIN_LENGTH_HARD_LIMIT
        cls.min_length = min_length

        max_length = cls.config.get("password.max_length")
        if max_length > cls.MAX_LENGTH_HARD_LIMIT:
            cls.logger.warning(
                f"Overriding max_length parameter {max_length} with {cls.MAX_LENGTH_HARD_LIMIT}")
            max_length = cls.MAX_LENGTH_HARD_LIMIT
        cls.max_length = max_length

        return cls.instance

    def previous_password_exists(self):
        """
        Returns true if a previous password was provided, from the system's perspective.
        """
        return os.path.exists(self.config.get("password.hash_file_path"))

    def password_acceptable(self, password: str) -> bool:
        """
        Returns true if password meets requirements.
        """
        return self.min_length <= len(password) <= self.max_length

    def password_matches(self, password: str) -> bool:
        """
        Returns true if password matches previously provided password.
        """
        hash_file_path = self.config.get("password.hash_file_path")
        if not self.previous_password_exists():
            return True

        with open(hash_file_path, "r") as file:
            hashed_password = file.read()
            if not self.hasher.verify(password, hashed_password):
                return False
        return True

    def set_password(self, password: str) -> bool:
        """
        Sets a new password if it meets requirements.
        """
        if not self.password_acceptable(password):
            return False

        hash_file_path = self.config.get("password.hash_file_path")
        with open(hash_file_path, "w") as file:
            hashed_password = self.hasher.hash(password)
            file.write(hashed_password)
        return True
