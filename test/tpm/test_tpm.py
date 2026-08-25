from pathlib import Path

import pytest

from src.tpm.tpm import TPM

TEST_DIR = Path(__file__).parent


@pytest.mark.parametrize("cleanup_singleton", [TPM], indirect=True)
@pytest.mark.parametrize("stub_config", [
    TEST_DIR / "test-config-notpm.json",
    TEST_DIR / "test-config-swtpm.json"
], indirect=True)
@pytest.mark.usefixtures("stub_config", "cleanup_singleton")
class TestTPM:
    """
    TPM unit tests.
    """

    def test_tpm(self):
        tpm = TPM()
        tpm.setup_secret()
        secret1 = tpm.get_secret()
        secret2 = tpm.get_secret()
        assert secret1 == secret2
