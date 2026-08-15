import os

from webview import Window

from src.config.config_manager import ConfigManager
from src.logger.logger_manager import LoggerManager
from src.ui.controller.login_controller import LoginController
from src.ui.controller.register_controller import RegisterController
from src.ui.controller.response import Response
from src.ui.controller.totp_controller import TOTPController
from src.ui.controller.view import View


class MasterController:
    """
    The main controller, registered as js_api in webview.create_window. Handles calls from
    index.html. Other HTML pages shall call their dedicated controllers, which are embedded here.

    Calls from JS are mapped like this:
    - window.pywebview.api.function -> MasterController.function()
    - window.pywebview.api.login.function -> LoginController.function()
    ...
    """

    logger = LoggerManager()
    config = ConfigManager()

    def __init__(self):
        self.window = None  # Can be set after webview.create_window succeeds.
        self.login = LoginController(self)
        self.register = RegisterController(self)
        self.totp = TOTPController(self)  # Can be instantiated only when user password is provided.

    def set_window(self, window: Window):
        self.window = window

    def init_totp_controller(self, user_password: str):
        self.totp.setup_storage_manager(user_password)

    def get_constants_handler(self):
        self.logger.log_enter("get_constants_handler")
        return Response.get_constants()

    def startup_handler(self):
        """
        Called when pywebview is ready => when UI is loaded.
        """
        self.logger.log_enter("startup_handler")
        path = self.config.get("storage.hashed_user_password_file_path")
        if not os.path.exists(path):
            self.load_view(View.REGISTER)  # No saved password => register.
            return

        self.load_view(View.LOGIN)

    def load_view(self, view: View):
        """
        Tells JS to load the given view.
        """
        self.window.evaluate_js(f"loadView('{view.value}')")
