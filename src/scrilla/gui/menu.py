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
        self._style_menu_widgets()
        self._arrange_menu_widgets()
        self._stage_menu_widgets()

    def _init_menu_widgets(self):
        self.title = QtWidgets.QLabel("scrilla", alignment=QtCore.Qt.AlignTop)

        self.widget_buttons = [ QtWidgets.QPushButton("Correlation Matrix"),
                                QtWidgets.QPushButton("Efficient Frontier"),
                                QtWidgets.QPushButton("Moving Averages"),
                                QtWidgets.QPushButton("Portfolio Optimization"),
                                QtWidgets.QPushButton("Risk-Return Profile"),
                            ]

        self.function_widgets = [ CorrelationWidget(), 
                                  EfficientFrontierWidget(),
                                  MovingAverageWidget(),
                                  OptimizerWidget(),
                                  RiskReturnWidget(),
                            ]

        self.menu_pane = QtWidgets.QWidget()
        self.display_pane = QtWidgets.QWidget()
        self.container_pane = QtWidgets.QWidget()

        self.menu_layout = QtWidgets.QVBoxLayout()
        self.display_layout = QtWidgets.QVBoxLayout()
        self.container_layout = QtWidgets.QHBoxLayout()
        self.root_layout = QtWidgets.QVBoxLayout()

        self.menu_pane.setLayout(self.menu_layout)
        self.display_pane.setLayout(self.display_layout)
        self.container_pane.setLayout(self.container_layout)
        self.setLayout(self.root_layout)


    def _style_menu_widgets(self):
        """Sets fonts and styles on child widgets"""
        self.title.setFont(formats.get_font_style(formats.STYLES['TITLE']))

    def _arrange_menu_widgets(self):
        """Arranges child widget within their layouts."""
        self.container_layout.addWidget(self.menu_pane)
        self.container_layout.addWidget(self.display_pane)

        self.root_layout.addWidget(self.title)
        self.root_layout.addStretch()
        self.root_layout.addWidget(self.container_pane)
        self.root_layout.addStretch()

        self.menu_layout.addStretch()
        for button in self.widget_buttons:
            self.menu_layout.addWidget(button)
        self.menu_layout.addStretch()

        self.display_layout.addStretch()
        for widget in self.function_widgets:
            self.display_layout.addWidget(widget)
        self.display_layout.addStretch()
        
    def _stage_menu_widgets(self):
        for i, button in enumerate(self.widget_buttons):
            button.show()
            button.setAutoDefault(True)
            button.clicked.connect((lambda i: lambda: self._show_widget(i))(i))
        for widget in self.function_widgets:
            widget.hide()

    @QtCore.Slot()
    def _show_widget(self, widget_index):
        print(widget_index)
        for widget in self.function_widgets:
            widget.hide()
        self.function_widgets[widget_index].show()

    @QtCore.Slot()
    def _clear(self):
        for widget in self.function_widgets:
            widget.hide()
            # TODO: widget.clear_contents() -> erase all saved data

if __name__ == "__main__":
    app = QtWidgets.QApplication([])

    mainWidget = MenuWidget()
    mainWidget.resize(settings.GUI_WIDTH, settings.GUI_HEIGHT)
    mainWidget.show()

    sys.exit(app.exec_())