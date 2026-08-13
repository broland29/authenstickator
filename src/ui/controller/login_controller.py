from src.ui.controller.response import Response


class LoginController:

    def __init__(self):
        self.window = None

    def set_window(self, window):
        self.window = window

    def verify_password_handler(self, password):
        # TODO: implement
        return Response.success(password)
