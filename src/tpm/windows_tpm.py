from src.tpm.abstract_tpm import AbstractTPM
from typing_extensions import override

"""
TODO: implement in v0.2.
"""
class WindowsTPM(AbstractTPM):

    @override
    def encrypt(self, string: str) -> str:
        pass

    @override
    def decrypt(self, string: str) -> str:
        pass
