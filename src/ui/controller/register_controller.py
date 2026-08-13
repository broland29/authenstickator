from src.hasher.hasher import Hasher
from src.ui.controller.response import Response
from src.ui.controller.view import View


class RegisterController:
    def __init__(self):
        self.hasher = Hasher()
        self.window = None

    def set_window(self, window):
        self.window = window

    def new_password_handler(self, password):
        if not self.is_password_complex_enough(password):
            return Response.error("Password is not complex enough")

        return Response.success("Password is valid", View.TOTP.value)

    @staticmethod
    def is_password_complex_enough(password):
        # TODO: add password complexity check.
        return len(password) > 1
