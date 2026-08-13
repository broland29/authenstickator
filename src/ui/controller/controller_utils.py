from webview import Window

from src.ui.controller.view import View


class ControllerUtils:
    @staticmethod
    def load_view(window: Window, view: View):
        """
        Tells JS to load the given view.
        """
        window.evaluate_js(f"loadView('{view.value}')")
