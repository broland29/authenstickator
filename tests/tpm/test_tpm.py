from pathlib import Path

import pytest

from model.tpm.tpm import TPM

TEST_DIR = Path(__file__).parent


@pytest.mark.parametrize("stub_config", [
    TEST_DIR / "test-config-notpm.json",
    TEST_DIR / "test-config-swtpm.json"
], indirect=True)
class TestTPM:
    """
    TPM unit tests.
    """

    def test_tpm(self, stub_config):
        tpm = TPM()
        tpm.setup_secret()
        secret1 = tpm.get_secret()
        secret2 = tpm.get_secret()
        assert secret1 == secret2
