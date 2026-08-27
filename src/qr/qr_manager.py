from PIL import Image
from pyzbar.pyzbar import decode

from src.logger.logger_manager import LoggerManager


class QRManager:
    """
    Singleton responsible for decoding (extracting text from) a QR code image.
    """
    instance = None
    logger = LoggerManager

    def __new__(cls):
        if cls.instance is not None:
            return cls.instance

        cls.instance = super().__new__(cls)
        cls.instance.logger = LoggerManager()

        return cls.instance

    def decode(self, image_path) -> str | None:
        """
        Decodes the image at image_path. Returns None on failure.
        """
        try:
            image = Image.open(image_path)
        except FileNotFoundError:
            self.logger.error(f"Image {image_path} not found.")
            return None
        decoded_list = decode(image)  # returns a list, we only care about first, and its data attr.
        if len(decoded_list) == 0:
            self.logger.error(f"Image {image_path} did not contain any QR codes.")
            return None
        if len(decoded_list) > 1:
            self.logger.warning(f"Read multiple QR codes, processing only first")
        decoded_bytes = decoded_list[0].data
        return decoded_bytes.decode("utf-8")
