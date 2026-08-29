from Crypto.Cipher import AES
from Crypto.Hash import SHA256
from Crypto.Protocol.KDF import PBKDF2
from typing_extensions import override

from src.model.config.config_manager import ConfigManager
from src.model.encryptor.abstract_encryptor import AbstractEncryptor
from src.model.logger.logger_manager import LoggerManager


class AESEncryptor(AbstractEncryptor):
    """
    Encrypts and decrypts data using AES algorithm.
    """
    logger: LoggerManager
    config: ConfigManager
    key: bytes

    def __init__(self):
        self.logger = LoggerManager()
        self.config = ConfigManager()

    @override
    def set_key(self, user_password: str, salt: bytes) -> None:
        # With the help of the PBKDF2, the user password is combined with the salt and yields a 32
        # byte key, which is accepted by AES. This way, there is no need to restrict user_password
        # to specific exact lengths, and the salt is combined with the user_password in a standard,
        # cryptographically correct fashion.
        #
        # 600_000 iterations and SHA256 as recommended by OWASP:
        # https://cheatsheetseries.owasp.org/cheatsheets/Password_Storage_Cheat_Sheet.html#pbkdf2
        self.key = PBKDF2(
            password=user_password,
            salt=salt,
            dkLen=32,
            count=600_000,
            hmac_hash_module=SHA256
        )

    @override
    def encrypt(self, plaintext: str) -> bytes:
        cipher = AES.new(
            key=self.key,
            mode=AES.MODE_EAX
        )
        ciphertext, tag = cipher.encrypt_and_digest(plaintext.encode())
        return cipher.nonce + tag + ciphertext

    @override
    def decrypt(self, ciphertext: bytes) -> str | None:
        nonce = ciphertext[:16]
        tag = ciphertext[16:32]
        actual_ciphertext = ciphertext[32:]

        cipher = AES.new(
            self.key,
            AES.MODE_EAX,
            nonce=nonce
        )
        try:
            return cipher.decrypt_and_verify(actual_ciphertext, tag).decode()
        except ValueError:
            self.logger.error("Decryption failed. The fact that execution reached here probably "
                              "means that user password is correct, but either the salt changed ("
                              "the TPM configs were changed) or the storage was tampered with. If "
                              "you changed TPM configs, you shall undo those changes. If the file "
                              "was tampered with, you shall recover the original version. If you "
                              "can't do any of these, you shall delete the storage file and run "
                              "again.")
            return None
