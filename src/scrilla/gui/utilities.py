from PySide6.QtGui import QPixmap
from PySide6.QtCore import Qt

from scrilla import settings

def calculate_image_width(width) -> float:
    return 7*width/10

def calculate_image_height(height) -> float:
    return 7*height/10

def generate_pixmap_from_temp(width, height, ext) -> QPixmap:
    pixmap = QPixmap(f'{settings.TEMP_DIR}/{ext}')
    pixmap = pixmap.scaled(calculate_image_width(width), calculate_image_height(height), aspectMode=Qt.KeepAspectRatio)
    return pixmap

