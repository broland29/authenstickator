from src.encryptor.aes_encryptor import AESEncryptor


class Encryptor:
    """
    Picks the right encryptor based on the config file. Currently, only AES is supported.
    """
    instance = None

    def __new__(cls, user_password: str, salt: bytes):
        if cls.instance is not None:
            return cls.instance

        cls.instance = AESEncryptor(user_password, salt)
        return cls.instance
