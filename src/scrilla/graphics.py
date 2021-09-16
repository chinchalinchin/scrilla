import sys

from PyQt5 import QtWidgets
import scrilla.gui.menu as menu
from scrilla import settings

def do_gui():
    app = QtWidgets.QApplication([])

    widget = menu.MenuWidget()
    widget.resize(settings.GUI_WIDTH, settings.GUI_HEIGHT)
    widget.show()

    sys.exit(app.exec_())