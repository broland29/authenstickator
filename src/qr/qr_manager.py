import zxingcpp
from PIL import Image

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
        results = zxingcpp.read_barcodes(image)
        if len(results) == 0:
            self.logger.error(f"Image {image_path} did not contain any QR codes.")
            return None
        if len(results) > 1:
            self.logger.warning(f"Read multiple QR codes, processing only first")
        return results[0].text
