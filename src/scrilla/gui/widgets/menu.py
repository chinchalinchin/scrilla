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

from PySide6 import QtCore, QtWidgets, QtGui

from scrilla import settings

from scrilla.gui import formats
from scrilla.gui.widgets.functions import RiskReturnWidget, CorrelationWidget, \
                                            MovingAverageWidget, EfficientFrontierWidget, \
                                            OptimizerWidget

# NOTE: widget_buttons and function_widgets must preserve order.
class MenuWidget(QtWidgets.QWidget):
    """
    
    .. notes::
        * Widget Hierarchy: 

    """
    def __init__(self):
        super().__init__()
        self._init_menu_widgets()
        self._generate_menu_bar()
        self._arrange_menu_widgets()
        self._stage_menu_widgets()

    def _generate_menu_bar(self):
        self.api_key_action = QtGui.QAction('Add API Key', self)
        self.jpeg_export_action = QtGui.QAction('JPEG', self)
        self.json_export_action = QtGui.QAction('JSON', self)

        self.menu_bar = QtWidgets.QMenuBar(None)
        self.menu_bar.setObjectName('menu-bar')

        file = self.menu_bar.addMenu('File')
        view = self.menu_bar.addMenu('Function')
        preferences = self.menu_bar.addMenu('Preferences')

        self.function_actions = [ QtGui.QAction(function, self) for function in formats.FUNCTIONS ]
        for action in self.function_actions:
            view.addAction(action)

        export = file.addMenu('Export')

        self.api_key_action.setEnabled(True)
        self.jpeg_export_action.setEnabled(False)
        self.json_export_action.setEnabled(False)

        file.addAction(self.api_key_action)
        export.addAction(self.jpeg_export_action)
        export.addAction(self.json_export_action)

    def _init_menu_widgets(self):
        self.setObjectName('root')

        self.intro_msg = QtWidgets.QLabel("Select A Function To Get Started")
        self.intro_msg.setObjectName('title')

        self.title = QtWidgets.QLabel("scrilla")
        self.title.setObjectName('title')

        self.function_menu = QtWidgets.QLabel('Functions')
        self.function_menu.setObjectName('function-menu')
        
        
        self.widget_buttons = [ QtWidgets.QPushButton(function) for function in formats.FUNCTIONS ]

        self.exit_button = QtWidgets.QPushButton("Exit")
        self.exit_button.setObjectName('button')

        for button in self.widget_buttons:
            button.setObjectName('button')

        self.function_widgets = [ 
            CorrelationWidget('great-grand-child'), 
            EfficientFrontierWidget('great-grand-child'),
            MovingAverageWidget('great-grand-child'),
            OptimizerWidget('great-grand-child'),
            RiskReturnWidget('great-grand-child'),
        ]

        self.menu_pane = QtWidgets.QWidget()
        self.menu_pane.setLayout(QtWidgets.QVBoxLayout())
        self.menu_pane.setObjectName('grand-child')
        
        self.display_pane = QtWidgets.QWidget()
        self.display_pane.setLayout(QtWidgets.QVBoxLayout())
        self.display_pane.setObjectName('grand-child')

        self.container_pane = QtWidgets.QWidget()
        self.container_pane.setLayout(QtWidgets.QHBoxLayout())
        self.container_pane.setObjectName('child')

        self.setLayout(QtWidgets.QVBoxLayout())

    def _arrange_menu_widgets(self):
        """Arranges child widget within their layouts."""
        self.title.setAlignment(QtCore.Qt.AlignHCenter)
        self.intro_msg.setAlignment(QtCore.Qt.AlignCenter)
        self.function_menu.setAlignment(QtCore.Qt.AlignHCenter)

        self.container_pane.setSizePolicy(QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding,
                                                                QtWidgets.QSizePolicy.Expanding))
        self.menu_pane.setSizePolicy(QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum,
                                                            QtWidgets.QSizePolicy.Expanding))
        self.display_pane.setSizePolicy(QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding,
                                                            QtWidgets.QSizePolicy.Expanding))
        self.title.setSizePolicy(QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding,
                                                        QtWidgets.QSizePolicy.Minimum))

        self.container_pane.layout().addWidget(self.menu_pane)
        self.container_pane.layout().addWidget(self.display_pane)

        self.layout().addWidget(self.menu_bar)
        self.layout().addWidget(self.title)
        self.layout().addWidget(self.container_pane)

        self.menu_pane.layout().addWidget(self.function_menu)
        for button in self.widget_buttons:
            self.menu_pane.layout().addWidget(button)
        self.menu_pane.layout().addStretch()
        self.menu_pane.layout().addWidget(self.exit_button)

        self.display_pane.layout().addWidget(self.intro_msg)
        for widget in self.function_widgets:
            self.display_pane.layout().addWidget(widget)
        
    def _stage_menu_widgets(self):
        for i, button in enumerate(self.widget_buttons):
            button.show()
            button.setAutoDefault(True)
            button.clicked.connect((lambda i: lambda: self._show_widget(i))(i))
            button.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        for widget in self.function_widgets:
            widget.hide()
        self.exit_button.clicked.connect(self.close)
        self.exit_button.show()
        self.menu_bar.show()

    @QtCore.Slot()
    def _show_widget(self, widget_index):
        self.intro_msg.hide()
        for widget in self.function_widgets:
            widget.hide()
        self.function_widgets[widget_index].show()

    @QtCore.Slot()
    def _clear(self):
        for widget in self.function_widgets:
            widget.hide()
        self.intro_msg.show()

if __name__ == "__main__":
    app = QtWidgets.QApplication([])

    mainWidget = MenuWidget()
    mainWidget.resize(settings.GUI_WIDTH, settings.GUI_HEIGHT)
    mainWidget.show()

    sys.exit(app.exec_())