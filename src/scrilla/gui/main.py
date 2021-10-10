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

from PySide6 import QtWidgets, QtGui
import scrilla.gui.menu as menu
from scrilla import settings
from scrilla.util import outputter

logger = outputter.Logger('main', settings.LOG_LEVEL)

def do_gui():
    app = QtWidgets.QApplication([])

    logger.debug(f'Initializing GUI with dimensions ({settings.GUI_WIDTH}, {settings.GUI_HEIGHT})')

    widget = menu.MenuWidget()
    widget.resize(settings.GUI_WIDTH, settings.GUI_HEIGHT)

    center = QtGui.QScreen.availableGeometry(QtWidgets.QApplication.primaryScreen()).center()
    geo = widget.frameGeometry()
    geo.moveCenter(center)
    widget.move(geo.topLeft())

    widget.show()

    sys.exit(app.exec_())

if __name__ == "__main__":
    do_gui()