import platform
from pathlib import Path

import webview

from src.controller.master_controller import MasterController
from src.model.config.config_manager import ConfigManager
from src.model.logger.logger_manager import LoggerManager


class Main:
    config = ConfigManager()
    logger = LoggerManager()

    def __init__(self):
        self.config.log_config(self.logger)

    def main(self):
        index_path = Path(__file__).parent / "view" / "html" / "index.html"

        width = self.config.get("pywebview.width")
        height = self.config.get("pywebview.height")

        js_api = MasterController()
        window = webview.create_window("Authenstickator", index_path.as_uri(), js_api=js_api,
                                       width=width, height=height)
        js_api.set_window(window)

        LoggerManager.disable_pywebview_logger()

        os_name = platform.system()
        if os_name == "Linux":
            icon = str(Path(__file__).parent / "view" / "html" / "res" / "logo.png")
        elif os_name == "Windows":
            icon = str(Path(__file__).parent / "view" / "html" / "res" / "logo.ico")
        else:
            self.logger.error(f"Icon not implemented for OS {os_name}, continuing without icon")
            icon = None
        webview.start(debug=self.config.get("pywebview.debug"), icon=icon)


if __name__ == "__main__":
    Main().main()
