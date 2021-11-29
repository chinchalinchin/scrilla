import shutil
import json

from PySide6 import QtWidgets
from PySide6.QtGui import QPixmap
from PySide6.QtCore import Qt

from scrilla import settings

import webbrowser


def calculate_image_width(width) -> float:
    return 9*width/10


def calculate_image_height(height) -> float:
    return 9*height/10


def open_browser(link):
    webbrowser.open(link)


def generate_pixmap_from_temp(width, height, ext) -> QPixmap:
    pixmap = QPixmap(f'{settings.TEMP_DIR}/{ext}')
    pixmap = pixmap.scaled(calculate_image_width(
        width), calculate_image_height(height), aspectMode=Qt.KeepAspectRatio)
    return pixmap


def get_metadata(key) -> str:
    with open(settings.METADATA_FILE, 'r') as f:
        dict_format = json.load(f)
    return dict_format[key]


def load_html_template(template_key):
    with open(f'{settings.GUI_TEMPLATE_DIR}/{template_key}.html', 'r') as f:
        html = f.read()
    return html


def download_tmp_to_file(tmp_key, dest):
    shutil.copy(f'{settings.TEMP_DIR}/{tmp_key}', dest)


def download_table_to_json(qtable: QtWidgets.QTableWidget, dest) -> None:
    result = {}
    for row in range(qtable.rowCount()):
        row_header = qtable.verticalHeaderItem(row).text()
        result[row_header] = {}
        for column in range(qtable.columnCount()):
            column_header = qtable.horizontalHeaderItem(column).text()
            result[row_header][column_header] = qtable.item(row, column).text()

    with open(dest, 'w') as f:
        json.dump(result, f)


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
