from src.model.encryptor.abstract_encryptor import AbstractEncryptor
from src.model.encryptor.aes_encryptor import AESEncryptor


class Encryptor:
    """
    Encryptor singleton: picks the encryptor from config. Currently, only AES is supported.
    """
    instance: AbstractEncryptor = None

    def __new__(cls, user_password: str, salt: bytes):
        if cls.instance is not None:
            return cls.instance

        cls.instance = AESEncryptor(user_password, salt)
        return cls.instance
