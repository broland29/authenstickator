from abc import ABC, abstractmethod


class AbstractEncryptor(ABC):

    @abstractmethod
    def set_key(self, user_password: str, salt: bytes) -> None:
        """
        Set the key for encryption.
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
