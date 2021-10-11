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

from typing import Callable, Dict, List, Union
from PySide6 import QtGui, QtCore, QtWidgets

from scrilla.gui import utilities, formats
from scrilla.static import definitions, constants

# TODO: have widgets create their own layouts and arrange their hcild widgets in them, i.e. not in their root layout.
#       then compose the layouts in the functions module.

# in fact, if you think about it, none of these widgets need to inherit QWidget. they could implement Layouts and add their
# child widgets directly to their layouts. then in the functions module, the layouts could be composed...

# that's probably the way to do this...

# this is definitely not a clean way of doing. all the classes are mixed together. need to enforce separation or streamline
# the inheritance.

# question: where should the calculate buttons come from?
# question: what widgets are absolutely necessary for each widget in here?
# isolate by functionality. no widget dependency.

# REFACTOR.

# I think the calculate button and clear button coming from the symbolwidget is fine, but table/composite/graph/portfolio 
# should not hook up the functions to these buttons.

# no inheritance between widgets. 

"""
A series of classes that all inherit from ``PySide6.QtWidgets.QWidget` and build up in sequence the necessary functionality to grab and validate user input, calculate and display results, etc. These widgets are not directly displayed on the GUI; rather, they are used as building blocks by the `scrilla.gui.functions` module, to create widgets specifically for application functions.

All widgets have a similar structure in that they call a series of methods tailored to their specific class: 
    1. **_init**
        Child widgets are constructed. Layouts are created.
    2. **_arrange**
        Child widgets are arranged. Layouts are applied.
    3. **_stage**
        Child widgets are prepped for display.
"""


def generate_control_skeleton():
    return { arg: False for arg in definitions.ARG_DICT }

def _layout_factory(format: str):
    widget = QtWidgets.QWidget()

    if format == 'vertical-box':
        widget.setLayout(QtWidgets.QVBoxLayout())
    
    elif format == 'horizontal-box':
        widget.setLayout(QtWidgets.QHBoxLayout())
    
    else:
        widget.setLayout(QtWidgets.QBoxLayout())

    return widget

def _atomic_widget_factory(format: str, title: str):
    if format in ['title', 'subtitle', 'heading', 'label', 'error', 'text'] :
        widget = QtWidgets.QLabel(title)
        widget.setObjectName(format)
        if format in ['title', 'subtitle', 'label', 'heading']:
            widget.setAlignment(QtCore.Qt.AlignTop)
    
    elif format == 'button':
        widget = QtWidgets.QPushButton(title)
        widget.setObjectName(format)

    else: 
        widget = QtWidgets.QWidget()
    
    return widget
# this methdo was separated into input and passive factory methods. combined them because i thought it made sense,
# however, this method is now getting a little complex. it might not hurt to simplify and refactor a bit.
def _composite_widget_factory(format: str, title: str = None) -> QtWidgets.QWidget:
    # input widget

    if format == 'date':
        widget = QtWidgets.QWidget()
        widget.setLayout(QtWidgets.QHBoxLayout())
        widget.setObjectName('input-container')

        label_widget = QtWidgets.QLabel(title)
        label_widget.setAlignment(QtCore.Qt.AlignBottom)
        label_widget.setObjectName('input-label')

        main_widget = QtWidgets.QDateEdit()
        main_widget.setDate(QtCore.QDate.currentDate())
        main_widget.setMaximumDate(QtCore.QDate.currentDate())
        main_widget.setMinimumDate(QtCore.QDate(constants.constants['PRICE_YEAR_CUTOFF'], 1,1))
        main_widget.setObjectName(format)

        widget.layout().addWidget(label_widget)
        widget.layout().addWidget(main_widget)

    elif format == 'decimal':
        pass

    elif format == 'currency':
        pass
    
    elif format == 'years':
        pass
    
    elif format == 'integer':
        pass
    
    elif format == 'model':
        pass
    
    elif format == 'select':
        pass
    
    elif format == 'file':
        pass
    
    elif format == 'key':
        pass
    
    elif format == 'password':
        pass
    
    elif format == 'flag':
        pass
    
    elif format == 'line-edit':
        widget = QtWidgets.QWidget()
        widget.setLayout(QtWidgets.QHBoxLayout())
        widget.setObjectName('input-container')

        label_widget = QtWidgets.QLabel(title)
        label_widget.setAlignment(QtCore.Qt.AlignBottom)
        label_widget.setObjectName('input-label')

        main_widget = QtWidgets.QLineEdit()
        main_widget.setAlignment(QtCore.Qt.AlignTop)
        main_widget.setObjectName(format)

        widget.layout().addWidget(label_widget)
        widget.layout().addWidget(main_widget)

    else:
        widget = QtWidgets.QWidget()
    
    return widget

def _set_policy_on_widget_list(widget_list: List[QtWidgets.QWidget], policy: QtWidgets.QSizePolicy):
    for widget in widget_list:
        widget.setSizePolicy(policy)

