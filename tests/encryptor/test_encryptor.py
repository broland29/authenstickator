from pathlib import Path

import pytest

TEST_DIR = Path(__file__).parent


@pytest.mark.parametrize("stub_config", [
    TEST_DIR / "test-config-aesencryptor.json"
], indirect=True)
class TestEncryptor:
    """
    Encryptor unit tests.
    """

    def test_encryptor(self, encryptor, stub_config):
        original = "For I was conscious that I knew practically nothing..."
        encrypted = encryptor.encrypt(original)
        decrypted = encryptor.decrypt(encrypted)

        assert original == decrypted
