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

from PySide6 import QtGui, QtCore, QtWidgets


from scrilla import settings
import scrilla.analysis.models.geometric.statistics as statistics
import scrilla.analysis.optimizer as optimizer
import scrilla.analysis.objects.portfolio as portfolio

from scrilla.util import outputter, helper, plotter

from scrilla.gui import formats, utilities
from scrilla.gui.widgets import CompositeWidget, GraphWidget, \
                            TableWidget, PortfolioWidget

logger = outputter.Logger('gui.functions', settings.LOG_LEVEL)

class RiskReturnWidget(CompositeWidget):
    def __init__(self, objectName):
        super().__init__(widget_title="Risk-Return Profile Over Last 100 Days", button_msg="Calculate Profile", 
                            calculate_function=self.calculate, clear_function=self.clear)
        self.setObjectName(objectName)
        self._init_profile_widgets()
        self._arrange_profile_widgets()
        self._stage_profile_widgets()

    def _init_profile_widgets(self):
        self.figure = QtWidgets.QLabel("Risk Profile Graph")

    def _arrange_profile_widgets(self):
        self.figure.setAlignment(QtCore.Qt.AlignHCenter)
        self.right_layer.layout().insertWidget(0, self.figure, 1)

    def _stage_profile_widgets(self):
        self.figure.hide()

    @QtCore.Slot()
    def calculate(self):
        if self.figure.isVisible():
            self.figure.hide()

        symbols = helper.split_and_strip(self.symbol_input.text())

        self.table.setRowCount(len(symbols))
        self.table.setColumnCount(2)
        self.table.setHorizontalHeader(QtWidgets.QHeaderView(QtCore.Qt.Horizontal))
        self.table.setHorizontalHeaderLabels(['Return','Risk'])
        self.table.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
        self.table.setVerticalHeader(QtWidgets.QHeaderView(QtCore.Qt.Vertical))
        self.table.setVerticalHeaderLabels(symbols)
        # self.table.verticalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)

        profiles = {}
        for symbol in symbols:
            stats = statistics.calculate_risk_return(symbol)
            profiles[symbol] = stats
            formatted_ret, formatted_vol = formats.format_risk_return(stats)

            ret_item = QtWidgets.QTableWidgetItem(formatted_ret)
            ret_item.setTextAlignment(QtCore.Qt.AlignHCenter)
            vol_item = QtWidgets.QTableWidgetItem(formatted_vol)
            vol_item.setTextAlignment(QtCore.Qt.AlignHCenter)
            
            self.table.setItem(symbols.index(symbol), 0, ret_item)
            self.table.setItem(symbols.index(symbol), 1, vol_item)

        plotter.plot_profiles(symbols=symbols, profiles=profiles, show=False,
                                        savefile=f'{settings.TEMP_DIR}/profile.jpeg')

        self.figure.setPixmap(utilities.generate_pixmap_from_temp(self.width(), self.height(),'profile'))
        self.figure.show()
        self.table.resizeColumnsToContents()
        self.table.show()

    def resizeEvent(self, event: QtGui.QResizeEvent) -> None:
        if self.figure.isVisible():
            self.figure.setPixmap(utilities.generate_pixmap_from_temp(self.width(), self.height(),'profile'))
        return super().resizeEvent(event)

    @QtCore.Slot()
    def clear(self):
        self.figure.hide()
        self.table.clear()
        self.symbol_input.clear()

class CorrelationWidget(TableWidget):
    def __init__(self, objectName):
        super().__init__(widget_title = "Correlation Over Last 100 Days", button_msg="Calculate Correlation",
                            table_function = self.calculate_table, clear_function=self.clear)
        self.setObjectName(objectName)


    @QtCore.Slot()
    def calculate_table(self):
        if self.table.isVisible():
            self.table.clear()

        symbols = helper.split_and_strip(self.symbol_input.text())

        if len(symbols) > 1:
            self.table.setRowCount(len(symbols))
            self.table.setColumnCount(len(symbols))

            self.table.setHorizontalHeaderLabels(symbols)
            #self.table.horizontalHeader().setStretchLastSection(True)
            self.table.setVerticalHeaderLabels(symbols)

            for i, value in enumerate(symbols):
                for j in range(i, len(symbols)):
                    if i == j:
                        item = QtWidgets.QTableWidgetItem("100.0%")
                        item.setTextAlignment(QtCore.Qt.AlignHCenter)
                        self.table.setItem(i, j, item)
                        
                    else:    
                        correlation = statistics.calculate_correlation(value, symbols[j])

                        item_1 = QtWidgets.QTableWidgetItem(formats.format_correlation(correlation))
                        item_1.setTextAlignment(QtCore.Qt.AlignHCenter)

                        item_2 = QtWidgets.QTableWidgetItem(formats.format_correlation(correlation))
                        item_2.setTextAlignment(QtCore.Qt.AlignHCenter)

                        self.table.setItem(j, i, item_1)
                        self.table.setItem(i, j, item_2)
        else:
            self.table.setRowCount(1)
            self.table.setColumnCount(1)
            self.table.setHorizontalHeader(QtWidgets.QHeaderView(QtCore.Qt.Horizontal))
            self.table.setHorizontalHeaderLabels(["Error, Will Robinson"])
            self.table.horizontalHeader().setStretchLastSection(True)
            error_item = QtWidgets.QTableWidgetItem("Error Occurred. Check Input and Try Again.")
            error_item.setTextAlignment(QtCore.Qt.AlignHCenter)
            self.table.setItem(0, 0, error_item)

        self.table.resizeColumnsToContents()
        self.table.show()

    @QtCore.Slot()
    def clear(self):
        self.symbol_input.clear()
        self.error_message.hide()
        self.table.clear()
        self.table.hide()

