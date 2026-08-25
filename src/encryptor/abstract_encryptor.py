from abc import ABC, abstractmethod


class AbstractEncryptor(ABC):

    @abstractmethod
    def __init__(self, user_password: str, salt: bytes):
        """
        Encryptor shall be initialized with a valid state, i.e., with key initialized.
        """
        pass

    @abstractmethod
    def reinit(self, user_password: str, salt: bytes):
        pass

    @abstractmethod
    def encrypt(self, plaintext: str) -> bytes:
        pass

    @abstractmethod
    def decrypt(self, ciphertext: bytes) -> str:
        pass
