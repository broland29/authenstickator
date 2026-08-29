import webview
from webview import Window

from src.controller.change_password_controller import ChangePasswordController
from src.controller.errors import Errors
from src.controller.login_controller import LoginController
from src.controller.register_controller import RegisterController
from src.controller.response import Response, ResponseType
from src.controller.totp_controller import TOTPController
from src.controller.view_path import ViewPath
from src.model.config.config_manager import ConfigManager
from src.model.encryptor.encryptor import Encryptor
from src.model.logger.logger_manager import LoggerManager
from src.model.password.password_manager import PasswordManager
from src.model.storage.storage_manager import StorageManager
from src.model.tpm.tpm import TPM


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

    Variables with dunder are like this for a purpose: if window is without _, pywebview on
    Windows crashes :D (it tries to serialize it to JSON so JavaScript can access it,
    or something like that)
    """
    _logger: LoggerManager
    _config: ConfigManager
    change_password: ChangePasswordController
    login: LoginController
    register: RegisterController
    totp: TOTPController
    _window: Window

    def __init__(self):
        """
        Some fields cannot be initialized at all/ can be initialized only partially:
        - window:
            - created by webview.create_window, which requires as argument this class
            - set later using set_window()
        - totp, change_password:
            - they require user password for proper functioning
            - but they need to be set here so that it is seen by js (ex: window.pywebview.api.totp)
            - set later by LoginController/RegisterController using init_with_user_password()
        """
        self._logger = LoggerManager()
        self._config = ConfigManager()
        self.change_password = ChangePasswordController(self)
        self.login = LoginController(self)
        self.register = RegisterController(self)
        self.totp = TOTPController(self)

    def set_window(self, window: Window):
        """
        To be called when window ready.
        """
        self._window = window

    def init_with_user_password(self, user_password: str) -> ResponseType:
        """
        Updates encryptor and storage due to user password change.

        Shall be called at each user password change. Change, in this context,  means that it was
        either provided for registration and accepted, provided for login and accepted, or it was
        actually changed and accepted.
        """
        self._logger.log_enter("init_with_user_password")

        # Retrieve TPM secret.
        tpm = TPM()
        if tpm is None:
            return Response.error("Encountered a TPM error. Try provisioning or disabling TPM.")
        tpm_secret = tpm.get_secret()
        if tpm_secret is None:
            return Response.error("Encountered a TPM error. Try provisioning or disabling TPM.")

        # Update encryptor since user password changed.
        encryptor = Encryptor(user_password, tpm_secret)

        # Update storage since encryptor changed. Implicitly re-encrypts (re-saved) storage file.
        storage = StorageManager(encryptor)
        if storage is None:
            return Response.error(Errors.ERROR_DECRYPT)

        self.totp.init(storage)

        return Response.success("Initialization successful.")

    def get_response_constants(self) -> dict[str, str]:
        """
        Method which sends response constants to UI upon startup.
        """
        self._logger.log_enter("get_response_constants")
        return Response.get_constants()

    def get_view_path_constants(self) -> dict[str, str]:
        """
        Method which sends HTML path constants to UI upon startup.
        """
        self._logger.log_enter("get_view_path_constants")
        return ViewPath.get_constants()

    def startup_handler(self) -> ResponseType:
        """
        Called when pywebview is ready => when UI is loaded.
        """
        self._logger.log_enter("startup_handler")
        password = PasswordManager()
        if password.previous_password_exists():
            self.load_view(ViewPath.LOGIN)
        else:
            self.load_view(ViewPath.REGISTER)
        return Response.success("Startup successful")

    def load_view(self, view_path: str):
        """
        Tells JS to load the given html.
        """
        self._window.evaluate_js(f"loadView('{view_path}')")

    def open_image_dialog(self) -> str | None:
        """
        Opens a dialog (default file explorer), lets the user choose a file (preferably an image),
        returns the path of the selected file.
        See: https://pywebview.flowrl.com/examples/open_file_dialog.html.
        """
        result = self._window.create_file_dialog(
            webview.FileDialog.OPEN,
            allow_multiple=False,
            file_types=("Image Files (*.bmp;*.jpg;*.jpeg;*.png;*.gif)", "All files (*.*)")
        )
        if result is None:
            return None  # example: when user presses cancel
        return result[0]