class ArgumentWidget(QtWidgets.QWidget):
    """
    Base class for other more complex widgets to inherit. An instance of `scrilla.gui.widgets.ArgumentWidget` embeds its child widgets in its own layout,  which is an instance of``PySide6.QtWidgetQVBoxLayout``. This class provides access to the following widgets:a ``PySide6.QtWidgets.QLabel`` for the title widget, an error message widget, a ``PySide6.QtWidgets.QPushButton`` for the calculate button widget, a ``PySide6.QtWidget.QLineEdit`` for ticker symbol input, and a variety of optional input widgets enabled by boolean flags in the `controls` constructor argument. 
    
    Constructor
    -----------
    1. **calculate_function**: ``str``
    2. **clear_function**: ``str``
    3. **controls:**: ``Dict[bool]``
    4. **widget_title**: ``str``
        *Optional*. Defaults to `Function Input`. Title affixed to the top of the widget.
    5. **button_msg**: ``str``
        *Optional*. Defaults to `Calculate`. Message written on `self.calculate_button`

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
    """
    # TODO: calculate and clear should be part of THIS constructor, doesn't make sense to have other widgets hook them up.
    def __init__(self, calculate_function: Callable, clear_function: Callable, controls: Dict[str, bool], layer):
        super().__init__()
        self.layer = layer
        self.controls = controls
        self.control_widgets = {}
        self.calculate_function = calculate_function
        self.clear_function = clear_function

        self._init_arg_widgets()
        self._arrange_arg_widgets()
        self._stage_arg_widgets()
    
    def _init_arg_widgets(self):
        """Creates child widgets"""
        self.title = _atomic_widget_factory(format='subtitle', title='Function Input')
        self.required_title = _atomic_widget_factory(format='label', title='Required Arguments')
        self.optional_title = _atomic_widget_factory(format='label', title='Optional Arguments')
        self.error_message = _atomic_widget_factory(format='error', title="Error Message Goes Here")
        self.calculate_button = _atomic_widget_factory(format='button', title='Calculate')
        self.clear_button = _atomic_widget_factory(format='button', title='Clear')
        self.symbol_hint = _atomic_widget_factory(format='text', title="Separate symbols with comma")

        self.symbol_widget = _composite_widget_factory(format='line-edit', title="Symbols :")
        for control in self.controls:
            if self.controls[control]:
                self.control_widgets[control] = _composite_widget_factory(definitions.ARG_DICT[control]['widget_type'], 
                                                                            f'{definitions.ARG_DICT[control]["name"]} :')
            else:
                self.control_widgets[control] = None

        self.required_pane = _layout_factory(format='vertical-box')
        self.required_pane.setObjectName(self.layer)
        self.optional_pane =_layout_factory(format='vertical-box')
        self.optional_pane.setObjectName(self.layer)
        self.setLayout(QtWidgets.QVBoxLayout())
    
    def _arrange_arg_widgets(self):
        """Arrange child widgets in their layouts and provides rendering hints"""
        self.symbol_hint.setAlignment(QtCore.Qt.AlignBottom)
        self.error_message.setAlignment(QtCore.Qt.AlignHCenter)
        
        _set_policy_on_widget_list([self.title, self.required_title, self.optional_title, self.calculate_button, 
                                    self.clear_button, self.symbol_hint, self.symbol_widget, self.required_pane, 
                                    self.optional_pane], 
                                    QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Maximum))
        _set_policy_on_widget_list([self.symbol_widget], 
                                    QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Maximum, QtWidgets.QSizePolicy.Maximum))

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

    def _stage_arg_widgets(self):
        """Prepares child widgets for display"""
        self.error_message.hide()
        self.calculate_button.setAutoDefault(True) # emits 'clicked' when return is pressed
        self.clear_button.setAutoDefault(True)
        self.clear_button.clicked.connect(self.clear_function)
        self.calculate_button.clicked.connect(self.calculate_function)
        self.get_symbol_input().setMaxLength(100)
        self.get_symbol_input().returnPressed.connect(self.calculate_function)

    def get_symbol_input(self):
        return self.symbol_widget.layout().itemAt(1).widget()

    def get_control_input(self, control_widget_key):
        if self.control_widgets[control_widget_key] is None:
            return None
        return self.control_widgets[control_widget_key].layout().itemAt(1).widget()


