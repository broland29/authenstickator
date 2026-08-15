import os

import pytest

from src.hasher.hasher import Hasher


@pytest.mark.parametrize("cleanup_singleton", [Hasher], indirect=True)
@pytest.mark.parametrize("stub_config", [
    os.path.join("hasher", "test-config-argon2hasher.json")
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
