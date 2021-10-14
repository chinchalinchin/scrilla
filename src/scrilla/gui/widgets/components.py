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

import datetime
from typing import Callable, Dict, List, Union
from PySide6 import QtCore, QtWidgets, QtGui

from scrilla.util import helper
from scrilla.gui import utilities
from scrilla.static import definitions
from scrilla.gui.widgets import factories

"""
A series of classes that all inherit from ``PySide6.QtWidgets.QWidget` and build up in sequence the necessary functionality to grab and validate user input, calculate and display results, etc. These widgets are not directly displayed on the GUI; rather, they are used as building blocks by the `scrilla.gui.functions` module, to create widgets specifically for application functions.

All widgets have a similar structure in that they call a series of methods tailored to their specific class: 
    1. **_init**
        Child widgets are constructed. Layouts are created.
    2. **_arrange**
        Child widgets are arranged. Layouts are applied.
    3. **_stage**
        Child widgets are prepped for display.

The idea behind the module is to hide as much widget initialization and styling as possible behind its functions, so the `scrilla.gui.functions` module can focus on application-level logic and isn't cluttered with ugly declarative configuration.

Widgets have styles applied to them through the `scrilla.styles.app.qss` stylesheet. Widgets are layered over one another in a hierarchy described by: `root` -> `child` -> `grand-child` -> `great-grand-child` -> etc. Each layers has a theme that descends down the material color scheme hex codes in sequence with its place in the layer hierarchy. See `scrilla.gui.formats` for more information. 
"""

