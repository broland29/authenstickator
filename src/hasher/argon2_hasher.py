from argon2 import PasswordHasher
from argon2.exceptions import InvalidHashError, VerificationError
from typing_extensions import override

from src.hasher.abstract_hasher import AbstractHasher


class Argon2Hasher(AbstractHasher):

    def __init__(self):
        self.password_hasher = PasswordHasher()

    @override
    def hash(self, plaintext: str) -> str:
        return self.password_hasher.hash(plaintext)

    @override
    def verify(self, plaintext: str, hashed: str) -> bool:
        try:
            return self.password_hasher.verify(hashed, plaintext)
        except InvalidHashError | VerificationError:
            return False
