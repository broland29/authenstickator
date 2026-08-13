from enum import Enum


class View(Enum):
    """
    Enum for each view. Value should be the relative path of the view's HTML file w.r.t. index.html.
    """
    LOGIN = "login.html"
    REGISTER = "register.html"
    TOTP = "totp.html"
