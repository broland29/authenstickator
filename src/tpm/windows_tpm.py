from typing_extensions import override

from src.tpm.abstract_tpm import AbstractTPM


class WindowsTPM(AbstractTPM):
    """
    TODO: implement in v0.2.
    """

    @override
    def encrypt(self, string: str) -> str:
        pass

    @override
    def decrypt(self, string: str) -> str:
        pass
