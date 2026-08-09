from abc import ABC, abstractmethod


class AbstractTPM(ABC):
    """
    TPM is used to encrypt and decrypt data, binding the secrets to a specific machine.

    Each platform should implement an AbstractTPMInterface, and TpmInterface shall pick the right one.
    """

    @abstractmethod
    def encrypt(self, plaintext: str) -> bytes:
        pass

    @abstractmethod
    def decrypt(self, ciphertext: bytes) -> str:
        pass
