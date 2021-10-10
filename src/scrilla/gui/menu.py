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

from scrilla.gui.functions import RiskReturnWidget, CorrelationWidget, \
                                    MovingAverageWidget, EfficientFrontierWidget, \
                                    OptimizerWidget

# NOTE: widget_buttons and function_widgets must preserve order.
class MenuWidget(QtWidgets.QWidget):
    """
    
    .. notes::
        * Widget Hierarchy: 
            1. root_layout --> Vertically aligned
                a. container_layout --> Horizontally aligned
                    i. menu_layout --> Vertically aligned
                    ii. display_layout --> Vertically aligned
    """
    def __init__(self):
        super().__init__()
        
        self._init_menu_widgets()
        self._arrange_menu_widgets()
        self._stage_menu_widgets()

    def _init_menu_widgets(self):
        self.setObjectName('root')

        self.title = QtWidgets.QLabel("scrilla")
        self.title.setObjectName('title')

        self.menu_title = QtWidgets.QLabel('Functions')
        self.menu_title.setObjectName('menu-title')
        
        self.widget_buttons = [ QtWidgets.QPushButton("Correlation Matrix"),
                                QtWidgets.QPushButton("Efficient Frontier"),
                                QtWidgets.QPushButton("Moving Averages"),
                                QtWidgets.QPushButton("Portfolio Optimization"),
                                QtWidgets.QPushButton("Risk-Return Profile"),
                            ]
        self.exit_button = QtWidgets.QPushButton("Exit")
        self.exit_button.setObjectName('button')

        for button in self.widget_buttons:
            button.setObjectName('button')

        self.function_widgets = [ CorrelationWidget('great-grand-child'), 
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
        self.container_pane.layout().addWidget(self.menu_pane)
        self.container_pane.layout().addWidget(self.display_pane)

        self.container_pane.setSizePolicy(QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding,
                                                                QtWidgets.QSizePolicy.Expanding))
        self.menu_pane.setSizePolicy(QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum,
                                                            QtWidgets.QSizePolicy.Expanding))
        self.display_pane.setSizePolicy(QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding,
                                                            QtWidgets.QSizePolicy.Expanding))
        self.title.setSizePolicy(QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding,
                                                        QtWidgets.QSizePolicy.Minimum))

        self.layout().addWidget(self.title)
        self.layout().addWidget(self.container_pane)

        self.menu_pane.layout().addWidget(self.menu_title)
        for button in self.widget_buttons:
            self.menu_pane.layout().addWidget(button)
        self.menu_pane.layout().addStretch()
        self.menu_pane.layout().addWidget(self.exit_button)

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

    @QtCore.Slot()
    def _show_widget(self, widget_index):
        for widget in self.function_widgets:
            widget.hide()
        self.function_widgets[widget_index].show()

    @QtCore.Slot()
    def _clear(self):
        for widget in self.function_widgets:
            widget.hide()

if __name__ == "__main__":
    app = QtWidgets.QApplication([])

    mainWidget = MenuWidget()
    mainWidget.resize(settings.GUI_WIDTH, settings.GUI_HEIGHT)
    mainWidget.show()

    sys.exit(app.exec_())