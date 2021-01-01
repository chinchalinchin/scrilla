import sys

from PySide6 import QtCore, QtWidgets, QtGui

import app.statistics as statistics

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

class RiskProfileWidget(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()

        self.title = QtWidgets.QLabel("Risk-Profile Over Last 100 Days", alignment=QtCore.Qt.AlignTop)
        self.title.setFont(get_label_font())

        self.message = QtWidgets.QLabel("Please separate symbols with a comma", alignment=QtCore.Qt.AlignBottom)
        self.message.setFont(get_msg_font())    

        self.calculate_button = QtWidgets.QPushButton("Calculate Risk-Return")
        self.calculate_button.setAutoDefault(True)
            # emits 'clicked' when return is pressed

        self.clear_button = QtWidgets.QPushButton("Clear")
        self.clear_button.setAutoDefault(True)
            # emits 'clicked' when return is pressed

        self.result = QtWidgets.QLabel("Result", alignment=QtCore.Qt.AlignCenter)
        self.result.setFont(get_result_font())
        self.result.hide()
        
        self.symbol_input = QtWidgets.QLineEdit()
        self.symbol_input.setMaxLength(100)
        
        self.layout = QtWidgets.QVBoxLayout()

        self.layout.addWidget(self.title)
        self.layout.addStretch()
        self.layout.addWidget(self.result)
        self.layout.addWidget(self.message)
        self.layout.addWidget(self.symbol_input)
        self.layout.addWidget(self.calculate_button)
        self.layout.addWidget(self.clear_button)

        self.setLayout(self.layout)

        self.calculate_button.clicked.connect(self.calculate)
        self.clear_button.clicked.connect(self.clear)
        self.symbol_input.returnPressed.connect(self.calculate)

    @QtCore.Slot()
    def calculate(self):
        user_symbols = self.symbol_input.text().upper().split(",")

        formatted_result = ""
        for user_symbol in user_symbols:
            user_symbol = user_symbol.strip()
            stats = statistics.calculate_risk_return(user_symbol)
            if stats:
                annual_ret, annual_vol = str(stats['annual_return'])[:5], str(stats['annual_volatility'])[:5]
                formatted_result += f'{user_symbol}_(return, vol) = ({annual_ret}, {annual_vol}) \n'
            else: 
                formatted_result += f'Price History Not Found For {user_symbol} \n'
        self.result.setText(formatted_result)
        self.result.show()

    @QtCore.Slot()
    def clear(self):
        self.symbol_input.clear()
        self.result.hide()

class CorrelationWidget(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()

class EfficientFrontierWidget(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()

class OptimizerWidget(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()    