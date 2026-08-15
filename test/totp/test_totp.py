import requests

from src.totp.totp_manager import TOTPManager


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
        current_code, next_code, expires_at, next_expires_at = totp.get_info(
            secret)

        assert current_code == totp_code
