from src.hasher.argon2_hasher import Argon2Hasher


class Hasher:
    """
    Picks the right hasher based on the configuration. Currently, only Argon2 is supported.
    """
    instance = None

    def __new__(cls):
        if cls.instance is not None:
            return cls.instance

        cls.instance = Argon2Hasher()
        return cls.instance
