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
        self.login = LoginController()
        self.register = RegisterController()
        self.totp = TOTPController()
        self.window = None

    def set_window(self, window):
        """
        Sets the window attribute of the controller and its subcontrollers so that controllers can
        call JS functions.
        """
        self.window = window
        self.login.set_window(window)
        self.register.set_window(window)
        self.totp.set_window(window)

    def get_constants_handler(self):
        return Response.get_constants()

    def startup_handler(self):
        """
        Called when pywebview is ready => when UI is loaded.
        """
        self.logger.debug("Startup handler called.")
        key = self.read_key()
        if not key:
            self.load_view(View.REGISTER)
            return

        self.load_view(View.LOGIN)

    def load_view(self, view: View):
        """
        Tells JS to load the given view.
        """
        self.window.evaluate_js(f"loadView('{view.value}')")
