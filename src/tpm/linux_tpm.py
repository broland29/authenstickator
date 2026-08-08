from typing import Final
from typing_extensions import override

from tpm2_pytss import FAPI

from src.tpm.abstract_tpm import AbstractTPM

class LinuxTPM(AbstractTPM):
    """
    TPM interface for Linux.

    TPM has to be set up by the user. The config is usually at path /etc/tpm2-tss/fapi-config.json
    """

    KEY_PATH: Final[str] = "HS/SRK/usb2fakey"
    """Encryption and decryption uses a key, which is identified by this path."""

    def __init__(self):
        with FAPI() as fapi:
            fapi.set_auth_callback(self.auth_callback)
            fapi.provision(is_provisioned_ok=True)

    def auth_callback(self, path, description, user_data=None):
        """FAPI"""
        print(path)
        return b""

    @override
    def encrypt(self, plaintext: str) -> bytes:
        with FAPI() as fapi:
            fapi.set_auth_callback(self.auth_callback)
            fapi.create_key(
                path = self.KEY_PATH,
                type_ = "decrypt",
                exists_ok = True
            )
            return fapi.encrypt(self.KEY_PATH, plaintext.encode("utf-8"))

    @override
    def decrypt(self, ciphertext: bytes) -> str:
        with FAPI() as fapi:
            fapi.set_auth_callback(self.auth_callback)
            return fapi.decrypt(self.KEY_PATH, ciphertext).decode("utf-8")
