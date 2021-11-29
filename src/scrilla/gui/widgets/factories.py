from typing import List

from PySide6 import QtWidgets, QtCore, QtGui
from scrilla.gui import utilities
from scrilla.static import definitions, constants


def generate_control_skeleton():
    """
    Generates a control dictionary with all argument controls initialized to `False` using the `scrilla.static.definitions.ARG_DICT`. This dictionary is used to configured the input widgets enabled on `scrilla.gui.widgets.components.ArgumentWidget`. By switching controls in this dictionary on before passing it into the constructor, the widgets for that specific input control will be displayed on `scrilla.gui.widgets.components.ArgumentWidget`.
    """
    return {arg: False for arg in definitions.ARG_DICT if not definitions.ARG_DICT[arg]['cli_only']}


def layout_factory(layout: str):
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

    else:
        widget.setLayout(QtWidgets.QBoxLayout())

    return widget


def atomic_widget_factory(component: str, title: str):
    """
    Factory function for generating various subclasses of `PySide6.QtWidgets.QWidget` pre-configured for application display.

    Parameters
    ----------
    1. **component**: ``str``
        Allowable values: `title`, `subtitle`, `heading`, `label`, `error`, `text`, `splash`, `calculate-button`, `clear-button`, `hide-button`, `download-button`, `source-button`, `package-button`, `documentation-button`, `button`, `save-dialog`, `table`, `table-item`, `figure`, `menu-bar`. If `component=None` is provided, a `PySide6.QtWidgets.QWidget` will be constructed with a `PySide6.QtWidgets.QHBoxLayout` will be returned.
    """
    if component in ['title', 'subtitle', 'heading', 'label', 'error', 'text']:
        widget = QtWidgets.QLabel(title)
        if component in ['title', 'subtitle', 'label']:
            widget.setAlignment(QtCore.Qt.AlignTop)
        elif component in ['heading']:
            widget.setAlignment(QtCore.Qt.AlignLeft)
        elif component in ['error']:
            widget.setAlignment(QtCore.Qt.AlignHCenter)
        elif component in ['text']:
            widget.setAlignment(QtCore.Qt.AlignBottom)
        widget.setObjectName(component)

    elif component in ['splash']:
        widget = QtWidgets.QLabel(utilities.load_html_template(component))
        widget.setAlignment(QtCore.Qt.AlignTop)
        widget.setSizePolicy(QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Maximum))
        widget.setWordWrap(True)
        widget.setOpenExternalLinks(True)

    elif component in ['calculate-button', 'clear-button', 'hide-button',
                       'download-button', 'source-button', 'package-button',
                       'documentation-button', 'button']:
        # buttons with text
        if format not in ['hide-button', 'download-button', 'source-button']:
            widget = QtWidgets.QPushButton(title)
            widget.setSizePolicy(QtWidgets.QSizePolicy(
                QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Maximum))

        # icon buttons
        else:
            widget = QtWidgets.QPushButton()
            widget.setSizePolicy(QtWidgets.QSizePolicy(
                QtWidgets.QSizePolicy.Maximum, QtWidgets.QSizePolicy.Maximum))
            if component == 'hide-button':
                widget.setToolTip('Hide')
            elif component == 'download-button':
                widget.setToolTip('Save As')
            elif component == 'source-button':
                widget.setToolTip('View Source')
            elif component == 'package-button':
                widget.setToolTip('View PyPi Package')
            elif component == 'documentation-button':
                widget.setToolTip('View Documentation')

        widget.setAutoDefault(True)
        widget.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        widget.setObjectName(component)

    elif component in ['save-dialog']:
        widget = QtWidgets.QFileDialog()
        widget.setFileMode(QtWidgets.QFileDialog.AnyFile)
        widget.setViewMode(QtWidgets.QFileDialog.Detail)
        widget.setNameFilter(title)
        widget.setAcceptMode(QtWidgets.QFileDialog.AcceptSave)

    elif component == 'table':
        widget = QtWidgets.QTableWidget()
        widget.setHorizontalHeader(QtWidgets.QHeaderView(QtCore.Qt.Horizontal))
        widget.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
        widget.setVerticalHeader(QtWidgets.QHeaderView(QtCore.Qt.Vertical))
        widget.setSizeAdjustPolicy(
            QtWidgets.QAbstractScrollArea.AdjustToContents)
        widget.setSizePolicy(QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum))
        # widget.verticalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
        widget.setObjectName(component)

    elif component == 'table-item':
        widget = QtWidgets.QTableWidgetItem(title)
        widget.setTextAlignment(QtCore.Qt.AlignHCenter)

    elif component == 'figure':
        widget = QtWidgets.QLabel()
        widget.setAlignment(QtCore.Qt.AlignCenter)
        widget.setSizePolicy(QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding))
        widget.setObjectName(component)

    elif component == 'menu-bar':
        widget = QtWidgets.QMenuBar(title)

    else:
        widget = QtWidgets.QWidget()
        widget.setLayout(QtWidgets.QHBoxLayout())
        widget.setSizePolicy(QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum))

    return widget


