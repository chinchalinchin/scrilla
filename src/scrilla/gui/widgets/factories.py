from typing import List, Union, Dict

from PySide6 import QtWidgets, QtCore, QtGui
from scrilla.gui import utilities
from scrilla.gui import definitions as gui_definitions
from scrilla.static import definitions, constants


def generate_control_skeleton() -> Dict[str, bool]:
    """
    Generates a control dictionary with all argument controls initialized to `False` using the `scrilla.static.definitions.ARG_DICT`. This dictionary is used to configured the input widgets enabled on `scrilla.gui.widgets.components.ArgumentWidget`. By switching controls in this dictionary on before passing it into the constructor, the widgets for that specific input control will be displayed on `scrilla.gui.widgets.components.ArgumentWidget`.
    """
    return {arg: False for arg in definitions.ARG_DICT if not definitions.ARG_DICT[arg]['cli_only']}


def layout_factory(layout: str) -> QtWidgets.QWidget:
    """
    Factory function for generating instances of `PySide6.QtWidgets.QLayout`. 

    Parameters
    ----------
    1. **layout** : ``str``
        Type of layout being constructed. Allowable values: `vertical-box`, `horizontal-box`. If `layout=None`, a `PySide6.QtWidgets.QBoxLayout` will be returned.
    """
    widget = QtWidgets.QWidget()

    if layout == 'vertical-box':
        widget.setLayout(QtWidgets.QVBoxLayout())

    elif layout == 'horizontal-box':
        widget.setLayout(QtWidgets.QHBoxLayout())

    return widget


def dialog_widget_factory(component: str, options: list) -> QtWidgets.QDialog:
    dialog = QtWidgets.QDialog()
    dialog.setObjectName(component)
    dialog.setLayout(QtWidgets.QVBoxLayout())

    user_select = QtWidgets.QComboBox()
    user_select.insertItems(0, options)
    user_text = argument_widget_factory('symbols', None, False)

    input_widget = layout_factory('horizontal-box')
    input_widget.layout().addWidget(user_select)
    input_widget.layout().addWidget(user_text)

    def save():
        dialog.selection = user_select.currentText()
        dialog.value = user_text.text()
        dialog.accept()

    def cancel():
        dialog.close()

    btn = QtWidgets.QDialogButtonBox.Save | QtWidgets.QDialogButtonBox.Cancel
    box = QtWidgets.QDialogButtonBox(btn)
    box.accepted.connect(save)
    box.rejected.connect(cancel)
    dialog.layout().addWidget(input_widget)
    dialog.layout().addWidget(box)

    return dialog


