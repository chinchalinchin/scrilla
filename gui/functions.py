import sys
import matplotlib

from PyQt5 import QtGui, QtCore, QtWidgets


import app.statistics as statistics
import app.settings as settings
import app.optimizer as optimizer
import app.portfolio as portfolio

import util.logger as logger
import util.helpers as helper
import util.plotter as plotter

from gui.widgets import CalculateWidget, GraphWidget, TableWidget

output = logger.Logger('gui.functions')

class RiskReturnWidget(CalculateWidget):
    def __init__(self):
        super().__init__(widget_title="Risk-Return Profile Over Last 100 Days", button_msg="Calculate Profile", 
                            calculate_function=self.calculate)

    @QtCore.Slot()
    def calculate(self):
        user_symbols = helper.strip_string_array(self.symbol_input.text().upper().split(","))

        formatted_result = "(return, volatility) \n"
        for user_symbol in user_symbols:
            stats = statistics.calculate_risk_return(user_symbol)
            if stats:
                annual_ret, annual_vol = str(100*stats['annual_return'])[:5], str(100*stats['annual_volatility'])[:settings.SIG_FIGS]
                formatted_result += f'{user_symbol} = ({annual_ret} %, {annual_vol} %) \n'
            
            else: 
                formatted_result += f'Price History Not Found For {user_symbol} \n'

        self.result.setText(formatted_result)
        self.result.show()

class CorrelationWidget(TableWidget):
    def __init__(self):
        super().__init__(widget_title = "Correlation Over Last 100 Days", button_msg="Calculate Correlation",
                            table_function = self.calculate_table)

    @QtCore.Slot()
    def calculate_table(self):
        user_symbols = helper.strip_string_array(self.symbol_input.text().upper().split(","))
        no_symbols = len(user_symbols)

        self.table.setRowCount(no_symbols)
        self.table.setColumnCount(no_symbols)
        self.table.setHorizontalHeader(QtWidgets.QHeaderView(QtCore.Qt.Horizontal))
        self.table.setVerticalHeader(QtWidgets.QHeaderView(QtCore.Qt.Vertical))
        self.table.setHorizontalHeaderLabels(user_symbols)
        self.table.setVerticalHeaderLabels(user_symbols)

        for i in range(len(user_symbols)):
            for j in range(i, len(user_symbols)):
                if i == j:
                    item = QtWidgets.QTableWidgetItem("100.0%")
                    self.table.setItem(i, j, item)
                    
                else:    
                    correlation = statistics.calculate_correlation(user_symbols[i], user_symbols[j])
                    formatted_correlation = str(100*correlation["correlation"])[:settings.SIG_FIGS]+"%"
                    item_1, item_2 = QtWidgets.QTableWidgetItem(formatted_correlation), QtWidgets.QTableWidgetItem(formatted_correlation)
                    self.table.setItem(j, i, item_1)
                    self.table.setItem(i, j, item_2)

        self.table.show()

class OptimizerWidget(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()   

class EfficientFrontierWidget(GraphWidget):
    def __init__(self):
        super().__init__(widget_title = "Efficient Portfolio Frontier Plot", button_msg="Calculate Efficient Frontier",
                            display_function=self.display)

    @QtCore.Slot()
    def display(self):
        user_symbols = helper.strip_string_array(self.symbol_input.text().upper().split(","))
        frontier = optimizer.calculate_efficient_frontier(equities=user_symbols)
        figure = plotter.plot_frontier(portfolio=portfolio.Portfolio(user_symbols), frontier=frontier, show=False)
        self.figure = figure
        self.layout.insertWidget(1, self.figure)
        self.displayed = True 

class MovingAverageWidget(GraphWidget):
    def __init__(self):
        super().__init__(widget_title = "Rolling Moving Average Plot", button_msg="Calculate MAs",
                            display_function=self.display)
        
    @QtCore.Slot()
    def display(self):
        user_symbols = helper.strip_string_array(self.symbol_input.text().upper().split(","))
        moving_averages = statistics.calculate_moving_averages(user_symbols)
        figure = plotter.plot_moving_averages(symbols=user_symbols, averages=moving_averages, show=False)
        self.figure = figure
        self.layout.insertWidget(1, self.figure)
        self.displayed = True

