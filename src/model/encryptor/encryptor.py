from src.model.encryptor.abstract_encryptor import AbstractEncryptor
from src.model.encryptor.aes_encryptor import AESEncryptor


class Encryptor:
    """
    Encryptor singleton: picks the encryptor from config. Currently, only AES is supported.

    While Encryptor is a singleton, user password and salt are set at each call, since these
    might change, and in practice, each time the constructor is called, user password changed.
    """
    instance: AbstractEncryptor = None

    def __new__(cls, user_password: str, salt: bytes):
        if cls.instance is not None:
            cls.instance.set_key(user_password, salt)
            return cls.instance

        cls.instance = AESEncryptor()
        cls.instance.set_key(user_password, salt)
        return cls.instance
