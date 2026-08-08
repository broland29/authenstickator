from abc import ABC, abstractmethod

class AbstractEncryptor(ABC):
    @abstractmethod
    def encrypt(self, plaintext: str) -> bytes:
        pass

    @abstractmethod
    def decrypt(self, ciphertext: bytes) -> str:
        pass