class ArgumentWidget(QtWidgets.QWidget):
    """
    Base class for other more complex widgets to inherit. An instance of `scrilla.gui.widgets.ArgumentWidget` embeds its child widgets in its own layout,  which is an instance of``PySide6.QtWidgetQVBoxLayout``. This class provides access to the following widgets:a ``PySide6.QtWidgets.QLabel`` for the title widget, an error message widget, a ``PySide6.QtWidgets.QPushButton`` for the calculate button widget, a ``PySide6.QtWidget.QLineEdit`` for ticker symbol input, and a variety of optional input widgets enabled by boolean flags in the `controls` constructor argument. 
    
    Constructor
    -----------
    1. **calculate_function**: ``str``
        Function attached to the `calculate_button` widget. Triggered when the widget is clicked.
    2. **clear_function**: ``str``
        Function attached to the `clear_button` widget. Trigged when the widget is clicked.
    3. **controls:**: ``Dict[bool]``
        Dictionary of boolean flags instructing the class which optional input to include. Optional keys can be found in `scrilla.static.definitions.ARG_DICT`. An dictionary skeleton with all the optional input disabled can be retrieved through `scrilla.gui.widgets.factories.generate_control_skeleton`.
    4. **layer**: ``str``
        Stylesheet property attached to widget.

    Attributes
    ----------
    1. **title**: ``PySide6.QtWidgets.QLabel``
    2. **required_title**: ``PySide6.QtWidgets.QLabel``
    3. **optional_title**: ``PySide6.QtWidgets.QLabel``
    4. **required_pane**: ``PySide6.QtWidgets.QLabel``
    5. **optional_pane**: ``PySide6.QtWidgets.QLabel``
    6. **message**: ``PySide6.QtWidgets.QLabel``
        Label attached to `self.symbol_input`.
    7. **error_message**: ``PySide6.QtWidget.QLabel``
        Message displayed if there is an error thrown during calculation.
    8. **calculate_button**: ``PySide6.QtWidget.QPushButton``
        Empty button for super classes to inherit, primed to fire events on return presses
    9. **clear_button**: ``PySide6.QtWidget.QPushButton``
        Empty button for super classes to inherit, primed to fire events on return presses.
    10. **symbol_widget**: ``PySide6.QtWidget.QLineEdit``
        Empty text area for super classes to inherit
    11. **control_widgets**: ``Dict[str,Union[PySide6.QtWidgets.QWidget,None]]
        Dictionary containing the optional input widgets.
    """
    # TODO: calculate and clear should be part of THIS constructor, doesn't make sense to have other widgets hook them up.
    def __init__(self, calculate_function: Callable, clear_function: Callable, controls: Dict[str, bool], layer):
        super().__init__()
        self.layer = layer
        self.controls = controls
        self.control_widgets = {}
        self.calculate_function = calculate_function
        self.clear_function = clear_function

        self._init_widgets()
        self._arrange_widgets()
        self._stage_widgets()
    
    def _init_widgets(self):
        """
        Creates child widgets by calling factory methods from `scrilla.gui.widgets.factories`. This method will iterate over `self.controls` and initialize the optional input widget accordingly. `self.optional_pane` and `self.required_pane`, the container widgets for the input elements, are initialized with a style tag on the same layer as the `scrilla.gui.widgets.components.ArgumentWidget`.
        """
        self.title = factories.atomic_widget_factory(format='subtitle', title='Function Input')
        self.required_title = factories.atomic_widget_factory(format='label', title='Required Arguments')
        self.optional_title = factories.atomic_widget_factory(format='label', title='Optional Arguments')
        self.error_message = factories.atomic_widget_factory(format='error', title="Error Message Goes Here")
        self.calculate_button = factories.atomic_widget_factory(format='button', title='Calculate')
        self.clear_button = factories.atomic_widget_factory(format='button', title='Clear')
        self.symbol_hint = factories.atomic_widget_factory(format='text', title="Separate Symbols With Commas")

        self.symbol_widget = factories.composite_widget_factory(format='symbols', title="Symbols :", optional=False)

        for control in self.controls:
            if self.controls[control]:
                self.control_widgets[control] = factories.composite_widget_factory(definitions.ARG_DICT[control]['widget_type'], 
                                                                            f'{definitions.ARG_DICT[control]["name"]} :',
                                                                            optional = True)
            else:
                self.control_widgets[control] = None
        # TODO: save group controls in dictionary and initialize in separate loop so all elements in group can be inputted.

        self.required_pane = factories.layout_factory(format='vertical-box')
        self.required_pane.setObjectName(self.layer)
        self.optional_pane = factories.layout_factory(format='vertical-box')
        self.optional_pane.setObjectName(self.layer)
        self.setLayout(QtWidgets.QVBoxLayout())
    
    def _arrange_widgets(self):
        """
        Arrange child widgets in their layouts and provides rendering hints. The `self.symbol_widget` is set into a ``PySide6.QtWidgets.QVBoxLayout`` named `self.required_pane`. The optional input widgets are set into a separate ``PySide6.QtWidgets.QVBoxLayout`` named `self.optional_pane`. `self.required_pane` and `self.optional_pane` are in turn set into a parent `PySide6.QtWidgets.QVBoxLayout``, along with `self.calculate_button` and `self.clear_button`. A strecth widget is inserted between the input widgets and the button widgets. 
        
        """
        factories.set_policy_on_widget_list([self.title, self.required_title, self.optional_title, self.symbol_hint, 
                                            self.required_pane, self.optional_pane], 
                                            QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Maximum))
        self.setSizePolicy(QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding))

        self.required_pane.layout().addWidget(self.required_title)
        self.required_pane.layout().addWidget(self.symbol_hint)
        self.required_pane.layout().addWidget(self.symbol_widget)

        self.optional_pane.layout().addWidget(self.optional_title)
        for control_widget in self.control_widgets.values():
            if control_widget is not None:
                self.optional_pane.layout().addWidget(control_widget)

        self.layout().addWidget(self.title)
        self.layout().addWidget(self.error_message)
        self.layout().addWidget(self.required_pane)
        self.layout().addWidget(self.optional_pane)
        self.layout().addStretch()
        self.layout().addWidget(self.calculate_button)
        self.layout().addWidget(self.clear_button)

    def _stage_widgets(self):
        """
        Prepares child widgets for display. `self.clear_function` and `self.calculate` function are hooked into the `clicked` signal emitted from `self.clear_button` and `self.calculate_button`, respectively.
        """
        self.error_message.hide()
        self.clear_button.clicked.connect(self.clear_function)
        self.calculate_button.clicked.connect(self.calculate_function)
            # NOTE: symbol widget is technically a layout in which the lineedit is abutted by a label, so need
            # to pull the actual input element from the layout
        self.symbol_widget.layout().itemAt(1).widget().returnPressed.connect(self.calculate_function)

    def get_symbol_input(self) -> str:
        """
        Returns the list of symbols inputted into the `PySide6.QtWidgets.QLineEdit` child of `symbol_widget`. The strings in the returned list have been split on a comma delimiter and had whitespace trimmed. 
        """
        return helper.split_and_strip(self.symbol_widget.layout().itemAt(1).widget().text())

    def get_control_input(self, control_widget_key: str) -> Union[datetime.date, str, bool, None]:
        """
        Get the value on the specified optional input widget. Optional keys are accessed through the keys of the  `scrilla.static.definitions.ARG_DICT` dictionary.

        If the widget is disabled or has been excluded altogether from the parent widget, i.e. a value of `False` was passed in through the constructor's `controls` arguments for that optional input widget, this method will return `None`.
        """
        if self.control_widgets[control_widget_key] is None:
            return None

        widget = self.control_widgets[control_widget_key].layout().itemAt(1).widget()

        if not widget.isEnabled():
            return None

        if type(widget) == QtWidgets.QDateEdit: 
            return widget.date().toPython()
        if type(widget) == QtWidgets.QLineEdit:
            if type(widget.validator()) ==  QtGui.QIntValidator:
                return int(widget.text())
            if type(widget.validator()) in [QtGui.QDoubleValidator, QtGui.QRegularExpressionValidator]:
                return float(widget.text())
            return widget.text()
        if type(widget) == QtWidgets.QRadioButton:
            return widget.isChecked()
    
    def prime(self) -> None:
        """
        Enables user input on child widgets, except `clear_button` which is disabled.
        """
        self.clear_button.hide()
        self.calculate_button.show()
        self.symbol_widget.layout().itemAt(1).widget().setEnabled(True)
        self.symbol_widget.layout().itemAt(1).widget().clear()
        for control in self.control_widgets:
            if self.control_widgets[control] is not None:
                if type(self.control_widgets[control].layout().itemAt(1).widget()) != QtWidgets.QRadioButton:
                    self.control_widgets[control].layout().itemAt(1).widget().clear()
                self.control_widgets[control].layout().itemAt(2).widget().setEnabled(True)
                self.control_widgets[control].layout().itemAt(2).widget().setCheckState(QtCore.Qt.Unchecked)
                self.control_widgets[control].layout().itemAt(1).widget().setEnabled(False)
                # NOTE: have to set Widget1 to disabled last since the signal on the Widget2 is connected
                # through CheckState to the enabled stated of Widget1, i.e. flipping the CheckState on 
                # Widget2 switches the enabled state of Widget1.
    
    def fire(self) -> None:
        """
        Disables user input on child widgets, except `clear_button` which is enabled.
        """
        self.clear_button.show()
        self.calculate_button.hide()
        self.symbol_widget.layout().itemAt(1).widget().setEnabled(False)
        for control in self.control_widgets:
            if self.control_widgets[control] is not None:
                self.control_widgets[control].layout().itemAt(1).widget().setEnabled(False)
                self.control_widgets[control].layout().itemAt(2).widget().setEnabled(False)