def atomic_widget_factory(component: str, title: str = None) -> Union[QtWidgets.QWidget, QtWidgets.QLabel, QtWidgets.QPushButton, QtWidgets.QFileDialog, QtWidgets.QTableWidget, QtWidgets.QTableWidgetItem, QtWidgets.QMenuBar]:
    """
    Factory function for generating various subclasses of `PySide6.QtWidgets.QWidget` pre-configured for application display.

    Parameters
    ----------
    1. **component**: ``str``
        Allowable values can be assessed through the `scrilla.gui.definitions.FACTORIES['ATOMIC']` dictionary, underneath the successive `TYPES` key. If `component=None` is provided, a `PySide6.QtWidgets.QWidget` constructed with a `PySide6.QtWidgets.QHBoxLayout` will be returned.
    2. **title**: ``str``
        Name assigned to the widget.
    """
    atomic_map = gui_definitions.FACTORIES['ATOMIC']

    # Type Configuration
    if component in atomic_map['LABEL']:
        # Template Configuration
        if component in atomic_map['TEMPLATE']:
            widget = QtWidgets.QLabel(utilities.load_html_template(component))
            widget.setWordWrap(True)
            widget.setOpenExternalLinks(True)
        else:
            widget = QtWidgets.QLabel(title)
    elif component in atomic_map['BUTTON']:
        if component in atomic_map['TITLED']:
            widget = QtWidgets.QPushButton(title)
        else:
            widget = QtWidgets.QPushButton()
        widget.setAutoDefault(True)
        widget.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
    elif component in atomic_map['DIALOG']:
        widget = QtWidgets.QFileDialog()
        widget.setNameFilter(title)
        widget.setFileMode(QtWidgets.QFileDialog.AnyFile)
        widget.setViewMode(QtWidgets.QFileDialog.Detail)
        widget.setAcceptMode(QtWidgets.QFileDialog.AcceptSave)
    elif component in atomic_map['TABLE']:
        widget = QtWidgets.QTableWidget()
        widget.setHorizontalHeader(QtWidgets.QHeaderView(QtCore.Qt.Horizontal))
        widget.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
        widget.setVerticalHeader(QtWidgets.QHeaderView(QtCore.Qt.Vertical))
        widget.setSizeAdjustPolicy(
            QtWidgets.QAbstractScrollArea.AdjustToContents)
    elif component in atomic_map['ITEM']:
        widget = QtWidgets.QTableWidgetItem(title)
        widget.setTextAlignment(QtCore.Qt.AlignHCenter)
    elif component in atomic_map['MENU']:
        widget = QtWidgets.QMenuBar()

    else:
        widget = QtWidgets.QWidget()
        widget.setLayout(QtWidgets.QHBoxLayout())
        

    # Size Configuration
    if component in atomic_map['SIZING']['EXPANDEXPAND']:
        widget.setSizePolicy(QtWidgets.QSizePolicy(
                QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding))
    elif component in atomic_map['SIZING']['EXPANDMIN']:
        widget.setSizePolicy(QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum))
    elif component in atomic_map['SIZING']['MINMAX']:
        widget.setSizePolicy(QtWidgets.QSizePolicy(
                QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Maximum)) 
    elif component in atomic_map['SIZING']['MINMIN']:
        widget.setSizePolicy(QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum))
    elif component in atomic_map['SIZING']['MAXMAX']:
        widget.setSizePolicy(QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Maximum, QtWidgets.QSizePolicy.Maximum))

    # Alignment Configuration
    if component in atomic_map['ALIGN']['TOP']:
        widget.setAlignment(QtCore.Qt.AlignTop)
    elif component in atomic_map['ALIGN']['LEFT']:
        widget.setAlignment(QtCore.Qt.AlignLeft)
    elif component in atomic_map['ALIGN']['HCENTER']:
        widget.setAlignment(QtCore.Qt.AlignHCenter)
    elif component in atomic_map['ALIGN']['BOTTOM']:
        widget.setAlignment(QtCore.Qt.AlignBottom)
    elif component in atomic_map['ALIGN']['CENTER']:
        widget.setAlignment(QtCore.Qt.AlignCenter)

    # Type Specific Configuration
    # TODO: think about how to parametrize this in `scrilla.gui.definitions
    # could add a dictionary for tooltips and then use a generator-filter...`
    if component == 'hide-button':
        widget.setToolTip('Hide')
    elif component == 'clear-button':
        widget.setToolTip('Cancel')
    elif component == 'download-button':
        widget.setToolTip('Save As')
    elif component == 'source-button':
        widget.setToolTip('View Source')
    elif component == 'package-button':
        widget.setToolTip('View PyPi Package')
    elif component == 'documentation-button':
        widget.setToolTip('View Documentation')
    elif component == 'okay-button':
        widget.setToolTip('Okay')
    if component not in atomic_map['ITEM']:
        widget.setObjectName(component)
    return widget


def group_widget_factory(components: List[str], title: str) -> QtWidgets.QGroupBox:
    """
    Embeds a group of `PySide6.QtWidgets.QRadioButton` in a `PySide6.QtWidgets.GroupBox` with a vertical layout.

    Parameters
    ----------
    1. **components**: ``List[str]``
        A list of strings containing the text used for the radio button's display. Order of list corresponds to the displayed order of buttons.
    2. **title**: ``str``
        Title assigned to the container of the radio buttons, `PySide6.QtWidgets.GroupBox`.
    """
    widget_layout = QtWidgets.QVBoxLayout()

    for i, component in enumerate(components):
        radio_button = QtWidgets.QRadioButton(component)
        radio_button.setObjectName('group-toggle')
        widget_layout.addWidget(radio_button)
        if i == 0:
            radio_button.setChecked(True)

    widget = QtWidgets.QGroupBox(title)
    widget.setLayout(widget_layout)
    widget.setObjectName('group-box')

    return widget


