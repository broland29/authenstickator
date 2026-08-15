from pathlib import Path

import pytest

from src.hasher.hasher import Hasher

TEST_DIR = Path(__file__).parent


@pytest.mark.parametrize("cleanup_singleton", [Hasher], indirect=True)
@pytest.mark.parametrize("stub_config", [
    TEST_DIR / "test-config-argon2hasher.json"
], indirect=True)
@pytest.mark.usefixtures("stub_config", "cleanup_singleton")
class TestHasher:
    """
    Encryptor unit tests.
    """

    def test_hasher(self):
        """
        Fun fact: Argon2 does not generate the same hash for the same input. Instead, its verify
        method shall be used.
        """
        hasher = Hasher()
        original = "For I was conscious that I knew practically nothing..."
        hashed = hasher.hash(original)
        assert hasher.verify(original, hashed)