class TableWidget(QtWidgets.QWidget):
    """
    Base class for other more complex widgets to inherit. An instance of `scrilla.gui.widgets.TableWidget` embeds its child widgets in its own layout, which is an instance of``PySide6.QtWidgetQVBoxLayout``. This class provides access to the following widgets: a ``PySide6.QtWidgets.QLabel`` for the title widget, an error message widget and a ``PySide6.QtWidgets.QTableWidget`` for results display. 

    Parameters
    ----------
    1. **layer**: ``str``
        Stylesheet property attached to widget.
    2. **widget_title**: ``str``
        *Optional*. Defaults to "Table Result". Title of the widget.

    Attributes
    ----------
    1. **title**: ``PySide6.QtWidget.QLabel``
    2.. **table**: ``PySide6.QtWidget.QTableWidget``

    """
    def __init__(self, layer, widget_title: str ="Table Result"):
        super().__init__()
        self.layer = layer
        self._init_widgets(widget_title)
        self._arrange_widgets()
        self._stage_widgets()

    def _init_widgets(self, widget_title: str) -> None:
        """Creates child widgets and their layouts"""
        self.title = factories.atomic_widget_factory(format='heading', title=widget_title)
        self.table = factories.atomic_widget_factory(format='table', title=None)
        self.setLayout(QtWidgets.QVBoxLayout())
    
    def _arrange_widgets(self) -> None:
        self.title.setSizePolicy(QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding,
                                                            QtWidgets.QSizePolicy.Minimum))
        self.setSizePolicy(QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding,
                                                            QtWidgets.QSizePolicy.Minimum))
        self.layout().addWidget(self.title)
        self.layout().addWidget(self.table, 1)

    def _stage_widgets(self) -> None:
        self.table.hide()
    
    def init_table(self, rows: List[str], columns: List[str]) -> None:
        """
        Initializes `table` for display. Number of rows and columns is determined by the length of the passed in lists.

        Parameters
        ----------
        1. **rows**: ``List[str]``
            List containing the row headers.
        2. **columns**: ``List[str]``
            List containing the column headers.
        """
        self.table.setRowCount(len(rows))
        self.table.setColumnCount(len(columns))
        self.table.setHorizontalHeaderLabels(columns)
        self.table.setVerticalHeaderLabels(rows)

    def show_table(self):
        self.table.resizeColumnsToContents()
        self.table.show()

