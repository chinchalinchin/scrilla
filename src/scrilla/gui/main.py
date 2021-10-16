# This file is part of scrilla: https://github.com/chinchalinchin/scrilla.

# scrilla is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 3
# as published by the Free Software Foundation.

# scrilla is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with scrilla.  If not, see <https://www.gnu.org/licenses/>
# or <https://github.com/chinchalinchin/scrilla/blob/develop/main/LICENSE>.

import sys
import argparse

from PySide6 import QtWidgets, QtGui
from scrilla import settings
from scrilla.util import outputter
from scrilla.gui import formats
import scrilla.gui.widgets.menu as menu

logger = outputter.Logger('main', settings.LOG_LEVEL)


def parse_dimensions():
    parser = argparse.ArgumentParser()
    parser.add_argument('--full-screen', '-full-screen', '--full',
                        '-full', action='store_true', dest='full_screen')
    parser.add_argument('--width', '-width', '--w', type=int,
                        dest='width', default=settings.GUI_WIDTH)
    parser.add_argument('--height', '-height', '--h', type=int,
                        dest='height', default=settings.GUI_HEIGHT)
    return vars(parser.parse_args())


def do_gui():
    dimensions = parse_dimensions()

    app = QtWidgets.QApplication([])

    widget = menu.MenuWidget()

    with open(settings.GUI_STYLESHEET_FILE, "r") as f:
        _style = formats.format_stylesheet(f.read())
        app.setStyleSheet(_style)

    logger.debug(f'Initializing GUI with style sheet: {_style}')

    if not dimensions['full_screen']:
        widget.resize(dimensions['width'], dimensions['height'])
        center = QtGui.QScreen.availableGeometry(
            QtWidgets.QApplication.primaryScreen()).center()
        geo = widget.frameGeometry()
        geo.moveCenter(center)
        widget.move(geo.topLeft())
        widget.show()

    else:
        widget.showFullScreen()

    sys.exit(app.exec_())


if __name__ == "__main__":
    do_gui()
