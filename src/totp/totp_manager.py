import base64
import binascii
import datetime
from typing import Tuple

import pyotp


class TOTPManager:
    instance = None

    def __new__(cls):
        if cls.instance is not None:
            return cls.instance

        cls.instance = super().__new__(cls)
        return cls.instance

    @staticmethod
    def get_info(secret: str) -> tuple[str, str, float, float, int] | None:
        """
        Returns current and next code and expiration time (in milliseconds, since JS Date.now()
        uses milliseconds as well).

        I let JavaScript calculate the remaining time, I just give the expiration time.
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
        expires_at = next_step_start * 1000  # expires when next code becomes valid, just need to
        # convert to ms
        next_expires_at = next_next_step_start * 1000
        return current_code, next_code, expires_at, next_expires_at, interval

    def parse_secret(self, secret: str) -> str | None:
        """
        Preprocesses secret. Returns the preprocessed secret if valid TOTP secret, otherwise None.
        """
        # Some websites, (ex: Google) gives secret with spaces. These shall be removed.
        secret = secret.replace(" ", "")

        try:
            # Pyotp pads with = to make secret's length compatible with Base32. We don't store it
            # padded, but check validness after padding. See: pyotp -> otp.py -> byte_secret()
            missing_padding = len(secret) % 8
            if missing_padding != 0:  # for 0, would pad with 8, making code incorrect :)
                secret += "=" * (8 - missing_padding)
            base64.b32decode(secret, casefold=True)  # valid TOTP secret = valid Base32 string
        except binascii.Error:
            return None

        return secret

    @staticmethod
    def parse_provisioning_uri(provisioning_uri: str) -> Tuple[str | None, str | None]:
        """
        Extracts from a provisioning URI the secret and the name. Returns none if parsing fails.
        """
        try:
            otp = pyotp.parse_uri(provisioning_uri)
            return otp.secret, TOTPManager.combine_name_and_issuer(otp.name, otp.issuer)
        except Exception:
            return None, None

    @staticmethod
    def combine_name_and_issuer(name: str | None, issuer: str | None) -> str | None:
        if name is not None and issuer is not None:
            if name.startswith(f"{issuer}:"):
                # Sometimes name contains the issuer and is not stripped by pyotp (ex: Google
                # encodes : and hence pyotp does not string); in such cases we can just return
                # the name. There are no cases in which the email itself contains the issuer and a
                # colon (ex: Google:mymail.com for the mail itself) since the colon is an invalid
                # email character
                return name
            return f"{issuer}:{name}"
        if name is not None:
            return name
        if issuer is not None:
            return issuer
        return None