class TableWidget(QtWidgets.QWidget):
    """
    Base class for other more complex widgets to inherit. An instance of `scrilla.gui.widgets.TableWidget` embeds its child widgets in its own layout, which is an instance of``PySide6.QtWidgetQVBoxLayout``. This class provides access to the following widgets: a ``PySide6.QtWidgets.QLabel`` for the title widget, an error message widget and a ``PySide6.QtWidgets.QTableWidget`` for results display. 

    Parameters
    ----------
    1. **widget_title**: ``str``
        Title of the widget. Passed to the super class `scrilla.gui.widgets.SymbolWidget`.
    2. **button_msg**: ``str``
        Message written on the `self.calculate_button`. Passed to the super class `scrilla.gui.widgets.SymbolWidget`.

    Attributes
    ----------
    1. **title**: ``PySide6.QtWidget.QLabel``
    2.. **table**: ``PySide6.QtWidget.QTableWidget``

    """
    def __init__(self, widget_title: str ="Table Result"):
        super().__init__()
        self._init_table_widgets(widget_title)
        self._arrange_table_widgets()
        self._stage_table_widgets()

    def _init_table_widgets(self, widget_title):
        """Creates child widgets and their layouts"""
        self.title = QtWidgets.QLabel(widget_title)
        self.title.setObjectName('heading')

        self.table = QtWidgets.QTableWidget()
        self.table.setObjectName('table')

        self.setLayout(QtWidgets.QVBoxLayout())
    
    def _arrange_table_widgets(self):
        self.table.setHorizontalHeader(QtWidgets.QHeaderView(QtCore.Qt.Horizontal))
        self.table.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)

        self.table.setVerticalHeader(QtWidgets.QHeaderView(QtCore.Qt.Vertical))
        # self.table.verticalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)

        self.layout().addWidget(self.title)
        self.layout().addStretch()
        self.layout().addWidget(self.table, 1)

    def _stage_table_widgets(self):
        self.table.setSizeAdjustPolicy(QtWidgets.QAbstractScrollArea.AdjustToContents)
        self.table.hide()
    
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
        Title applied to the label of the graph.

    Attributes
    ----------
    1. **tmp_graph_key**: ``str``
    2. **title**: ``PySide6.QtWidget.QLabel``
    3. **figure**: ``PySide6.QtWidget.QLabel``
    """
    def __init__(self, tmp_graph_key: str, widget_title: str ="Graph Results"):
        super().__init__()    
        self.tmp_graph_key = tmp_graph_key
        self._init_graph_widgets(widget_title)
        self._arrange_graph_widgets()
        self._stage_graph_widgets() 
    
    def _init_graph_widgets(self, widget_title):
        self.title = QtWidgets.QLabel(widget_title)
        self.title.setObjectName('heading')
        self.figure = QtWidgets.QLabel()
        self.setLayout(QtWidgets.QVBoxLayout())


    def _arrange_graph_widgets(self):
        self.title.setSizePolicy(QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding,
                                                            QtWidgets.QSizePolicy.Minimum))
        self.figure.setSizePolicy(QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding,
                                                            QtWidgets.QSizePolicy.Expanding))

        self.title.setAlignment(QtCore.Qt.AlignLeft)
        self.figure.setAlignment(QtCore.Qt.AlignCenter)

        self.layout().addWidget(self.title)
        self.layout().addWidget(self.figure)
    
    def _stage_graph_widgets(self):
        self.figure.hide()

    def set_pixmap(self):
        self.figure.setPixmap(utilities.generate_pixmap_from_temp(self.width(), self.height(), self.tmp_graph_key))
        self.figure.show()

class CompositeWidget(QtWidgets.QWidget):
    """
    Constructor
    -----------
    1. **tmp_graph_key**: ``str``
    2. **widget_title**: ``str``
        Title of the widget. Passed to the super class `scrilla.gui.widgets.SymbolWidget`.
    3. **table_title**: ``str``
    4. **graph_title**: ``str``

    Attributes
    ----------
    1. **title**: ``PySide6.QtWidgets.QLabel``
    2. **table_widget**: ``scrilla.gui.widgets.TableWidget``
    3. **graph_widget**: ``scrilla.gui.widgets.GraphWidget``
    4. **tab_widget**: ``PySide6.QtWidget.QWidget``

    """
    def __init__(self, tmp_graph_key: str, layer: str, widget_title: str="Results", 
                    table_title: Union[str, None]=None, 
                    graph_title: Union[str,None]=None):
        super().__init__()
        self.setObjectName(layer)
        self._init_composite_widgets(widget_title=widget_title,
                                        tmp_graph_key=tmp_graph_key)
        self._arrange_composite_widgets(graph_title=graph_title, 
                                        table_title=table_title)

    def _init_composite_widgets(self, widget_title, tmp_graph_key):
        """Creates child widgets and their layouts"""
        self.title = QtWidgets.QLabel(widget_title)
        self.title.setObjectName('subtitle')

        self.table_widget = TableWidget()
        self.graph_widget = GraphWidget(tmp_graph_key)

        self.tab_widget = QtWidgets.QTabWidget()

        self.setLayout(QtWidgets.QVBoxLayout())
        
    def _arrange_composite_widgets(self, graph_title, table_title):
        self.title.setSizePolicy(QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding,
                                                            QtWidgets.QSizePolicy.Minimum))
        self.title.setAlignment(QtCore.Qt.AlignLeft)

        self.tab_widget.addTab(self.table_widget, table_title)
        self.tab_widget.addTab(self.graph_widget, graph_title)
        
        self.layout().addWidget(self.title)
        self.layout().addWidget(self.tab_widget)
