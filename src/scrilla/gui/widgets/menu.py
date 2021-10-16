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

from scrilla.gui import formats, utilities
from scrilla.gui.widgets import factories

# NOTE: widget_buttons and function_widgets must preserve order.
class MenuWidget(QtWidgets.QWidget):
    """
    
    .. notes::
        * Widget Hierarchy: 

    .. links::
        * [Stack Overflow: Weird Lambda Behavior in Loops](https://stackoverflow.com/questions/19768456/weird-lambda-behaviour-in-loops)
    """
    def __init__(self):
        super().__init__()
        self._init_menu_widgets()
        self._generate_menu_bar()
        self._arrange_menu_widgets()
        self._stage_menu_widgets()

    def _generate_menu_bar(self):
        self.menu_bar = factories.atomic_widget_factory(format='menu-bar', title=None)
        self.menus = []

        for j, menu in enumerate(formats.MENUBAR_WIDGET):
            self.menus.append(self.menu_bar.addMenu(menu))
            for i, action in enumerate(formats.MENUBAR_WIDGET[menu]):
                q_action = QtGui.QAction(action['name'], self)
                q_action.setShortcut(action['shortcut'])
                if menu == 'Functions':
                    q_action.triggered.connect((lambda i: lambda: self._show_widget(i))(i))
                elif menu== 'File':
                    pass
                elif menu == 'View':
                    if action['name'] == 'Function Menu':
                        q_action.triggered.connect(lambda: self.function_menu.show())
                self.menus[j].addAction(q_action)

    def _init_menu_widgets(self):
        self.setObjectName('root')
        self.intro_msg = factories.atomic_widget_factory(format='title', title="Select A Function To Get Started")
        self.title = factories.atomic_widget_factory(format='title', title=settings.APP_NAME)

        self.function_menu = factories.layout_factory(format='vertical-box')
        self.function_menu.setObjectName('grand-child')
        self.function_title_container = factories.layout_factory(format='horizontal-box')
        self.function_title = factories.atomic_widget_factory(format='heading', title='Functions')
        self.function_hide_button = factories.atomic_widget_factory(format='hide-button', title=None)
        
        self.widget_buttons = [ factories.atomic_widget_factory(format='button', title=function['name']) for function in formats.FUNC_WIDGETS.values() ]
        self.exit_button = factories.atomic_widget_factory(format='button', title="Exit")

        self.function_widgets = [ function['class']('great-grand-child', self) for function in formats.FUNC_WIDGETS.values() ]

        self.display_pane = factories.layout_factory(format='vertical-box')
        self.display_pane.setObjectName('grand-child')

        self.container_pane = factories.layout_factory(format='horizontal-box')
        self.container_pane.setObjectName('child')

        self.setLayout(QtWidgets.QVBoxLayout())

    def _arrange_menu_widgets(self):
        """Arranges child widget within their layouts."""
        self.title.setAlignment(QtCore.Qt.AlignHCenter)
        self.intro_msg.setAlignment(QtCore.Qt.AlignCenter)

        self.container_pane.setSizePolicy(QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding,
                                                                QtWidgets.QSizePolicy.Expanding))
        self.function_menu.setSizePolicy(QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum,
                                                            QtWidgets.QSizePolicy.Expanding))
        self.display_pane.setSizePolicy(QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding,
                                                            QtWidgets.QSizePolicy.Expanding))
        self.title.setSizePolicy(QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding,
                                                        QtWidgets.QSizePolicy.Minimum))

        self.container_pane.layout().addWidget(self.function_menu)
        self.container_pane.layout().addWidget(self.display_pane)

        self.layout().addWidget(self.menu_bar)
        self.layout().addWidget(self.title)
        self.layout().addWidget(self.container_pane)

        self.function_title_container.layout().addWidget(self.function_title)
        self.function_title_container.layout().addWidget(self.function_hide_button)
        self.function_menu.layout().addWidget(self.function_title_container)
        for button in self.widget_buttons:
            self.function_menu.layout().addWidget(button)
        self.function_menu.layout().addStretch()
        self.function_menu.layout().addWidget(self.exit_button)

        self.display_pane.layout().addWidget(self.intro_msg)
        for widget in self.function_widgets:
            self.display_pane.layout().addWidget(widget)
        
    def _stage_menu_widgets(self):
        for i, button in enumerate(self.widget_buttons):
            button.show()
            # see #NOTE
            button.clicked.connect((lambda i: lambda: self._show_widget(i))(i))

        for widget in self.function_widgets:
            widget.hide()

        self.function_hide_button.clicked.connect(lambda: utilities.switch_visibility(self.function_menu))
        self.exit_button.clicked.connect(self.close)
        self.exit_button.show()
        self.menu_bar.show()

    @QtCore.Slot()
    def _show_widget(self, widget_index):
        self.intro_msg.hide()
        for widget in self.function_widgets:
            widget.hide()
        self.function_widgets[widget_index].show()
        print(list(formats.FUNC_WIDGETS.values())[widget_index])
        self.title.setText(list(formats.FUNC_WIDGETS.values())[widget_index]['name'])

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