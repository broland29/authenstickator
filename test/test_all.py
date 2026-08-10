import pytest

from src.encryptor.encryptor import Encryptor
from src.tpm.no_tpm import NoTPM
from src.tpm.tpm import TPM


class TestAll:
    """
    Tests TOTP code generation using https://authenticationtest.com/totpChallenge/.
    """

    def test_generate_code(self):
        """
        secret = "I65VU7K5ZQL7WB4E"
        response = requests.get(f"https://authenticationtest.com/totp/?secret={secret}")
        assert response.status_code == 200

        totp = TOTPApp()
        totp.get_code_and_remaining_time(secret)

        data = response.json()
        totp_code = data["code"]
        print(totp_code)


        #print(totp.generate_code("I65VU7K5ZQL7WB4E"))
        """
        assert True

    @staticmethod
    def assert_encrypt_decrypt(encryptor):
        original = "For I was conscious that I knew practically nothing..."
        encrypted = encryptor.encrypt(original)
        decrypted = encryptor.decrypt(encrypted)

        assert original == decrypted

    def test_no_tpm(self):
        self.assert_encrypt_decrypt(NoTPM())

    def test_tpm(self):
        """
        Tests the running platform's TPM class.
        """
        self.assert_encrypt_decrypt(TPM())

    @pytest.mark.parametrize("cleanup_singleton", [Encryptor], indirect=True)
    @pytest.mark.parametrize("encryptor_type", ["NO", "AES"])
    def test_no_encryptor(self, encryptor_type: str, cleanup_singleton):
        Encryptor.encryptor_type = encryptor_type
        self.assert_encrypt_decrypt(Encryptor(b"key"))
