from abc import ABC, abstractmethod


class AbstractTPM(ABC):
    """
    The TPM's role is to generate a secret (random number) and store it in its NVRAM (non-volatile
    memory), such that, when later queried, the secret can be retrieved. This secret shall never be
    saved, logged or given away in any form. Due to its length and the way it is protected,
    it is considered that only the machine which generated it knows it.
    """

    @abstractmethod
    def setup_secret(self) -> None:
        """
        Generate a secret (random number) through the TPM and store it in its NVRAM.
        """
        pass

    @abstractmethod
    def get_secret(self) -> bytes:
        """
        Retrieve the previously generated and stored secret from TPM.
        """
        pass
