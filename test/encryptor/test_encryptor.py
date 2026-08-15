import os

import pytest

from src.encryptor.encryptor import Encryptor


@pytest.mark.parametrize("cleanup_singleton", [Encryptor], indirect=True)
@pytest.mark.parametrize("stub_config", [
    os.path.join("tpm", "test-config-aesencryptor.json")
], indirect=True)
@pytest.mark.usefixtures("stub_config", "cleanup_singleton")
class TestEncryptor:
    """
    Encryptor unit tests.
    """
    USER_PASSWORD = "DummyPassword"
    SALT = ("A" * 16).encode()

    def test_encryptor(self):
        encryptor = Encryptor(self.USER_PASSWORD, self.SALT)
        original = "For I was conscious that I knew practically nothing..."
        encrypted = encryptor.encrypt(original)
        decrypted = encryptor.decrypt(encrypted)

        assert original == decrypted
