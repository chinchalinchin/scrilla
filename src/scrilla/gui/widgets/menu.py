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

from scrilla.gui import formats, utilities, definitions
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
        self._generate_splash()
        self._arrange_menu_widgets()
        self._stage_menu_widgets()

    def _generate_menu_bar(self):
        self.menu_bar = factories.atomic_widget_factory(
            component='menu-bar', title=None)
        self.menus = []

        for j, menu in enumerate(definitions.MENUBAR_WIDGET):
            self.menus.append(self.menu_bar.addMenu(menu))
            for i, action in enumerate(definitions.MENUBAR_WIDGET[menu]):
                q_action = QtGui.QAction(action['name'], self)
                q_action.setShortcut(action['shortcut'])
                if menu == 'Functions':
                    q_action.triggered.connect(
                        (lambda i: lambda: self._show_widget(i))(i))
                elif menu == 'Account':
                    pass
                elif menu == 'View':
                    if action['name'] == 'Function Menu':
                        q_action.triggered.connect(lambda: self.function_menu.setVisible(
                            (not self.function_menu.isVisible())))
                    elif action['name'] == 'Splash Menu':
                        q_action.triggered.connect(self._clear)

                self.menus[j].addAction(q_action)

    def _generate_splash(self):
        self.splash_container = factories.layout_factory(layout='vertical-box')
        self.source_button = factories.atomic_widget_factory(
            component='source-button', title=None)
        self.package_button = factories.atomic_widget_factory(
            component='package-button', title=None)
        self.documentation_button = factories.atomic_widget_factory(
            component='documentation-button', title=None)
        self.splash = factories.atomic_widget_factory(
            component='splash', title=None)

        self.splash_button_panel = factories.layout_factory(
            layout='horizontal-box')

        self.splash_button_panel.layout().addStretch()
        self.splash_button_panel.layout().addWidget(self.source_button)
        self.splash_button_panel.layout().addWidget(self.package_button)
        self.splash_button_panel.layout().addWidget(self.documentation_button)
        self.splash_button_panel.layout().addStretch()

    def _init_menu_widgets(self):
        self.setObjectName('root')
        self.title = factories.atomic_widget_factory(
            component='title', title=settings.APP_NAME)

        self.function_menu = factories.layout_factory(layout='vertical-box')
        self.function_menu.setObjectName('grand-child')
        self.function_title_container = factories.layout_factory(
            layout='horizontal-box')
        self.function_title = factories.atomic_widget_factory(
            component='heading', title='Functions')
        self.function_hide_button = factories.atomic_widget_factory(
            component='hide-button', title=None)

        self.widget_buttons = [factories.atomic_widget_factory(
            component='button', title=function['name']) for function in definitions.FUNC_WIDGETS.values()]
        self.exit_button = factories.atomic_widget_factory(
            component='button', title="Exit")

        self.function_widgets = [function['class'](
            'great-grand-child', self) for function in definitions.FUNC_WIDGETS.values()]

        self.display_pane = factories.layout_factory(layout='vertical-box')
        self.display_pane.setObjectName('grand-child')

        self.container_pane = factories.layout_factory(layout='horizontal-box')
        self.container_pane.setObjectName('child')

        self.setLayout(QtWidgets.QVBoxLayout())

    def _arrange_menu_widgets(self):
        """Arranges child widget within their layouts."""
        self.title.setAlignment(QtCore.Qt.AlignHCenter)
        # self.splash.setAlignment(QtCore.Qt.AlignCenter)

        self.container_pane.setSizePolicy(QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding,
                                                                QtWidgets.QSizePolicy.Expanding))
        self.function_menu.setSizePolicy(QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum,
                                                               QtWidgets.QSizePolicy.Expanding))
        self.display_pane.setSizePolicy(QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding,
                                                              QtWidgets.QSizePolicy.Expanding))
        self.title.setSizePolicy(QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding,
                                                       QtWidgets.QSizePolicy.Minimum))

        self.function_title_container.layout().addWidget(self.function_title)
        self.function_title_container.layout().addWidget(self.function_hide_button)

        self.function_menu.layout().addWidget(self.function_title_container)
        for button in self.widget_buttons:
            self.function_menu.layout().addWidget(button)
        self.function_menu.layout().addStretch()
        self.function_menu.layout().addWidget(self.exit_button)

        self.splash_container.layout().addWidget(self.splash)
        self.splash_container.layout().addStretch()
        self.splash_container.layout().addWidget(self.splash_button_panel)

        self.display_pane.layout().addWidget(self.splash_container)
        for widget in self.function_widgets:
            self.display_pane.layout().addWidget(widget)

        self.container_pane.layout().addWidget(self.function_menu)
        self.container_pane.layout().addWidget(self.display_pane)

        self.layout().addWidget(self.menu_bar)
        self.layout().addWidget(self.title)
        self.layout().addWidget(self.container_pane)

    def _stage_menu_widgets(self):
        for i, button in enumerate(self.widget_buttons):
            button.show()
            # see #NOTE
            button.clicked.connect((lambda i: lambda: self._show_widget(i))(i))

        for widget in self.function_widgets:
            widget.hide()

        self.function_hide_button.clicked.connect(
            lambda: utilities.switch_visibility(self.function_menu))
        self.exit_button.clicked.connect(self.close)
        self.source_button.clicked.connect(
            lambda: utilities.open_browser(utilities.get_metadata('source')))
        self.package_button.clicked.connect(
            lambda: utilities.open_browser(utilities.get_metadata('package')))
        self.documentation_button.clicked.connect(
            lambda: utilities.open_browser(utilities.get_metadata('documentation')))
        self.exit_button.show()
        self.menu_bar.show()

    def _clear(self):
        for widget in self.function_widgets:
            widget.hide()
        self.splash_container.show()

    @QtCore.Slot()
    def _show_widget(self, widget_index):
        self.splash_container.hide()
        for widget in self.function_widgets:
            widget.hide()
        self.function_widgets[widget_index].show()
        self.title.setText(list(definitions.FUNC_WIDGETS.values())[
                           widget_index]['name'])


if __name__ == "__main__":
    app = QtWidgets.QApplication([])

    mainWidget = MenuWidget()
    mainWidget.resize(settings.GUI_WIDTH, settings.GUI_HEIGHT)
    mainWidget.show()

    sys.exit(app.exec_())
