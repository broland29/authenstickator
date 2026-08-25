import webview
from webview import Window

from src.config.config_manager import ConfigManager
from src.logger.logger_manager import LoggerManager
from src.password.password_manager import PasswordManager
from src.ui.controller.change_password_controller import ChangePasswordController
from src.ui.controller.login_controller import LoginController
from src.ui.controller.register_controller import RegisterController
from src.ui.controller.response import Response
from src.ui.controller.totp_controller import TOTPController
from src.ui.controller.view import View


class MasterController:
    """
    Main controller, registered as js_api in webview.create_window. Handles calls from index.html.
    Other HTML pages shall call their dedicated controllers, which are embedded here.

    Calls from JS are mapped like this:
    - window.pywebview.api.function -> MasterController.function()
    - window.pywebview.api.login.function -> LoginController.function()
    ...

    Passes itself as reference for dedicated controllers; they shall not communicate with window
    directly.
    """

    logger: LoggerManager
    config: ConfigManager
    change_password: ChangePasswordController
    login: LoginController
    register: RegisterController
    totp: TOTPController
    password: PasswordManager
    window: Window

    def __init__(self):
        """
        Some fields cannot be initialized at all/ can be initialized only partially:
        - window:
            - created by webview.create_window, which requires as argument this class
            - set later using set_window()
        - totp:
            - requires user password for proper functioning
            - but needs to be set here so that it is seen as window.pywebview.api.totp
            - set later by LoginController/RegisterController using init_totp_controller()
        """
        self.logger = LoggerManager()
        self.config = ConfigManager()
        self.change_password = ChangePasswordController(self)
        self.login = LoginController(self)
        self.register = RegisterController(self)
        self.totp = TOTPController(self)
        self.password = PasswordManager()

    def set_window(self, window: Window):
        self.window = window

    def init_with_user_password(self, user_password: str):
        self.totp.init_with_user_password(user_password)
        self.change_password.init_with_user_password(user_password)

    def get_constants_handler(self):
        self.logger.log_enter("get_constants_handler")
        return Response.get_constants()

    def startup_handler(self):
        """
        Called when pywebview is ready => when UI is loaded.
        """
        self.logger.log_enter("startup_handler")
        if self.password.previous_password_exists():
            self.load_view(View.LOGIN)
        else:
            self.load_view(View.REGISTER)

    def load_view(self, view: View):
        """
        Tells JS to load the given view.
        """
        self.window.evaluate_js(f"loadView('{view.value}')")

    def open_image_dialog(self) -> str | None:
        """
        Opens a dialog (default file explorer), lets the user choose a file (preferably an image),
        returns the path of the selected file.
        See: https://pywebview.flowrl.com/examples/open_file_dialog.html.
        """
        result = self.window.create_file_dialog(
            webview.FileDialog.OPEN,
            allow_multiple=False,
            file_types=("Image Files (*.bmp;*.jpg;*.jpeg;*.png;*.gif)", "All files (*.*)")
        )
        if result is None:
            return None  # example: when user presses cancel
        return result[0]
