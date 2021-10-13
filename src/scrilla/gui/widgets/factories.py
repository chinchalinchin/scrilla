from typing import List

from PySide6 import QtWidgets, QtCore, QtGui
from scrilla.static import definitions, constants

def generate_control_skeleton():
    return { arg: False for arg in definitions.ARG_DICT if not definitions.ARG_DICT[arg]['cli_only']}

def layout_factory(format: str):
    widget = QtWidgets.QWidget()

    if format == 'vertical-box':
        widget.setLayout(QtWidgets.QVBoxLayout())

    elif format == 'horizontal-box':
        widget.setLayout(QtWidgets.QHBoxLayout())
    
    else:
        widget.setLayout(QtWidgets.QBoxLayout())

    return widget

def atomic_widget_factory(format: str, title: str):
    if format in ['title', 'subtitle', 'heading', 'label', 'error', 'text'] :
        widget = QtWidgets.QLabel(title)
        if format in ['title', 'subtitle', 'label']:
            widget.setAlignment(QtCore.Qt.AlignTop)
        elif format in [ 'heading' ]:
            widget.setAlignment(QtCore.Qt.AlignLeft)
        elif format in [ 'error' ]:
            widget.setAlignment(QtCore.Qt.AlignHCenter)
        elif format in [ 'text' ]:
            widget.setAlignment(QtCore.Qt.AlignBottom)
        widget.setObjectName(format)

    elif format == 'button':
        widget = QtWidgets.QPushButton(title)
        widget.setAutoDefault(True)
        widget.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        widget.setSizePolicy(QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Maximum))
        widget.setObjectName(format)

    elif format == 'table':
        widget = QtWidgets.QTableWidget()
        widget.setHorizontalHeader(QtWidgets.QHeaderView(QtCore.Qt.Horizontal))
        widget.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
        widget.setVerticalHeader(QtWidgets.QHeaderView(QtCore.Qt.Vertical))
        widget.setSizeAdjustPolicy(QtWidgets.QAbstractScrollArea.AdjustToContents)
        widget.setSizePolicy(QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum))
        # widget.verticalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
        widget.setObjectName(format)

    elif format == 'table-item':
        widget = QtWidgets.QTableWidgetItem(title)
        widget.setTextAlignment(QtCore.Qt.AlignHCenter)

    elif format == 'figure':
        widget = QtWidgets.QLabel()
        widget.setAlignment(QtCore.Qt.AlignCenter)
        widget.setSizePolicy(QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding))
        widget.setObjectName(format)


    elif format == 'menu-bar':
        widget = QtWidgets.QMenuBar(title)

    else: 
        widget = QtWidgets.QWidget()

    return widget

def composite_widget_factory(format: str, title: str = None, optional : bool = True) -> QtWidgets.QWidget:
    widget = QtWidgets.QWidget()
    widget.setLayout(QtWidgets.QHBoxLayout())
    widget.setObjectName('input-container')
    widget.setSizePolicy(QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum))

    if optional:
        toggle_widget = QtWidgets.QCheckBox()
        toggle_widget.setObjectName('input-toggle')
        toggle_widget.setSizePolicy(QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Maximum, QtWidgets.QSizePolicy.Maximum))

    label_widget = QtWidgets.QLabel(title)
    label_widget.setAlignment(QtCore.Qt.AlignBottom)
    label_widget.setObjectName('input-label')

    if format == 'date':
        main_widget = QtWidgets.QDateEdit()
        main_widget.setDate(QtCore.QDate.currentDate())
        main_widget.setMaximumDate(QtCore.QDate.currentDate())
        main_widget.setMinimumDate(QtCore.QDate(constants.constants['PRICE_YEAR_CUTOFF'], 1,1))
        main_widget.setObjectName(format)
        main_widget.setEnabled(False)

    elif format == 'decimal':
        main_widget = QtWidgets.QLineEdit()
        main_widget.setObjectName(format)
        main_widget.setValidator(QtGui.QDoubleValidator(-100, 100, 5, main_widget))
        main_widget.setEnabled(False)
        main_widget.setSizePolicy(QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Maximum, QtWidgets.QSizePolicy.Maximum))

    elif format == 'currency':
        main_widget = QtWidgets.QLineEdit()
        main_widget.setObjectName(format)
        # https://stackoverflow.com/questions/354044/what-is-the-best-u-s-currency-regex
        main_widget.setValidator(QtGui.QRegularExpressionValidator(r"[+-]?[0-9]{1,3}(?:,?[0-9]{3})*(?:\.[0-9]{2})", main_widget))
        main_widget.setEnabled(False)
        main_widget.setSizePolicy(QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Maximum, QtWidgets.QSizePolicy.Maximum))

    
    elif format == 'integer':
        main_widget = QtWidgets.QLineEdit()
        main_widget.setObjectName(format)
        main_widget.setValidator(QtGui.QIntValidator(0, 100, main_widget))
        main_widget.setEnabled(False)
        main_widget.setSizePolicy(QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Maximum, QtWidgets.QSizePolicy.Maximum))

    
    elif format == 'select':
        return None
    

    elif format == 'flag':
        main_widget = QtWidgets.QRadioButton(title)
        main_widget.setObjectName(format)
        main_widget.setSizePolicy(QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Maximum, QtWidgets.QSizePolicy.Maximum))
    
    elif format == 'group':
        return None

    elif format == 'symbols':
        main_widget = QtWidgets.QLineEdit()
        main_widget.setObjectName(format)
        main_widget.setMaxLength(100)
        main_widget.setSizePolicy(QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Maximum, QtWidgets.QSizePolicy.Maximum))


    else:
        main_widget = QtWidgets.QWidget()

    widget.layout().addWidget(label_widget)
    widget.layout().addWidget(main_widget)

    if optional:
       toggle_widget.stateChanged.connect(lambda : main_widget.setEnabled((not main_widget.isEnabled())))
       widget.layout().addWidget(toggle_widget)
    
    return widget

def set_policy_on_widget_list(widget_list: List[QtWidgets.QWidget], policy: QtWidgets.QSizePolicy):
    for widget in widget_list:
        widget.setSizePolicy(policy)