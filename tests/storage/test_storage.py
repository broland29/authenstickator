from pathlib import Path

import pytest

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

    def test_storage_persistence(self, storage, stub_config):
        # First session: a secret added.
        secret = "I65VU7K5ZQL7WB4E"
        name = "Authentication Test"

        assert storage.add_secret(secret, name) == True
        assert (storage.get_secret(name) == secret)

        # Second session: the secret shall still be there.
        # To simulate a new session, singletons are cleared and storage is reinitialized with the
        # same values as initially, but the storage file is not cleaned up.
        TestUtils.cleanup_singletons()
        storage = TestUtils.storage()  # same storage as the initial
        assert (storage.get_secret(name) == secret)

    def test_storage_delete(self, storage, stub_config):
        storage.add_secret("sec1", "nam1")
        assert storage.get_storage() == {"nam1": "sec1"}

        storage.add_secret("sec2", "nam2")
        assert storage.get_storage() == {"nam1": "sec1", "nam2": "sec2"}

        storage.remove_secret("nam1")
        assert storage.get_storage() == {"nam2": "sec2"}

    def test_storage_add_duplicate_name(self, storage, stub_config):
        storage.add_secret("sec1", "nam1")
        assert storage.get_storage() == {"nam1": "sec1"}

        assert storage.add_secret("sec2", "nam1") == False
        assert storage.get_storage() == {"nam1": "sec1"}

    def test_storage_get_nonexistent(self, storage, stub_config):
        assert storage.get_secret("nam1") is None
        assert storage.get_storage() == {}
