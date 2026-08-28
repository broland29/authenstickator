from src.model.hasher.abstract_hasher import AbstractHasher
from src.model.hasher.argon2_hasher import Argon2Hasher


class Hasher:
    """
    Hasher singleton: picks the hasher from config. Currently, only Argon2 is supported.
    """
    instance: AbstractHasher = None

    def __new__(cls):
        if cls.instance is not None:
            return cls.instance

        cls.instance = Argon2Hasher()
        return cls.instance
