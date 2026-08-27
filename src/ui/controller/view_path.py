from typing import Final


class ViewPath:
    """
    The path to each view (HTML) file w.r.t. index.html.
    """
    CHANGE_PASSWORD: Final[str] = "changepassword.html"
    LOGIN: Final[str] = "login.html"
    REGISTER: Final[str] = "register.html"
    TOTP: Final[str] = "totp.html"

    @staticmethod
    def get_constants() -> dict[str, str]:
        return {
            "CHANGE_PASSWORD": ViewPath.CHANGE_PASSWORD,
            "LOGIN": ViewPath.LOGIN,
            "REGISTER": ViewPath.REGISTER,
            "TOTP": ViewPath.TOTP
        }
