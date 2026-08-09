import base64
import datetime

import pyotp

from src.storage.storage_manager import StorageManager


class TOTPApp:
    def __init__(self):
        self.storage = StorageManager()

    def get_codes_and_expiration_times(self, name) -> tuple[str, str, float, float] | None:
        """
        I let JavaScript calculate the remaining time, I just give the expiration time (in milliseconds, since JS Date.now() is milliseconds as well).
        """
        secret = self.storage.get_secret(name)
        if secret is None:
            return None

        totp = pyotp.TOTP(secret)

        now = datetime.datetime.now().timestamp()
        interval = totp.interval  # duration (seconds) for which code is valid

        current_step_start = now - (now % interval)  # the last "round" second; when the code became valid
        next_step_start = current_step_start + interval  # when the next code will be valid
        next_next_step_start = next_step_start + interval

        current_code = totp.at(int(current_step_start))
        next_code = totp.at(int(next_step_start))
        expires_at = next_step_start * 1000  # expires when next code becomes valid, just need to convert to ms
        next_expires_at = next_next_step_start * 1000
        return current_code, next_code, expires_at, next_expires_at

    def get_all_secrets(self) -> dict[str, str]:
        return self.storage.get_all_secrets()

    def add_secret(self, secret, name) -> bool:
        return self.storage.add_secret(secret, name)

    def remove_secret(self, name) -> bool:
        return self.storage.remove_secret(name)

    # TODO: dive deep into correctness of TOTP codes
    @staticmethod
    def is_secret_valid(secret: str) -> bool:
        try:
            padding_needed = len(secret) % 8
            if padding_needed != 0:  # for 0, would pad with 8, making code incorrect :)
                secret += "=" * (8 - padding_needed)  # TOTP secrets are padded with = for size usable for base32
            base64.b32decode(secret, casefold=True)
        except Exception:
            return False

        return True
