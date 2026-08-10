import json
from pathlib import Path

import pytest
from _pytest.monkeypatch import MonkeyPatch

from src.config.config_manager import ConfigManager


@pytest.fixture
def cleanup_singleton(request):
    """
    Clears the instance of a singleton. Needed for parametrized tests that use singletons;
    otherwise instance is preserved across runs.
    """
    singleton_class = request.param
    singleton_class.instance = None
    yield
    singleton_class.instance = None


@pytest.fixture
def cleanup_storage():
    """
    Deletes the test storage file before and after test.
    """
    config = ConfigManager()
    path = Path(config.get("storage.storage_file_path"))

    path.unlink(missing_ok=True)
    yield
    path.unlink(missing_ok=True)


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
