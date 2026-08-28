import base64
import binascii
import datetime
from typing import Tuple

import pyotp


class TOTPManager:
    """
    Singleton responsible for TOTP code generation. No logging, since will be called frequently.
    """
    instance = None

    def __new__(cls):
        if cls.instance is not None:
            return cls.instance

        cls.instance = super().__new__(cls)
        return cls.instance

    @staticmethod
    def get_info(secret: str) -> tuple[str, str, float, float, int] | None:
        """
        Returns:
            - the current and the next TOTP code
            - the current and the next expiration time (in milliseconds, for JS convenience)
            - the time interval

        All this information is used by the frontend. The remaining time is calculated by the
        frontend from the expiration time, this way, this method needs to be queried only when
        current code expires. The next code and expiration is sent as well for a smooth transition:
        the frontend, upon expiration of current, can promote next instantly, without waiting for
        response (after promotion, the remaining time is the interval).
        """
        totp = pyotp.TOTP(secret)

        now = datetime.datetime.now().timestamp()
        interval = totp.interval  # duration (seconds) for which code is valid

        # the last "round" second; when the code became valid
        current_step_start = now - (now % interval)

        # when the next code will be valid
        next_step_start = current_step_start + interval

        # when the next code will expire
        next_next_step_start = next_step_start + interval

        current_code = totp.at(int(current_step_start))
        next_code = totp.at(int(next_step_start))
        expires_at = next_step_start * 1000  # expires when next code becomes valid; convert to ms
        next_expires_at = next_next_step_start * 1000
        return current_code, next_code, expires_at, next_expires_at, interval

    @staticmethod
    def parse_secret(secret: str) -> str | None:
        """
        Preprocesses secret. Returns the preprocessed secret if valid TOTP secret, otherwise None.

        Validation is done as in pyotp library's OTP class, method byte_secret: the string is
        padded with = signs to have a valid Base32 length (divisible by 8). However, this does
        not ensure Base32 correctness. In a Base32 string, each character encodes 5 bits; char A,
        being the first character, represents 00000. The filler protects only against cases
        where the leftovers are zeros and can be discarded when grouping into bytes.
            "MZXQ" => "MZXQ====" => [01100110][01101111][0000????] => 01100110_01101111 good
            "A"    => "A=======" => [00000???] => bad
            "AB"   => "AB======" => [00000000][01??????] => bad

        So, valid = can be converted to Base32 after padding with =.
        """
        # Some websites, (ex: Google) gives secret with spaces. These shall be removed.
        secret = secret.replace(" ", "")

        try:
            missing_padding = len(secret) % 8
            if missing_padding != 0:  # for 0, would pad with 8, making code incorrect :)
                secret += "=" * (8 - missing_padding)
            base64.b32decode(secret, casefold=True)
        except binascii.Error:
            return None

        return secret

    @staticmethod
    def parse_provisioning_uri(provisioning_uri: str) -> Tuple[str, str] | None:
        """
        Extracts from a provisioning URI the secret and the name. Returns none on failure.
        """
        try:
            otp = pyotp.parse_uri(provisioning_uri)
            name = TOTPManager.combine_name_and_issuer(otp.name, otp.issuer)
            if name is None:
                return None
            return otp.secret, name
        except ValueError:
            return None

    @staticmethod
    def combine_name_and_issuer(name: str | None, issuer: str | None) -> str | None:
        """
        Authenstickator only stores name and secret. URIs might contain name and issuer, there are
        concatenated.
        """
        if name is not None and issuer is not None:
            if name.startswith(f"{issuer}:"):
                # Sometimes name contains the issuer and is not stripped by pyotp (ex: Google
                # encodes : and hence pyotp does not strip); in such cases we can just return
                # the name. There are no cases in which the email itself contains the issuer and a
                # colon (ex: Google:mymail.com for the mail itself) since the colon is an invalid
                # email character.
                return name
            return f"{issuer}:{name}"
        if name is not None:
            return name
        if issuer is not None:
            return issuer
        return None
