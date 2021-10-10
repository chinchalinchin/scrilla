from PySide6.QtGui import QPixmap
from PySide6.QtCore import Qt

from scrilla import settings

def calculate_image_width() -> float:
    return 4*settings.GUI_WIDTH/5

def calculate_image_height() -> float:
    return 4*settings.GUI_HEIGHT/5

def generate_pixmap_from_cache() -> QPixmap:
    pixmap = QPixmap(settings.CACHE_TEMP_FILE)
    pixmap = pixmap.scaled(calculate_image_width(), calculate_image_height(), aspectMode=Qt.KeepAspectRatio)
    return pixmap

