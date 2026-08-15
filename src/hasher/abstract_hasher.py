from abc import ABC, abstractmethod


class AbstractHasher(ABC):

    @abstractmethod
    def hash(self, plaintext: str) -> str:
        pass

    @abstractmethod
    def verify(self, plaintext: str, hashed: str) -> bool:
        pass