class GraphWidget(QtWidgets.QWidget):
    """
    Base class for other more complex widgets to inherit. An instance of `scrilla.gui.widgets.GraphWidget` embeds its child widgets in its own layout, which is an instance of``PySide6.QtWidgetQVBoxLayout``. This class provides access to the following widgets: a ``PySide6.QtWidgets.QLabel`` for the title widget, an error message widget and a ``PySide6.QtWidgets.QTableWidget`` for results display. 

    The graph to be displayed should be stored in the `scrilla.settings.TEMP_DIR` directory before calling the `show_pixmap` method on this class. It will load the graph from file and convert it into a ``PySide6.QtGui.QPixMap``.

    Parameters
    ----------
    1. **tmp_graph_key**: ``str``
        The key of the file in the `scrilla.settings.TEMP_DIR` used to store the image of the graph.
    2. **widget_title**: ``str``
        *Optional*. Defaults to "Graph Results". Title of the widget.

    Attributes
    ----------
    1. **tmp_graph_key**: ``str``
    2. **title**: ``PySide6.QtWidget.QLabel``
    3. **figure**: ``PySide6.QtWidget.QLabel``
    """
    def __init__(self, tmp_graph_key: str, layer: str, widget_title: str ="Graph Results"):
        super().__init__()    
        self.layer = layer
        self.tmp_graph_key = tmp_graph_key
        self._init_widgets(widget_title)
        self._arrange_widgets()
        self._stage_widgets() 
    
    def _init_widgets(self, widget_title: str) -> None:
        self.title = factories.atomic_widget_factory(format='heading', title=widget_title)
        self.figure = factories.atomic_widget_factory(format='figure', title=None)
        self.setLayout(QtWidgets.QVBoxLayout())

    def _arrange_widgets(self) -> None:
        self.title.setSizePolicy(QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding,
                                                            QtWidgets.QSizePolicy.Minimum))
        self.setSizePolicy(QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding,
                                                            QtWidgets.QSizePolicy.Minimum))
        self.layout().addWidget(self.title)
        self.layout().addWidget(self.figure)
    
    def _stage_widgets(self) -> None:
        self.figure.hide()

    def set_pixmap(self) -> None:
        self.figure.setPixmap(utilities.generate_pixmap_from_temp(self.width(), self.height(), self.tmp_graph_key))
        self.figure.show()

class CompositeWidget(QtWidgets.QWidget):
    """
    Constructor
    -----------
    1. **tmp_graph_key**: ``str``
    2. **widget_title**: ``str``
        *Optional*. Defaults to "Results". Title of the widget.
    3. **table_title**: ``Union[str,None]``
    4. **graph_title**: ``Union[str,None]``

    Attributes
    ----------
    1. **title**: ``PySide6.QtWidgets.QLabel``
    2. **table_widget**: ``scrilla.gui.widgets.TableWidget``
    3. **graph_widget**: ``scrilla.gui.widgets.GraphWidget``
    4. **tab_widget**: ``PySide6.QtWidget.QTabWidget``

    """
    def __init__(self, tmp_graph_key: str, layer: str, widget_title: str="Results", 
                    table_title: Union[str, None]=None, 
                    graph_title: Union[str,None]=None):
        super().__init__()
        self.setObjectName(layer)
        self._init_widgets(widget_title=widget_title,
                                        tmp_graph_key=tmp_graph_key)
        self._arrange_widgets(graph_title=graph_title, 
                                        table_title=table_title)

    def _init_widgets(self, widget_title: str, tmp_graph_key: str) -> None:
        """Creates child widgets and their layouts"""
        self.title = factories.atomic_widget_factory(format='subtitle', title=widget_title)

        self.table_widget = TableWidget(layer=self.objectName())
        self.graph_widget = GraphWidget(tmp_graph_key=tmp_graph_key, layer=self.objectName())

        self.tab_widget = QtWidgets.QTabWidget()

        self.setLayout(QtWidgets.QVBoxLayout())
        
    def _arrange_widgets(self, graph_title: str, table_title: str) -> None:
        self.title.setSizePolicy(QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding,
                                                            QtWidgets.QSizePolicy.Minimum))
        self.tab_widget.setSizePolicy(QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding,
                                                            QtWidgets.QSizePolicy.Expanding))
        self.title.setAlignment(QtCore.Qt.AlignLeft)

        self.tab_widget.addTab(self.table_widget, table_title)
        self.tab_widget.addTab(self.graph_widget, graph_title)
        
        self.layout().addWidget(self.title)
        self.layout().addWidget(self.tab_widget)
