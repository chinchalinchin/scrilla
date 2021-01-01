import sys

from PySide6 import QtCore, QtWidgets, QtGui

import app.statistics as statistics

import util.logger as logger
import util.helpers as helper

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

class RiskProfileWidget(CalculateWidget):
    def __init__(self):
        super().__init__(widget_title="Risk-Profile Over Last 100 Days", button_msg="Calculate Profile", 
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
        entire_formatted_result, formatted_title = "", ""

        line_length, percent_length = 0, 0
        new_line=""
        no_symbols = len(user_symbols)

        for i in range(no_symbols):
            this_symbol = user_symbols[i].strip()
            symbol_string = f'{this_symbol} '
            if i != 0:
                this_line = symbol_string + ' '*(line_length - len(symbol_string) - 7*(no_symbols - i))
            else: 
                this_line = symbol_string

            new_line = this_line
            
            for j in range(i, no_symbols):
                if j == i:
                    new_line += " 100.0%"
                
                else:
                    that_symbol = user_symbols[j].strip()
                    result = statistics.calculate_correlation(this_symbol, that_symbol) 
                    formatted_result = str(100*result['correlation'])[:5]
                    new_line += f' {formatted_result}%'

            print(new_line)
            entire_formatted_result += new_line + '\n'
            
            if i == 0:
                line_length = len(new_line)
                output.debug(f'Line length set equal to {line_length}')

        for symbol in user_symbols:
            formatted_title += f' {symbol}'
        formatted_title += '\n'


        whole_thing = formatted_title + entire_formatted_result
        self.result.setText(whole_thing)
        self.result.show()

class EfficientFrontierWidget(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()

class OptimizerWidget(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()    