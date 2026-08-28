from pathlib import Path

from model.qr.qr_manager import QRManager

TEST_DIR = Path(__file__).parent


class TestQR:
    def test_qr_authentication_test(self):
        """
        Test with the QR from https://authenticationtest.com/totpChallenge/.
        """
        qr = QRManager()
        decoded = qr.decode(TEST_DIR / "test-qr-authenticationtest.jpeg")
        assert decoded == "otpauth://totp/totp@authenticationtest.com?secret=I65VU7K5ZQL7WB4E"

    def test_qr_google(self):
        """
        Test with QR from https://myaccount.google.com/two-step-verification (Google dummy account).
        """
        qr = QRManager()
        decoded = qr.decode(TEST_DIR / "test-qr-google.jpeg")
        assert decoded == ("otpauth://totp/Google%3Arolandtest123456%40gmail.com?secret"
                           "=refyopv7thgvsd5twr3marvdpqyugxls&issuer=Google")

    def test_qr_microsoft(self):
        """
        Test with QR from https://account.live.com/proofs (Microsoft dummy account).
        """
        qr = QRManager()
        decoded = qr.decode(TEST_DIR / "test-qr-microsoft.jpeg")
        assert decoded == ("otpauth://totp/Microsoft:rolandtest123456@gmail.com?secret"
                           "=G5HLROANXBF7335S&issuer=Microsoft")

    def test_qr_invalid(self):
        """
        Test with an image which does not contain QR code.
        """
        qr = QRManager()
        decoded = qr.decode(TEST_DIR / "test-qr-invalid.jpeg")
        assert decoded is None

    def test_qr_bad_path(self):
        """
        Test with a path which does not point to a file.
        """
        qr = QRManager()
        decoded = qr.decode("not-a-file")
        assert decoded is None
