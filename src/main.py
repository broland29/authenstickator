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

    def main(self):
        index_path = Path(__file__).parent / "ui" / "view" / "index.html"
        logo_path = Path(__file__).parent / "ui" / "view" / "res" / "logo.png"

        width = self.config.get("pywebview.width")
        height = self.config.get("pywebview.height")

        js_api = MasterController()
        window = webview.create_window("usb2fa", index_path.as_uri(), js_api=js_api, width=width,
                                       height=height)
        js_api.set_window(window)

        LoggerManager.disable_pywebview_logger()
        webview.start(debug=self.config.get("pywebview.debug"), icon=str(logo_path))


if __name__ == "__main__":
    Main().main()
