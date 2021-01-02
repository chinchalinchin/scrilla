import sys, time
import matplotlib

from PyQt5 import QtGui, QtCore, QtWidgets


import app.statistics as statistics
import app.settings as settings
import app.optimizer as optimizer
import app.portfolio as portfolio

import util.logger as logger
import util.helpers as helper
import util.plotter as plotter

from gui.widgets import CalculateWidget, GraphWidget, \
                            TableWidget, PortfolioWidget

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
        if self.table.isVisible():
            output.debug('Clearing correlation matrix from table widget.')
            self.table.clear()

        user_symbols = helper.strip_string_array(self.symbol_input.text().upper().split(","))
        no_symbols = len(user_symbols)

        if no_symbols > 1:
            self.table.setRowCount(no_symbols)
            self.table.setColumnCount(no_symbols)
            self.table.setHorizontalHeader(QtWidgets.QHeaderView(QtCore.Qt.Horizontal))
            self.table.setHorizontalHeaderLabels(user_symbols)
            self.table.horizontalHeader().setStretchLastSection(True)
            self.table.setVerticalHeader(QtWidgets.QHeaderView(QtCore.Qt.Vertical))
            self.table.setVerticalHeaderLabels(user_symbols)

            for i in range(len(user_symbols)):
                for j in range(i, len(user_symbols)):
                    if i == j:
                        item = QtWidgets.QTableWidgetItem("100.0%")
                        self.table.setItem(i, j, item)
                        
                    else:    
                        output.debug(f'Calculating correlation for ({user_symbols[i]}, {user_symbols[j]})')
                        correlation = statistics.calculate_correlation(user_symbols[i], user_symbols[j])
                        formatted_correlation = str(100*correlation["correlation"])[:settings.SIG_FIGS]+"%"
                        item_1 = QtWidgets.QTableWidgetItem(formatted_correlation)
                        item_1.setTextAlignment(Qt.AlignHCenter)
                        item_2 = QtWidgets.QTableWidgetItem(formatted_correlation)
                        item_2.setTextAlignment(Qt.AlignHCenter)

                        output.debug(f'Appending correlation = {formatted_correlation} to ({i}, {j}) and ({j}, {i}) entries of matrix')
                        self.table.setItem(j, i, item_1)
                        self.table.setItem(i, j, item_2)
        else:
            self.table.setRowCount(1)
            self.table.setColumnCount(1)
            self.table.setHorizontalHeader(QtWidgets.QHeaderView(QtCore.Qt.Horizontal))
            self.table.setHorizontalHeaderLabels(["Error, Will Robinson"])
            self.table.horizontalHeader().setStretchLastSection(True)
            error_item = QtWidgets.QTableWidgetItem("Error Occurred. Check Input and Try Again.")
            error_item.setTextAlignment(Qt.AlignHCenter)
            self.table.setItem(0, 0, error_item)

        self.table.resizeColumnsToContents()
        self.table.show()

class OptimizerWidget(PortfolioWidget):
    def __init__(self):
        super().__init__(widget_title="Portfolio Allocation Optimization",
                            min_function=self.minimize, opt_function=self.optimize)


    @QtCore.Slot()
    def minimize(self):
        if self.result_table.isVisible():
            self.reset_table()

        if self.result.isVisible():
            self.result.clear()

        user_symbols = helper.strip_string_array(self.symbol_input.text().upper().split(","))
        no_symbols = len(user_symbols)

        if no_symbols > 1:
            investment = self.portfolio_value.text()

            output.debug(f'Optimizing Portfolio : {user_symbols}.')
            allocation = optimizer.minimize_portfolio_variance(equities=user_symbols)
            this_portfolio = portfolio.Portfolio(user_symbols)
            
            output.debug(helper.format_allocation_profile(allocation, this_portfolio))
            self.result.setText(helper.format_allocation_profile(allocation, this_portfolio))

            self.result_table.setRowCount(no_symbols)
            self.result_table.setVerticalHeader(QtWidgets.QHeaderView(QtCore.Qt.Vertical))
            self.result_table.setVerticalHeaderLabels(user_symbols)
            
            if not investment:
                self.result_table.setColumnCount(1)
                labels = ['Allocation']
            else:
                self.result_table.setColumnCount(2)
                labels = ['Allocation', 'Shares']
                shares = this_portfolio.calculate_approximate_shares(allocation, float(investment))

            self.result_table.setHorizontalHeader(QtWidgets.QHeaderView(QtCore.Qt.Horizontal))
            self.result_table.setHorizontalHeaderLabels(labels)
            self.result_table.horizontalHeader().setStretchLastSection(True)


            for i in range(no_symbols):
                this_allocation = allocation[i]
                formatted_allocation = str(100*this_allocation)[:settings.SIG_FIGS]+"%"
                item = QtWidgets.QTableWidgetItem(formatted_allocation)
                item.setTextAlignment(QtCore.Qt.AlignHCenter)
                self.result_table.setItem(i, 0, item)
                if investment:
                    share_item = QtWidgets.QTableWidgetItem(str(shares[i]))
                    share_item.setTextAlignment(QtCore.Qt.AlignHCenter)
                    self.result_table.setItem(i, 1, share_item)
            
            self.result_table.resizeColumnsToContents()
            self.result_table.show()
            self.result.show()
        
        else:
            self.result.setText("Error Occurred. Check Input and Try Again.")
            self.result.show()


    @QtCore.Slot()
    def optimize(self):
        pass

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
        self.layout.insertWidget(1, self.figure, 1)
        self.displayed = True 

class MovingAverageWidget(GraphWidget):
    def __init__(self):
        super().__init__(widget_title = "Rolling Moving Average Plot", button_msg="Calculate MAs",
                            display_function=self.display)
        
    @QtCore.Slot()
    def display(self):
        if self.displayed:
            self.layout.removeWidget(self.figure)
            self.figure.deleteLater()
            self.figure = None
            time.sleep(1)
        user_symbols = helper.strip_string_array(self.symbol_input.text().upper().split(","))
        moving_averages = statistics.calculate_moving_averages(user_symbols)
        figure = plotter.plot_moving_averages(symbols=user_symbols, averages=moving_averages, show=False)
        self.figure = figure
        self.layout.insertWidget(1, self.figure, 1)
        self.displayed = True