def group_widget_factory(components: List[str], title: str):
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
    widget = atomic_widget_factory(None, None)
    widget.setObjectName('input-container')

    if optional:
        toggle_widget = QtWidgets.QCheckBox()
        toggle_widget.setObjectName('input-toggle')
        toggle_widget.setSizePolicy(QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Maximum, QtWidgets.QSizePolicy.Maximum))

    label_widget = QtWidgets.QLabel(title)
    label_widget.setAlignment(QtCore.Qt.AlignBottom)
    label_widget.setObjectName('input-label')

    if component == 'date':
        main_widget = QtWidgets.QDateEdit()
        main_widget.setDate(QtCore.QDate.currentDate())
        main_widget.setMaximumDate(QtCore.QDate.currentDate())
        main_widget.setMinimumDate(QtCore.QDate(
            constants.constants['PRICE_YEAR_CUTOFF'], 1, 1))
        main_widget.setObjectName(component)
        main_widget.setEnabled(False)

    elif component == 'decimal':
        main_widget = QtWidgets.QLineEdit()
        main_widget.setObjectName(component)
        main_widget.setValidator(
            QtGui.QDoubleValidator(-100, 100, 5, main_widget))
        main_widget.setEnabled(False)
        main_widget.setSizePolicy(QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Maximum, QtWidgets.QSizePolicy.Maximum))

    elif component == 'currency':
        main_widget = QtWidgets.QLineEdit()
        main_widget.setObjectName(component)
        # https://stackoverflow.com/questions/354044/what-is-the-best-u-s-currency-regex
        main_widget.setValidator(QtGui.QRegularExpressionValidator(
            r"[+-]?[0-9]{1,3}(?:,?[0-9]{3})*(?:\.[0-9]{2})", main_widget))
        main_widget.setEnabled(False)
        main_widget.setSizePolicy(QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Maximum, QtWidgets.QSizePolicy.Maximum))

    elif component == 'integer':
        main_widget = QtWidgets.QLineEdit()
        main_widget.setObjectName(component)
        main_widget.setValidator(QtGui.QIntValidator(0, 100, main_widget))
        main_widget.setEnabled(False)
        main_widget.setSizePolicy(QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Maximum, QtWidgets.QSizePolicy.Maximum))

    elif component == 'select':
        return None

    elif component == 'flag':
        main_widget = QtWidgets.QRadioButton(title)
        main_widget.setObjectName(component)
        main_widget.setSizePolicy(QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Maximum, QtWidgets.QSizePolicy.Maximum))

    elif component == 'symbols':
        main_widget = QtWidgets.QLineEdit()
        main_widget.setObjectName(component)
        main_widget.setMaxLength(100)
        main_widget.setSizePolicy(QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Maximum))

    elif component == 'symbol':
        main_widget = QtWidgets.QLineEdit()
        main_widget.setObjectName(component)
        main_widget.setMaxLength(100)
        main_widget.setSizePolicy(QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Maximum))
        main_widget.setValidator(
            QtGui.QRegularExpressionValidator(r"[A-Za-z]+", main_widget))

    else:
        main_widget = QtWidgets.QWidget()

    widget.layout().addWidget(label_widget)
    widget.layout().addWidget(main_widget)

    if optional:
        toggle_widget.stateChanged.connect(
            lambda: main_widget.setEnabled((not main_widget.isEnabled())))
        widget.layout().addWidget(toggle_widget)

    return widget


def set_policy_on_widget_list(widget_list: List[QtWidgets.QWidget], policy: QtWidgets.QSizePolicy):
    for widget in widget_list:
        widget.setSizePolicy(policy)