def argument_widget_factory(component: str, title: str = None, optional: bool = True) -> QtWidgets.QWidget:
    """
    Factory function for generating various subclasses of instance `PySide6.QtWidgets.QWidgets` pre-configured for user-input. 

    Parameters
    ----------
    1. **components** : ``str``
        Allowable values: `date`, `decimal`, `currency`, `integer`, `select`, `flag`, `symbols`, `symbol`. If `components=None`, a `PySide6.QtWidgets.QWidget` will be returned.
    """
    widget = atomic_widget_factory(None, 'input-container')
    label_widget = atomic_widget_factory('footer', 'input-label')
    arg_map = gui_definitions.FACTORIES['ARGUMENTS']
    # Type Configuration
    if component in arg_map['LINE']:
        main_widget = QtWidgets.QLineEdit()
    elif component in arg_map['DATE']:
        main_widget = QtWidgets.QDateEdit()
    elif component in arg_map['RADIO']:
        main_widget = QtWidgets.QRadioButton(title)
    else:
        main_widget = QtWidgets.QWidget()

    # Sizing Configuration
    if component in arg_map['SIZING']['MAXMAX']:
        main_widget.setSizePolicy(QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Maximum, QtWidgets.QSizePolicy.Maximum))
    elif component in arg_map['SIZING']['MINMAX']:
        main_widget.setSizePolicy(QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Maximum))

    # Constraint Configuration
    if component in arg_map['CONSTRAINTS']['LENGTH']:
        main_widget.setMaxLength(100)

    # Initial Disabled Configuration
    if component in arg_map['DISABLED']:
        main_widget.setEnabled(False)

    # Type Specific Configuration
    if component == 'date':
        main_widget.setDate(QtCore.QDate.currentDate())
        main_widget.setMaximumDate(QtCore.QDate.currentDate())
        main_widget.setMinimumDate(QtCore.QDate(
            constants.constants['PRICE_YEAR_CUTOFF'], 1, 1))
    elif component == 'decimal':
        main_widget.setValidator(
            QtGui.QDoubleValidator(-100, 100, 5, main_widget))
    elif component == 'currency':
        # https://stackoverflow.com/questions/354044/what-is-the-best-u-s-currency-regex
        main_widget.setValidator(QtGui.QRegularExpressionValidator(
            r"[+-]?[0-9]{1,3}(?:,?[0-9]{3})*(?:\.[0-9]{2})", main_widget))
    elif component == 'integer':
        main_widget.setValidator(QtGui.QIntValidator(0, 100, main_widget))
    elif component == 'symbol':
        main_widget.setValidator(
            QtGui.QRegularExpressionValidator(r"[A-Za-z]+", main_widget))

    main_widget.setObjectName(component)
    widget.layout().addWidget(label_widget)
    widget.layout().addWidget(main_widget)

    if optional:
        toggle_widget = QtWidgets.QCheckBox()
        toggle_widget.setObjectName('input-toggle')
        toggle_widget.setSizePolicy(QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Maximum, QtWidgets.QSizePolicy.Maximum))
        toggle_widget.stateChanged.connect(
            lambda: main_widget.setEnabled((not main_widget.isEnabled())))
        widget.layout().addWidget(toggle_widget)

    return widget


def set_policy_on_widget_list(widget_list: List[QtWidgets.QWidget], policy: QtWidgets.QSizePolicy) -> None:
    """
    Sets the same policy on a list of widgets.

    Parameters
    """
    for widget in widget_list:
        widget.setSizePolicy(policy)