class OptimizerWidget(PortfolioWidget):
    def __init__(self, objectName):
        super().__init__(widget_title="Portfolio Allocation Optimization",
                            optimize_function=self.optimize, 
                            clear_function=self.clear)
        self.setObjectName(objectName)

    @QtCore.Slot()
    def optimize(self):
        if self.result_table.isVisible():
            self.clear()

        symbols = helper.split_and_strip(self.symbol_input.text())

        # TODO: better error checking
        if len(symbols) > 1:
            self.result_table.setRowCount(len(symbols))
            self.result_table.setVerticalHeader(QtWidgets.QHeaderView(QtCore.Qt.Vertical))
            self.result_table.setVerticalHeaderLabels(symbols)
            self.result_table.setHorizontalHeader(QtWidgets.QHeaderView(QtCore.Qt.Horizontal))
            self.result_table.horizontalHeader().setStretchLastSection(True)

            investment = self.portfolio_value.text()

            this_portfolio = portfolio.Portfolio(tickers=symbols)
            allocation = optimizer.optimize_portfolio_variance(portfolio=this_portfolio)
            
            self.result.setText(formats.format_allocation_profile_title(allocation, this_portfolio))
            
            if not investment:
                self.result_table.setColumnCount(1)
                labels = ['Allocation']
            else:
                self.result_table.setColumnCount(2)
                labels = ['Allocation', 'Shares']
                shares = this_portfolio.calculate_approximate_shares(allocation, float(investment))
            self.result_table.setHorizontalHeaderLabels(labels)


            for i in range(len(symbols)):
                item = QtWidgets.QTableWidgetItem(formats.format_allocation(allocation[i]))
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
    def clear(self):
        self.symbol_input.clear()
        self.target_return.clear()
        self.portfolio_value.clear()
        self.result_table.clear()
        self.result_table.hide()
        self.result.clear()
        self.result.hide()

class EfficientFrontierWidget(GraphWidget):
    def __init__(self, objectName):
        super().__init__(widget_title = "Efficient Portfolio Frontier Plot", button_msg="Calculate Efficient Frontier",
                            display_function=self.display, clear_function=self.clear)
        self.setObjectName(objectName)
        self._init_frontier_widgets()
        self._arrange_frontier_widgets()
        self._stage_frontier_widgets()

    def _init_frontier_widgets(self):
        self.figure = QtWidgets.QLabel("Efficient Frontier Graph")

    def _arrange_frontier_widgets(self):
        self.figure.setAlignment(QtCore.Qt.AlignHCenter)
        self.layout().insertWidget(1, self.figure, 1)

    def _stage_frontier_widgets(self):
        self.figure.hide()

    def resizeEvent(self, event: QtGui.QResizeEvent) -> None:
        if self.figure.isVisible():
            self.figure.setPixmap(utilities.generate_pixmap_from_temp(self.width(), self.height(), 'frontier'))
        return super().resizeEvent(event)

        # TODO: DATES! & PORTFOLIO TABS
    @QtCore.Slot()
    def display(self):
        if self.figure.isVisible():
            self.figure.hide()

        symbols = helper.split_and_strip(self.symbol_input.text())

        this_portfolio = portfolio.Portfolio(tickers=symbols)
        frontier = optimizer.calculate_efficient_frontier(portfolio=this_portfolio)
        plotter.plot_frontier(portfolio=this_portfolio, 
                                frontier=frontier, 
                                show=False, 
                                savefile=f'{settings.TEMP_DIR}/frontier')

        self.figure.setPixmap(utilities.generate_pixmap_from_temp(self.width(), self.height(), 'frontier'))
        self.figure.show()
    
    @QtCore.Slot()
    def clear(self):
        self.symbol_input.clear()
        if self.figure.isVisible():
            self.figure.hide()

class MovingAverageWidget(GraphWidget):
    def __init__(self, objectName):
        super().__init__(widget_title = "Rolling Moving Average Plot", button_msg="Calculate MAs",
                            display_function=self.display, clear_function=self.clear)
        self.setObjectName(objectName)
        self._init_average_widgets()
        self._arrange_average_widgets()
        self._stage_average_widgets()

    def _init_average_widgets(self):
        self.figure = QtWidgets.QLabel("Moving Averages")

    def _arrange_average_widgets(self):
        self.figure.setAlignment(QtCore.Qt.AlignHCenter)
        self.layout().insertWidget(1, self.figure, 1)
    
    def _stage_average_widgets(self):
        self.figure.hide()
        
    def resizeEvent(self, event: QtGui.QResizeEvent) -> None:
        if self.figure.isVisible():
            self.figure.setPixmap(utilities.generate_pixmap_from_temp(self.width(), self.height(), 'averages'))
        return super().resizeEvent(event)

    @QtCore.Slot()
    def display(self):
        if self.figure.isVisible():
            self.figure.hide()

        symbols = helper.split_and_strip(self.symbol_input.text())

        moving_averages = statistics.calculate_moving_averages(symbols)
        periods = [settings.MA_1_PERIOD, settings.MA_2_PERIOD, settings.MA_3_PERIOD]
        plotter.plot_moving_averages(symbols=symbols, 
                                        averages_output=moving_averages, 
                                        periods=periods, 
                                        show=False, 
                                        savefile=f'{settings.TEMP_DIR}/averages')
        
        self.figure.setPixmap(utilities.generate_pixmap_from_temp(self.width(), self.height(), 'averages'))
        self.figure.show()
    
    @QtCore.Slot()
    def clear(self):
        self.symbol_input.clear()
        self.figure.hide()