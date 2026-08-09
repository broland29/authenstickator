from typing import Final

from src.config.config_manager import ConfigManager
from src.logger.logger_manager import LoggerManager
from src.storage import storage_manager
from src.storage.storage_manager import StorageManager
from src.totp.totpapp import TOTPApp
import webview

class Main:

    STATUS_SUCCESS: Final[str] = "success"
    STATUS_ERROR: Final[str] = "error"

    def __init__(self):
        self.config = ConfigManager()
        self.logger = LoggerManager()
        self.config.log_config(self.logger)
        self.totp = TOTPApp()

    def main(self):
        webview.create_window("usb2fa", "index.html", js_api=self)
        LoggerManager.disable_pywebview_logger()
        webview.start(debug=True)

    def get_constants_handler(self) -> dict:
        return {
            "STATUS_SUCCESS": self.STATUS_SUCCESS,
            "STATUS_ERROR": self.STATUS_ERROR,
        }

    def add_all_secrets_handler(self) -> list[dict]:
        self.logger.info("Function add_all_secrets_handler called.")
        secrets = self.totp.get_all_secrets()
        codes_and_remaining_times = []
        # TODO
        #for secret in secrets.values():
        #    codes_and_remaining_times.append(self.get_codes_and_expiration_times(name))
        return codes_and_remaining_times

    def add_secret_handler(self, secret, name):
        self.logger.info("Function add_secret_handler called.")

        if not secret:
            return self._error("Secret cannot be empty.")

        if not name:
            return self._error("Name cannot be empty.")

        secret = secret.replace(" ", "")  # Gmail gives secret with spaces, for example.
        if not self.totp.is_secret_valid(secret):
            return self._error("Invalid secret.")

        added = self.totp.add_secret(secret, name)
        if not added:
            return self._error(f"Secret for {name} already exists.")

        return self.get_codes_and_expiration_times(name)

    def get_codes_and_expiration_times(self, name) -> dict:
        current_code, next_code, expires_at, next_expires_at = self.totp.get_codes_and_expiration_times(name)
        return self._success({
            "name": name,
            "current_code": current_code,
            "next_code": next_code,
            "expires_at": expires_at,
            "next_expires_at": next_expires_at
        })

    def remove_secret_handler(self, name):
        self.logger.info("Function remove_secret_handler called.")
        self.totp.remove_secret(name)

    @staticmethod
    def _success(data = None):
        return {
            "status": "success",
            "data": data
        }

    @staticmethod
    def _error(error_message = None):
        return {
            "status": "error",
            "error_message": error_message
        }

if __name__ == "__main__":
    Main().main()
