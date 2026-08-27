import json
from pathlib import Path

import pytest
from _pytest.monkeypatch import MonkeyPatch

from src.config.config_manager import ConfigManager
from tests.test_utils import TestUtils


@pytest.fixture
def cleanup_storage(stub_config):
    """
    Deletes the tests storage file before and after tests.
    """
    config = ConfigManager()
    path = Path(config.get("storage.storage_file_path"))
    print(path.absolute())

    path.unlink(missing_ok=True)
    yield
    path.unlink(missing_ok=True)


@pytest.fixture(autouse=True)
def cleanup_singletons():
    TestUtils.cleanup_singletons()
    yield
    TestUtils.cleanup_singletons()


@pytest.fixture
def stub_config(monkeypatch: MonkeyPatch, request):
    """
    Stubs ConfigManager by replacing its __new__ method with a read from the JSON at config_path.
    """
    config_path = request.param

    def stubbed_new(cls):
        instance = object.__new__(cls)
        with open(config_path, "r") as file:
            instance.config = json.load(file)
        return instance

    monkeypatch.setattr(ConfigManager, "__new__", stubbed_new)
