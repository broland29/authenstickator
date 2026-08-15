from abc import ABC, abstractmethod


class AbstractTPM(ABC):
    """
    TPM is used to encrypt and decrypt data, binding the secrets to a specific machine.

    Each platform should implement an AbstractTPMInterface, and TpmInterface shall pick the right
    one.
    """

    @abstractmethod
    def setup_secret(self) -> None:
        """
        Get a random number (secret) and store it in TPM.
        """
        pass

    @abstractmethod
    def get_secret(self) -> bytes:
        """
        Retrieve the previously generated random number (secret) from TPM.
        """
        pass
