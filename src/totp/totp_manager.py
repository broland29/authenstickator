import base64
import datetime

import pyotp


class TOTPManager:
    instance = None

    def __new__(cls):
        if cls.instance is not None:
            return cls.instance

        cls.instance = super().__new__(cls)
        return cls.instance

    def get_info(self, secret: str) -> tuple[str, str, float, float] | None:
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
        return current_code, next_code, expires_at, next_expires_at

    def is_secret_valid(self, secret: str) -> bool:
        """
        Returns True if the secret is a valid TOTP secret.

        TODO: proper correctness check (research what is accepted).
        """
        try:
            base64.b32decode(secret, casefold=True)
        except Exception:
            return False

        return True
