from abc import ABC, abstractmethod


class AbstractHasher(ABC):

    @abstractmethod
    def hash(self, plaintext: str) -> str:
        pass
