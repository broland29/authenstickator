"""
Error message constants. Currently used only when error differentiation is necessary. In future
versions, if i18n is desired, all error messages shall be extracted here.
"""
from typing import Final


class Errors:
    ERROR_DECRYPT: Final[str] = ("Storage decryption failed. Either TPM settings changed, or the "
                                 "storage was tampered with.")
