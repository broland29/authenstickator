from pathlib import Path

import webview

from src.config.config_manager import ConfigManager
from src.logger.logger_manager import LoggerManager
from src.ui.controller.master_controller import MasterController


class Main:
    config = ConfigManager()
    logger = LoggerManager()

    def __init__(self):
        self.config.log_config(self.logger)

    @staticmethod
    def main():
        index_path = Path(__file__).parent / "ui" / "view" / "index.html"

        js_api = MasterController()
        window = webview.create_window("usb2fa", index_path.as_uri(), js_api=js_api)
        js_api.set_window(window)

        LoggerManager.disable_pywebview_logger()
        webview.start(debug=True)


if __name__ == "__main__":
    Main().main()
