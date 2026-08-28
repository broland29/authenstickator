from pathlib import Path

import pytest

from model.storage.storage_manager import StorageManager
from tests.test_utils import TestUtils

TEST_DIR = Path(__file__).parent


@pytest.mark.parametrize("stub_config", [
    TEST_DIR / "test-config-aesencryptor-notpm.json",
    TEST_DIR / "test-config-aesencryptor-swtpm.json"
], indirect=True)
class TestStorage:
    """
    Storage unit tests. Uses Encryptor and TPM, so those unit tests shall pass first.
    """
    USER_PASSWORD = "DummyPassword"

    def test_storage_persistence(self, cleanup_storage, stub_config, cleanup_singletons):
        # First session: a secret added.
        storage = StorageManager(self.USER_PASSWORD)
        secret = "I65VU7K5ZQL7WB4E"
        name = "Authentication Test"

        assert storage.add_secret(secret, name) == True
        assert (storage.get_secret(name) == secret)

        # Second session: the secret shall still be there.
        TestUtils.cleanup_singletons()
        storage = StorageManager(self.USER_PASSWORD)
        assert (storage.get_secret(name) == secret)

    def test_storage_delete(self, cleanup_storage, stub_config):
        storage = StorageManager(self.USER_PASSWORD)

        storage.add_secret("sec1", "nam1")
        assert storage.get_storage() == {"nam1": "sec1"}

        storage.add_secret("sec2", "nam2")
        assert storage.get_storage() == {"nam1": "sec1", "nam2": "sec2"}

        storage.remove_secret("nam1")
        assert storage.get_storage() == {"nam2": "sec2"}

    def test_storage_add_duplicate_name(self, cleanup_storage, stub_config):
        storage = StorageManager(self.USER_PASSWORD)

        storage.add_secret("sec1", "nam1")
        assert storage.get_storage() == {"nam1": "sec1"}

        assert storage.add_secret("sec2", "nam1") == False
        assert storage.get_storage() == {"nam1": "sec1"}

    def test_storage_get_nonexistent(self, cleanup_storage, stub_config):
        storage = StorageManager(self.USER_PASSWORD)

        assert storage.get_secret("nam1") is None
        assert storage.get_storage() == {}
