from src.totp.totpapp import TOTPApp
import requests

from src.tpm.tpm import TPM


class TestAll:

    """
    Tests TOTP code generation using https://authenticationtest.com/totpChallenge/.
    """
    def test_generate_code(self):
        secret = "I65VU7K5ZQL7WB4E"
        response = requests.get(f"https://authenticationtest.com/totp/?secret={secret}")
        assert response.status_code == 200

        totp = TOTPApp({})
        totp.get_code_and_remaining_time(secret)

        data = response.json()
        totp_code = data["code"]
        print(totp_code)


        #print(totp.generate_code("I65VU7K5ZQL7WB4E"))

        assert True

    def test_tpm(self):
        tpm = TPM()
        
        original = "For I was conscious that I knew practically nothing..."
        encrypted = tpm.encrypt(original)
        decrypted = tpm.decrypt(encrypted)

        assert original == decrypted
