from abc import ABC, abstractmethod


class AbstractHasher(ABC):

    @abstractmethod
    def hash(self, plaintext: str) -> str:
        """
        Hash the plaintext.
        """
        pass

    @abstractmethod
    def verify(self, plaintext: str, hashed: str) -> bool:
        """
        Verify the plaintext against hashed.
        """
        pass
