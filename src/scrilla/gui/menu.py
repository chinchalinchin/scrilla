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

def get_title_font():
    font = QtGui.QFont('Times', 12, QtGui.QFont.Bold)
    font.bold()
    return font

# NOTE: widget_buttons and function_widgets must preserve order.
class MenuWidget(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        
        self.init_widgets()
        self.arrange_widgets()
        self.style_widgets()

        for button in self.widget_buttons:
            button.setAutoDefault(True)
            if self.widget_buttons.index(button) == 0:
                button.clicked.connect(lambda: self.show_widget(0))
            elif self.widget_buttons.index(button) == 1:
                button.clicked.connect(lambda: self.show_widget(1))
            elif self.widget_buttons.index(button) == 2:
                button.clicked.connect(lambda: self.show_widget(2))
            elif self.widget_buttons.index(button) == 3:
                button.clicked.connect(lambda: self.show_widget(3))
            elif self.widget_buttons.index(button) == 4:
                button.clicked.connect(lambda: self.show_widget(4))

    def init_widgets(self):
        self.title = QtWidgets.QLabel("scrilla", alignment=QtCore.Qt.AlignTop)

        self.back_button = QtWidgets.QPushButton("Menu")

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

    def arrange_widgets(self):
        """
        Arranges children in the component hierarchy and specifies their layout.
        
        .. notes::
            * Menu Layout: 
                1. Root Pane --> Vertically aligned
                    a. Container Pane --> Horizontally aligned
                        i. Menu Pane --> Vertically aligned
                        ii. Display Pane --> Vertically aligned
        """
        self.menu_layout = QtWidgets.QVBoxLayout()
        self.display_layout = QtWidgets.QVBoxLayout()
        self.container_layout = QtWidgets.QHBoxLayout()
        self.layout = QtWidgets.QVBoxLayout()

        self.menu_pane.setLayout(self.menu_layout)
        self.display_pane.setLayout(self.display_layout)
        self.container_pane.setLayout(self.container_layout)

        self.container_layout.addWidget(self.menu_pane)
        self.container_layout.addWidget(self.display_pane)

        self.layout.addWidget(self.title)
        self.layout.addWidget(self.container_pane)
        self.layout.addStretch()
        self.setLayout(self.layout)

        for button in self.widget_buttons:
            self.menu_layout.addWidget(button)
            button.show()
        self.menu_layout.addStretch()

        for widget in self.function_widgets:
            widget.hide()
            self.display_layout.addWidget(widget)
        
        self.setLayout(self.layout)



    def style_widgets(self):
        self.title.setFont(get_title_font())

    @QtCore.Slot()
    def show_widget(self, widget_index):
        for widget in self.function_widgets:
            widget.hide()
        self.function_widgets[widget_index].show()

    @QtCore.Slot()
    def clear(self):
        for widget in self.function_widgets:
            widget.hide()
            # TODO: widget.clear_contents() -> erase all saved data

if __name__ == "__main__":
    app = QtWidgets.QApplication([])

    mainWidget = MenuWidget()
    mainWidget.resize(settings.GUI_WIDTH, settings.GUI_HEIGHT)
    mainWidget.show()

    sys.exit(app.exec_())