from typing import Final


class Response:
    """
    Return value of API calls - communication convention between UI and backend.
    """
    STATUS_SUCCESS: Final[str] = "STATUS_SUCCESS"
    STATUS_ERROR: Final[str] = "STATUS_ERROR"

    @staticmethod
    def success(success_message="", data=None):
        """
        A successful API call returns success status and, optionally, a success message to display
        for the user + data if the called method should return anything.
        """
        return {
            "status": Response.STATUS_SUCCESS,
            "success_message": success_message,
            "data": data
        }

    @staticmethod
    def error(error_message=None):
        """
        An unsuccessful API call returns error status and an error message to display for the user.
        """
        return {
            "status": Response.STATUS_ERROR,
            "error_message": error_message
        }

    @staticmethod
    def get_constants() -> dict:
        """
        Gets the constants representing used for status in API responses.
        """
        return {
            "STATUS_SUCCESS": Response.STATUS_SUCCESS,
            "STATUS_ERROR": Response.STATUS_ERROR,
        }
