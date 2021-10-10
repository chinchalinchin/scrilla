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

from typing import Callable
from PySide6 import QtGui, QtCore, QtWidgets

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
    2. **_style**
        Child widgets are styled. Fonts and cues are applied.
    3. **_arrange**
        Child widgets are arranged. Layouts are applied.
    4. **_stage**
        Child widgets are prepped for display.
"""

class SymbolWidget(QtWidgets.QWidget):
    """
    Base class for other more complex widgets to inherit. `scrilla.gui.widgets.SymbolWidget` only initializes its child widgets and applies no layouts. An instance of `scrilla.gui.widgets.SymbolWidget` provides essential widgets, such as ``PySide6.QtWidgets.QLabel``'s for the title widget and error message widget, a ``PySide6.QtWidgets.QPushButton`` for the calculate button widget, a ``PySide6.QtWidget.QLineEdit`` for ticker symbol input, etc. 
    
    Constructor
    -----------
    1. **widget_title**: ``str``
        Title affixed to the top of the widget.
    2. **button_msg**: ``str``
        Message written on `self.calculate_button`

    Attributes
    ----------
    1. **message**: ``PySide6.QtWidgets.QLabel``
        Label attached to `self.symbol_input`.
    2. **error_message**: ``PySide6.QtWidget.QLabel``
        Message displayed if there is an error thrown during calculation.
    3. **calculate_button**: ``PySide6.QtWidget.QPushButton``
        Empty button for super classes to inherit, primed to fire events on return presses
    4. **clear_button**: ``PySide6.QtWidget.QPushButton``
        Empty button for super classes to inherit, primed to fire events on return presses.
    5. **symbol_input**: ``PySide6.QtWidget.QLineEdit``
        Empty text area for super classes to inherit
    """
    # TODO: calculate and clear should be part of THIS constructor, doesn't make sense to have other widgets hook them up.
    def __init__(self, widget_title: str, button_msg: str):
        super().__init__()
        self.widget_title = widget_title
        self.button_msg = button_msg

        self._init_symbol_widgets()
        self._arrange_symbol_widgets()
        self._stage_symbol_widgets()
    
    def _init_symbol_widgets(self):
        """Creates child widgets"""
        self.title = QtWidgets.QLabel(self.widget_title)
        self.title.setObjectName('subtitle')

        self.message = QtWidgets.QLabel("Please separate symbols with a comma")
        self.message.setObjectName('text')

        self.error_message = QtWidgets.QLabel("Error message goes here")
        self.error_message.setObjectName('error')

        self.calculate_button = QtWidgets.QPushButton(self.button_msg)
        self.calculate_button.setObjectName('button')
        
        self.clear_button = QtWidgets.QPushButton("Clear")
        self.clear_button.setObjectName('button')

        self.symbol_input = QtWidgets.QLineEdit()
        self.symbol_input.setObjectName('line-edit')
    
    def _arrange_symbol_widgets(self):
        """Provides rendering hints to child widgets"""
        self.title.setAlignment(QtCore.Qt.AlignTop)
        self.message.setAlignment(QtCore.Qt.AlignBottom)
        self.error_message.setAlignment(QtCore.Qt.AlignHCenter)

    def _stage_symbol_widgets(self):
        """Prepares child widgets for display"""
        self.symbol_input.setMaxLength(100)
        self.error_message.hide()
        self.calculate_button.setAutoDefault(True) # emits 'clicked' when return is pressed
        self.clear_button.setAutoDefault(True)
        # self.clear_button.clicked.connect(self.clear_function)
        # self.calculate_button.clicked.connect(self.table_function)
        # self.symbol_input.returnPressed.connect(self.table_function)

class TableWidget(SymbolWidget):
    """
    Parameters
    ----------
    1. **widget_title**: ``str``
        Title of the widget. Passed to the super class `scrilla.gui.widgets.SymbolWidget`.
    2. **button_msg**: ``str``
        Message written on the `self.calculate_button`. Passed to the super class `scrilla.gui.widgets.SymbolWidget`.
    3. **table_function**: ``Callable``
        Function triggered by clicking on`self.calculate_button` or pressing return while focused on `self.symbol_input`.

    Attributes
    ----------
    1. **table_function**: ``Callable``
        Function triggered by clicking on`self.calculate_button` or pressing return while focused on `self.symbol_input`.
    2. **table**: ``PySide6.QtWidget.QTableWidget``
    3. **layout**: ``PySide6.QtWidget.QVBoxLayout`` 
    4. **displayed**: ``bool``
    5. **figure**: ``Union[None, QtWidgets.QLabel]``

    Methods
    -------
    1. _init_widgets()
        Creates the children widgets and layouts
    2. _arrange_widgets()
        Arrange the children widget within the layouts
    3. _stage_widgets()
        Prepares the children widget for display
    """
    def __init__(self, widget_title: str, button_msg: str, table_function: Callable, clear_function: Callable):
        super().__init__(widget_title=widget_title, button_msg=button_msg)
        self.table_function = table_function
        self.clear_function = clear_function

        self._init_table_widgets()
        self._arrange_table_widgets()
        self._stage_table_widgets()

    def _init_table_widgets(self):
        """Creates child widgets and their layouts"""
        self.table = QtWidgets.QTableWidget()
        self.table.setObjectName('table')

        self.setLayout(QtWidgets.QVBoxLayout())
    
    def _arrange_table_widgets(self):
        self.table.setHorizontalHeader(QtWidgets.QHeaderView(QtCore.Qt.Horizontal))
        self.table.setVerticalHeader(QtWidgets.QHeaderView(QtCore.Qt.Vertical))

        self.layout().addWidget(self.title)
        self.layout().addStretch()
        self.layout().addWidget(self.table, 1)
        self.layout().addWidget(self.error_message)
        self.layout().addWidget(self.message)
        self.layout().addWidget(self.symbol_input)
        self.layout().addWidget(self.calculate_button)
        self.layout().addWidget(self.clear_button)

    def _stage_table_widgets(self):
        # TODO: remove button function hook
        self.clear_button.clicked.connect(self.clear_function)
        self.calculate_button.clicked.connect(self.table_function)
        self.symbol_input.returnPressed.connect(self.table_function)
        self.table.setSizeAdjustPolicy(QtWidgets.QAbstractScrollArea.AdjustToContents)
        self.table.hide()

# NOTE: display_function MUST set displayed = True and set
#       figure to FigureCanvasAgg object
class GraphWidget(SymbolWidget):
    """
    Parameters
    ----------
    1. **widget_title**: ``str``
        Title of the widget. Passed to the super class `scrilla.gui.widgets.SymbolWidget`.
    2. **button_msg**: ``str``
        Message written on the `self.calculate_button`. Passed to the super class `scrilla.gui.widgets.SymbolWidget`.
    3. **display_function**: ``Callable``
        Function triggered by clicking on`self.calculate_button` or pressing return while focused on `self.symbol_input`.
    4. **clear_function**: ``Callable``
        Function trigged by clicking on `self.clear_button`.

    Attributes
    ----------
    1. **layout**: ``PySide6.QtWidget.QVBoxLayout``
    """
    def __init__(self, widget_title: str, button_msg: str, display_function: Callable, clear_function: Callable):
        super().__init__(widget_title=widget_title, button_msg=button_msg)    
        self.display_function = display_function
        self.clear_function = clear_function
        self._init_graph_widgets()
        self._arrange_graph_widgets()
        self._stage_graph_widgets() 
    
    def _init_graph_widgets(self):
        self.setLayout(QtWidgets.QVBoxLayout())

    def _arrange_graph_widgets(self):
        self.layout().addWidget(self.title)
        self.layout().addStretch()
        self.layout().addWidget(self.message)
        self.layout().addWidget(self.symbol_input)
        self.layout().addWidget(self.calculate_button)
        self.layout().addWidget(self.clear_button)
    
    def _stage_graph_widgets(self):
        # TODO: remove button function hook
        self.clear_button.clicked.connect(self.clear_function)
        self.calculate_button.clicked.connect(self.display_function)
        self.symbol_input.returnPressed.connect(self.display_function)

class CompositeWidget(SymbolWidget):
    """
    Constructor
    -----------
    1. **widget_title**: ``str``
        Title of the widget. Passed to the super class `scrilla.gui.widgets.SymbolWidget`.
    2. **button_msg**: ``str``
        Message written on the `self.calculate_button`. Passed to the super class `scrilla.gui.widgets.SymbolWidget`.
    3. **display_function**: ``Callable``
        Function triggered by clicking on`self.calculate_button` or pressing return while focused on `self.symbol_input`.
    4. **calculate_function**: ``Callable``
        Function triggered by clicking on `self.calculate_button` or pressing return while focused on `self.symbol_input`.

    Attributes
    ----------
    1. **displayed**: ``bool``
    2. **figure**: ``Union[None, QtWidgets.QLabel]``
    3. **table**
    4. **first_layer**
    5. **left_layer**
    6. **right_layer**


    """
    def __init__(self, widget_title, button_msg, calculate_function, clear_function):
        super().__init__(widget_title=widget_title, button_msg=button_msg)
        self.calculate_function = calculate_function
        self.clear_function = clear_function
        self._init_composite_widgets()
        self._arrange_composite_widgets()
        self._stage_composite_widgets()

    def _init_composite_widgets(self):
        """Creates child widgets and their layouts"""        
        self.table = QtWidgets.QTableWidget()

        self.setLayout(QtWidgets.QVBoxLayout())

        self.first_layer = QtWidgets.QWidget()
        self.first_layer.setLayout(QtWidgets.QHBoxLayout())

        self.left_layer = QtWidgets.QWidget()
        self.left_layer.setLayout(QtWidgets.QVBoxLayout())

        self.right_layer = QtWidgets.QWidget()
        self.right_layer.setLayout(QtWidgets.QVBoxLayout())
        
    def _arrange_composite_widgets(self):
        self.table.setSizeAdjustPolicy(QtWidgets.QAbstractScrollArea.AdjustToContents)
        self.first_layer.layout().addWidget(self.left_layer)
        self.first_layer.layout().addWidget(self.right_layer)

        self.left_layer.layout().addWidget(self.table, 1)
        
        self.layout().addWidget(self.title)
        self.layout().addWidget(self.first_layer)
        self.layout().addStretch()
        self.layout().addWidget(self.error_message)
        self.layout().addWidget(self.message)
        self.layout().addWidget(self.symbol_input)
        self.layout().addWidget(self.calculate_button)
        self.layout().addWidget(self.clear_button)

    def _stage_composite_widgets(self):
        self.table.hide()
        # TODO: remove button function hook
        self.clear_button.clicked.connect(self.clear_function)
        self.calculate_button.clicked.connect(self.calculate_function)
        self.symbol_input.returnPressed.connect(self.calculate_function)

class PortfolioWidget(SymbolWidget):
    """
    Attributes
    ----------
    1. **widget_title**
    2. **optimize_function**
    3. **left_title**
    4. **right_title**
    5. **target_label**
    6. **portfolio_label**
    7. **result**
    8. **result_table**
    9. **target_return**
    10. **portfolio_value**
    11. **first_layer**
    12. **left_layer**
    13. **right_layer**

    .. notes::
        * Widget Hierarchy
            1. root_layout -> Vertically aligned
                a. first_layout -> Horizonitally aligned
                    i. left_layout -> Vertically aligned
                    ii. right_layout -> Vertically aligned
    """
    def __init__(self, widget_title, optimize_function, clear_function):
        super().__init__(widget_title=widget_title, button_msg="Optimize Portfolio")
        self.widget_title = widget_title
        self.optimize_function = optimize_function
        self.clear_function = clear_function

        self._init_portfolio_widgets()
        self._arrange_portfolio_widgets()
        self._stage_portfolio_widgets()
        
    def _init_portfolio_widgets(self):
        """Creates child widgets and the hierarchy of layouts"""
        self.left_title = QtWidgets.QLabel("Portfolio")
        self.right_title = QtWidgets.QLabel("Constraints")
        self.target_label = QtWidgets.QLabel("Target Return")
        self.portfolio_label = QtWidgets.QLabel("Investment")
        self.result = QtWidgets.QLabel("Result")

        self.result_table = QtWidgets.QTableWidget()

        self.target_return = QtWidgets.QLineEdit()
        self.target_return.setObjectName('line-edit')

        self.portfolio_value = QtWidgets.QLineEdit()
        self.portfolio_value.setObjectName('line-edit')

        self.first_layer = QtWidgets.QWidget()
        self.left_layer = QtWidgets.QWidget()
        self.right_layer = QtWidgets.QWidget()

        self.first_layer.setLayout(QtWidgets.QHBoxLayout())
        self.left_layer.setLayout(QtWidgets.QVBoxLayout())
        self.right_layer.setLayout(QtWidgets.QVBoxLayout())
        self.setLayout(QtWidgets.QVBoxLayout())

    def _arrange_portfolio_widgets(self):
        """Arranges child widgets and provides rendering hints"""
        self.result.setAlignment(QtCore.Qt.AlignRight)
        self.result_table.setSizeAdjustPolicy(QtWidgets.QAbstractScrollArea.AdjustToContents)

        self.layout().addWidget(self.title)
        self.layout().addWidget(self.result)
        self.layout().addWidget(self.error_message)
        self.layout().addWidget(self.result_table, 1)
        self.layout().addStretch()
        self.layout().addWidget(self.first_layer)
        self.layout().addWidget(self.clear_button)
        self.layout().addStretch()

        self.first_layer.layout().addWidget(self.left_layer)
        self.first_layer.layout().addWidget(self.right_layer)

        self.left_layer.layout().addWidget(self.left_title)
        self.left_layer.layout().addWidget(self.portfolio_label)
        self.left_layer.layout().addWidget(self.portfolio_value)
        self.left_layer.layout().addWidget(self.message)
        self.left_layer.layout().addWidget(self.symbol_input)

        self.right_layer.layout().addWidget(self.right_title)
        self.right_layer.layout().addWidget(self.target_label)
        self.right_layer.layout().addWidget(self.target_return)
        self.right_layer.layout().addWidget(self.calculate_button)

    def _stage_portfolio_widgets(self):
        """Prepares child widgets for display and hooks widget functions into user input widgets"""
        self.result.hide()
        self.result_table.hide()

        # TODO: remove button function hook...target return is specific to this widget though...
        #       will need to think. 
        self.calculate_button.clicked.connect(self.optimize_function)
        self.clear_button.clicked.connect(self.clear_function)
        self.symbol_input.returnPressed.connect(self.optimize_function)
        self.target_return.returnPressed.connect(self.optimize_function)

        self.target_return.setValidator(QtGui.QDoubleValidator(-10.0000, 10.0000, 4))
        self.portfolio_value.setValidator(QtGui.QDoubleValidator(0, 1000000, 2))

