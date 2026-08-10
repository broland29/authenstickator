import pytest

from conftest import stub_config
from src.encryptor.encryptor import Encryptor
from src.storage.storage_manager import StorageManager


@pytest.mark.parametrize("cleanup_singleton", [Encryptor], indirect=True)
@pytest.mark.parametrize("stub_config", ["test-config-aesencryptor-notpm.json",
                                         "test-config-aesencryptor-tpm.json",
                                         "test-config-noencryptor-notpm.json",
                                         "test-config-noencryptor-tpm.json"], indirect=True)
@pytest.mark.usefixtures("stub_config", "cleanup_storage", "cleanup_singleton")
class TestStorage:

    def test_storage_persistence(self, cleanup_storage, cleanup_singleton):
        # first session: a secret added; when ends, dumped to storage file
        with StorageManager() as storage:
            secret = "I65VU7K5ZQL7WB4E"
            name = "Authentication Test"

            storage.add_secret(secret, name)
            assert (storage.get_secret(name) == secret)

        # second session
        with StorageManager() as storage:
            #  the secret shall still be there
            assert (storage.get_secret(name) == secret)

    def test_storage_delete(self, cleanup_storage):
        with StorageManager() as storage:
            storage.add_secret("sec1", "nam1")
            assert storage.get_all_secrets() == {"nam1": "sec1"}

            storage.add_secret("sec2", "nam2")
            assert storage.get_all_secrets() == {"nam1": "sec1", "nam2": "sec2"}

            storage.remove_secret("nam1")
            assert storage.get_all_secrets() == {"nam2": "sec2"}

    def test_storage_add_duplicate_name(self, cleanup_storage):
        with StorageManager() as storage:
            storage.add_secret("sec1", "nam1")
            assert storage.get_all_secrets() == {"nam1": "sec1"}

            assert storage.add_secret("sec2", "nam1") == False
            assert storage.get_all_secrets() == {"nam1": "sec1"}

    def test_storage_get_nonexistent(self, cleanup_storage):
        with StorageManager() as storage:
            assert storage.get_secret("nam1") is None
            assert storage.get_all_secrets() == {}
