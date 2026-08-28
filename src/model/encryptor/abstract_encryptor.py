from abc import ABC, abstractmethod


class AbstractEncryptor(ABC):

    @abstractmethod
    def __init__(self, user_password: str, salt: bytes):
        """
        Shall contain encryption key creation from user_password and salt.
        """
        pass

    @abstractmethod
    def reinit(self, user_password: str, salt: bytes):
        """
        If user_password or salt changes, encryption key shall be replaced.
        """
        pass

    @abstractmethod
    def encrypt(self, plaintext: str) -> bytes:
        """
        Encrypt the plaintext.
        """
        pass

    @abstractmethod
    def decrypt(self, ciphertext: bytes) -> str | None:
        """
        Decrypt the ciphertext. Returns None if ciphertext cannot be decrypted with the current key.
        """
        pass
