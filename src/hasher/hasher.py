from typing_extensions import override

from src.hasher.abstract_hasher import AbstractHasher
from src.hasher.argon2_hasher import Argon2Hasher


class Hasher(AbstractHasher):
    """
    Picks the right hasher based on the configuration. Currently, only Argon2 is supported.
    """
    instance = None

    def __new__(cls):
        if cls.instance is not None:
            return cls.instance

        cls.instance = Argon2Hasher()
        return cls.instance

    @override
    def hash(self, plaintext: str) -> str:
        return self.instance.hash(plaintext)

    @override
    def verify(self, plaintext: str, hashed: str) -> bool:
        return self.instance.verify(plaintext, hashed)
