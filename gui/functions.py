import sys
import matplotlib

from PyQt5 import QtGui, QtCore, QtWidgets


import app.statistics as statistics

import util.logger as logger
import util.helpers as helper
import util.plotter as plotter

output = logger.Logger('gui.functions')

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

class CalculateWidget(QtWidgets.QWidget):
    def __init__(self, widget_title, button_msg, calculate_function):
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

        self.result = QtWidgets.QLabel("Result", alignment=QtCore.Qt.AlignRight)
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

        self.clear_button.clicked.connect(self.clear)
        self.calculate_button.clicked.connect(calculate_function)
        self.symbol_input.returnPressed.connect(calculate_function)


    @QtCore.Slot()
    def clear(self):
        self.symbol_input.clear()
        self.result.hide()

class RiskReturnWidget(CalculateWidget):
    def __init__(self):
        super().__init__(widget_title="Risk-Return Profile Over Last 100 Days", button_msg="Calculate Profile", 
                            calculate_function=self.calculate)

    @QtCore.Slot()
    def calculate(self):
        user_symbols = self.symbol_input.text().upper().split(",")

        formatted_result = "(return, volatility) \n"
        for user_symbol in user_symbols:
            user_symbol = user_symbol.strip()
            stats = statistics.calculate_risk_return(user_symbol)
            if stats:
                annual_ret, annual_vol = str(100*stats['annual_return'])[:5], str(100*stats['annual_volatility'])[:5]
                formatted_result += f'{user_symbol} = ({annual_ret} %, {annual_vol} %) \n'
            
            else: 
                formatted_result += f'Price History Not Found For {user_symbol} \n'

        self.result.setText(formatted_result)
        self.result.show()

class CorrelationWidget(CalculateWidget):

    def __init__(self):
        super().__init__(widget_title = "Correlation Over Last 100 Days", button_msg="Calculate Correlation",
                            calculate_function = self.calculate)

    @QtCore.Slot()
    def calculate(self):
        user_symbols = self.symbol_input.text().upper().split(",")
        correlation_matrix = statistics.get_correlation_matrix_string(user_symbols)
        self.result.setText(correlation_matrix)
        self.result.show()

class EfficientFrontierWidget(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()

class OptimizerWidget(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()    

class MovingAverageWidget(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.title = QtWidgets.QLabel("Rolling Moving Average Plot", alignment=QtCore.Qt.AlignTop)
        self.title.setFont(get_label_font())

        self.message = QtWidgets.QLabel("Please separate symbols with a comma", alignment=QtCore.Qt.AlignBottom)
        self.message.setFont(get_msg_font())    

        self.calculate_button = QtWidgets.QPushButton("Calculate MAs")
        self.calculate_button.setAutoDefault(True)
            # emits 'clicked' when return is pressed

        self.clear_button = QtWidgets.QPushButton("Clear")
        self.clear_button.setAutoDefault(True)
            # emits 'clicked' when return is pressed
        
        self.symbol_input = QtWidgets.QLineEdit()
        self.symbol_input.setMaxLength(100)
        
        self.layout = QtWidgets.QVBoxLayout()
        self.layout.addWidget(self.title)
        self.layout.addStretch()
        self.layout.addWidget(self.message)
        self.layout.addWidget(self.symbol_input)
        self.layout.addWidget(self.calculate_button)
        self.layout.addWidget(self.clear_button)
        self.setLayout(self.layout)

        self.clear_button.clicked.connect(self.clear)
        self.calculate_button.clicked.connect(self.calculate)
        self.symbol_input.returnPressed.connect(self.calculate)
    
        self.displayed = False

    @QtCore.Slot()
    def clear(self):
        self.symbol_input.clear()
        if self.displayed:
            self.displayed = False
            self.layout.removeWidget(self.figure)
            self.figure.deleteLater()
            self.figure = None

    @QtCore.Slot()
    def calculate(self):
        user_symbols = self.symbol_input.text().upper().split(",")
        moving_averages = statistics.calculate_moving_averages(user_symbols)
        figure = plotter.plot_moving_averages(symbols=user_symbols, averages=moving_averages, show=False)
        self.figure = figure
        self.layout.insertWidget(1, self.figure)
        self.displayed = True

