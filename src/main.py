from pathlib import Path

import webview

from src.config.config_manager import ConfigManager
from src.logger.logger_manager import LoggerManager
from src.ui.controller.master_controller import MasterController


class Main:

    def __init__(self):
        self.config = ConfigManager()
        self.logger = LoggerManager()
        self.config.log_config(self.logger)
        # self.totp = TOTPApp()  TODO: instantiate after successful login

        # The pywebview window, so that we can call it to load views.
        self.window = None

    def main(self):
        index_path = Path(__file__).parent / "ui" / "view" / "index.html"

        js_api = MasterController()
        window = webview.create_window("usb2fa", index_path.as_uri(), js_api=js_api)
        js_api.set_window(window)

        LoggerManager.disable_pywebview_logger()
        webview.start(debug=True)


if __name__ == "__main__":
    Main().main()
