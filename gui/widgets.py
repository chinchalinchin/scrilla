from PyQt5 import QtGui, QtCore, QtWidgets

def get_label_font():
    font = QtGui.QFont('Arial', 10)
    font.setBold(True)
    font.setUnderline(True)
    return font

def get_msg_font():
    font = QtGui.QFont('Arial', 8)
    font.setItalic(True)
    return font

def get_result_font():
    font = QtGui.QFont('Arial', 8)
    font.setBold(True)
    return font


# Base Widget to get asset symbol input
class SymbolWidget(QtWidgets.QWidget):
    def __init__(self, widget_title, button_msg):
        super().__init__()
        self.title = QtWidgets.QLabel(widget_title, alignment=QtCore.Qt.AlignTop)
        self.title.setFont(get_label_font())

        self.message = QtWidgets.QLabel("Please separate symbols with a comma", alignment=QtCore.Qt.AlignBottom)
        self.message.setFont(get_msg_font())    

        self.calculate_button = QtWidgets.QPushButton(button_msg)
        self.calculate_button.setAutoDefault(True)
            # emits 'clicked' when return is pressed

        self.clear_button = QtWidgets.QPushButton("Clear")
        self.clear_button.setAutoDefault(True)
            # emits 'clicked' when return is pressed
        
        self.symbol_input = QtWidgets.QLineEdit()
        self.symbol_input.setMaxLength(100)

class CalculateWidget(SymbolWidget):
    def __init__(self, widget_title, button_msg, calculate_function):
        super().__init__(widget_title=widget_title, button_msg=button_msg)

        self.result = QtWidgets.QLabel("Result", alignment=QtCore.Qt.AlignRight)
        self.result.setFont(get_result_font())
        self.result.hide()
        
        self.layout = QtWidgets.QVBoxLayout()

        self.layout.addWidget(self.title)
        self.layout.addStretch()
        self.layout.addWidget(self.result)
        self.layout.addWidget(self.message)
        self.layout.addWidget(self.symbol_input)
        self.layout.addWidget(self.calculate_button)
        self.layout.addWidget(self.clear_button)

        self.setLayout(self.layout)

        self.clear_button.clicked.connect(self.clear)
        self.calculate_button.clicked.connect(calculate_function)
        self.symbol_input.returnPressed.connect(calculate_function)

    @QtCore.Slot()
    def clear(self):
        self.symbol_input.clear()
        self.result.hide()

class TableWidget(SymbolWidget):
    def __init__(self, widget_title, button_msg, table_function):
        super().__init__(widget_title=widget_title, button_msg=button_msg)

        self.table = QtWidgets.QTableWidget()
        self.table.hide()

        self.layout = QtWidgets.QVBoxLayout()
    
        self.layout.addWidget(self.title)
        self.layout.addStretch()
        self.layout.addWidget(self.table)
        self.layout.addWidget(self.message)
        self.layout.addWidget(self.symbol_input)
        self.layout.addWidget(self.calculate_button)
        self.layout.addWidget(self.clear_button)

        self.setLayout(self.layout)

        self.clear_button.clicked.connect(self.clear)
        self.calculate_button.clicked.connect(table_function)
        self.symbol_input.returnPressed.connect(table_function)
    
        self.displayed = False
        self.figure = None

    @QtCore.Slot()
    def clear(self):
        self.symbol_input.clear()
        self.table.hide()

# NOTE: display_function MUST set displayed = True and set
#       figure to FigureCanvasAgg object
class GraphWidget(SymbolWidget):
    def __init__(self, widget_title, button_msg, display_function):
        super().__init__(widget_title=widget_title, button_msg=button_msg)
        
        self.layout = QtWidgets.QVBoxLayout()
    
        self.layout.addWidget(self.title)
        self.layout.addStretch()
        self.layout.addWidget(self.message)
        self.layout.addWidget(self.symbol_input)
        self.layout.addWidget(self.calculate_button)
        self.layout.addWidget(self.clear_button)

        self.setLayout(self.layout)

        self.clear_button.clicked.connect(self.clear)
        self.calculate_button.clicked.connect(display_function)
        self.symbol_input.returnPressed.connect(display_function)
    
        self.displayed = False
        self.figure = None

    @QtCore.Slot()
    def clear(self):
        self.symbol_input.clear()
        if self.displayed:
            self.displayed = False
            self.layout.removeWidget(self.figure)
            self.figure.deleteLater()
            self.figure = None