from pathlib import Path

import pytest

from conftest import stub_config
from src.encryptor.encryptor import Encryptor
from src.storage.storage_manager import StorageManager
from src.tpm.tpm import TPM

TEST_DIR = Path(__file__).parent


@pytest.mark.parametrize("cleanup_singleton", [Encryptor, TPM], indirect=True)
@pytest.mark.parametrize("stub_config", [
    TEST_DIR / "test-config-aesencryptor-notpm.json",
    TEST_DIR / "test-config-aesencryptor-tpm.json"
], indirect=True)
@pytest.mark.usefixtures("stub_config", "cleanup_storage", "cleanup_singleton")
class TestStorage:
    """
    Storage unit tests. Uses Encryptor and TPM, so those unit tests shall pass first.
    """
    USER_PASSWORD = "DummyPassword"

    def test_storage_persistence(self, cleanup_storage, cleanup_singleton):
        # first session: a secret added; when ends, dumped to storage file
        storage = StorageManager(self.USER_PASSWORD)
        secret = "I65VU7K5ZQL7WB4E"
        name = "Authentication Test"

        storage.add_secret(secret, name)
        assert (storage.get_secret(name) == secret)

        # second session: the secret shall still be there
        storage = StorageManager(self.USER_PASSWORD)
        assert (storage.get_secret(name) == secret)

    def test_storage_delete(self, cleanup_storage):
        storage = StorageManager(self.USER_PASSWORD)

        storage.add_secret("sec1", "nam1")
        assert storage.get_storage() == {"nam1": "sec1"}

        storage.add_secret("sec2", "nam2")
        assert storage.get_storage() == {"nam1": "sec1", "nam2": "sec2"}

        storage.remove_secret("nam1")
        assert storage.get_storage() == {"nam2": "sec2"}

    def test_storage_add_duplicate_name(self, cleanup_storage):
        storage = StorageManager(self.USER_PASSWORD)

        storage.add_secret("sec1", "nam1")
        assert storage.get_storage() == {"nam1": "sec1"}

        assert storage.add_secret("sec2", "nam1") == False
        assert storage.get_storage() == {"nam1": "sec1"}

    def test_storage_get_nonexistent(self, cleanup_storage):
        storage = StorageManager(self.USER_PASSWORD)

        assert storage.get_secret("nam1") is None
        assert storage.get_storage() == {}
