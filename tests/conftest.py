"""
Fixtures. Most delegate to TestUtils, since fixtures cannot be called directly by code,
and in some cases, that was desired (ex: when simulating a new session, cleanup_session needs to
be manually called).
"""
import json

import pytest
from _pytest.monkeypatch import MonkeyPatch

from src.model.config.config_manager import ConfigManager
from src.model.encryptor.abstract_encryptor import AbstractEncryptor
from src.model.storage.storage_manager import StorageManager
from tests.test_utils import TestUtils


### Config stubbing ###

@pytest.fixture
def stub_config(monkeypatch: MonkeyPatch, request):
    """
    Stubs ConfigManager by replacing its __new__ method.
    """
    config_path = request.param

    def stubbed_new(cls):
        instance = object.__new__(cls)
        with open(config_path, "r") as file:
            instance.config = json.load(file)
        return instance

    monkeypatch.setattr(ConfigManager, "__new__", stubbed_new)


### Test data generation ###

@pytest.fixture
def encryptor() -> AbstractEncryptor:
    return TestUtils.encryptor()


@pytest.fixture
def storage(encryptor) -> StorageManager:
    return TestUtils.storage()


### Session cleanup ###

@pytest.fixture(autouse=True)
def cleanup_session(stub_config):
    """
    Cleans up singletons and storage. Must run after stub_config (to clear the right storage file),
    hence added as argument.
    """
    TestUtils.cleanup_session()
    yield
    TestUtils.cleanup_session()
