from pathlib import Path

import pytest
import requests

from src.model.totp.totp_manager import TOTPManager

TEST_DIR = Path(__file__).parent


@pytest.mark.parametrize("stub_config", [TEST_DIR / "test-config-totp.json"], indirect=True)
class TestTOTP:
    def test_generate_code(self):
        """
        Uses https://authenticationtest.com/totpChallenge/'s API to check TOTP code generation
        using their hardcoded secret.
        """
        secret = "I65VU7K5ZQL7WB4E"
        response = requests.get(f"https://authenticationtest.com/totp/?secret={secret}")
        assert response.status_code == 200

        data = response.json()
        totp_code = data["code"]
        assert totp_code is not None

        totp = TOTPManager()
        current_code, _, _, _, interval = totp.get_info(secret)
        assert current_code == totp_code
        assert interval == 30

    def test_parse_provisioning_uri_authentication_test(self):
        provisioning_uri = "otpauth://totp/totp@authenticationtest.com?secret=I65VU7K5ZQL7WB4E"
        totp = TOTPManager()
        secret, name = totp.parse_provisioning_uri(provisioning_uri)
        assert secret == "I65VU7K5ZQL7WB4E"
        assert name == "totp@authenticationtest.com"

    def test_parse_provisioning_uri_authentication_google(self):
        provisioning_uri = ("otpauth://totp/Google%3Arolandtest123456%40gmail.com?secret"
                            "=refyopv7thgvsd5twr3marvdpqyugxls&issuer=Google")
        totp = TOTPManager()
        secret, name = totp.parse_provisioning_uri(provisioning_uri)
        assert secret == "refyopv7thgvsd5twr3marvdpqyugxls"
        assert name == "Google:rolandtest123456@gmail.com"

    def test_parse_provisioning_uri_authentication_microsoft(self):
        provisioning_uri = ("otpauth://totp/Microsoft:rolandtest123456@gmail.com?secret"
                            "=G5HLROANXBF7335S&issuer=Microsoft")
        totp = TOTPManager()
        secret, name = totp.parse_provisioning_uri(provisioning_uri)
        assert secret == "G5HLROANXBF7335S"
        assert name == "Microsoft:rolandtest123456@gmail.com"
