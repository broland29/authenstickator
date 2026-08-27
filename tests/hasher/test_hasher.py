from pathlib import Path

import pytest

from src.hasher.hasher import Hasher

TEST_DIR = Path(__file__).parent


@pytest.mark.parametrize("stub_config", [
    TEST_DIR / "test-config-argon2hasher.json"
], indirect=True)
class TestHasher:
    """
    Encryptor unit tests.
    """

    def test_hasher(self, stub_config):
        hasher = Hasher()
        original = "For I was conscious that I knew practically nothing..."
        hashed = hasher.hash(original)
        assert hasher.verify(original, hashed)
