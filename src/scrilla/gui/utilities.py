from PySide6 import QtWidgets
from PySide6.QtGui import QPixmap
from PySide6.QtCore import Qt

from scrilla import settings

def calculate_image_width(width) -> float:
    return 9*width/10

def calculate_image_height(height) -> float:
    return 9*height/10

def generate_pixmap_from_temp(width, height, ext) -> QPixmap:
    pixmap = QPixmap(f'{settings.TEMP_DIR}/{ext}')
    pixmap = pixmap.scaled(calculate_image_width(width), calculate_image_height(height), aspectMode=Qt.KeepAspectRatio)
    return pixmap

def get_next_layer(layer):
    if layer == "root":
        return "child"
    if layer == "child":
        return "grand-child"
    return f'great-{layer}'

def switch_visibility(widget: QtWidgets.QWidget):
    if widget.isVisible():
        widget.hide()
    else:
        widget.show()