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
from scrilla import static
from scrilla.static import keys
# TODO: conditional import based on ANALYSIS_MODE
from scrilla.analysis import markets, optimizer
from scrilla.analysis.models.geometric import statistics
from scrilla.analysis.objects.portfolio import Portfolio

from scrilla.util import outputter, helper, plotter

from scrilla.gui import formats, utilities
from scrilla.gui.widgets.components import ArgumentWidget, CompositeWidget, \
                                            GraphWidget, TableWidget, generate_control_skeleton

logger = outputter.Logger('gui.functions', settings.LOG_LEVEL)

class RiskReturnWidget(QtWidgets.QWidget):
    def __init__(self, layer):
        super().__init__()
        self.setObjectName(layer)
        self._init_profile_widgets()
        self._arrange_profile_widgets()

    @staticmethod
    def _configure_control_skeleton():
        controls = generate_control_skeleton()
        controls['start_date'] = True
        controls['end_date'] = True
        return controls

    def _init_profile_widgets(self):
        self.composite_widget = CompositeWidget(keys.keys['GUI']['TEMP']['PROFILE'], 
                                                    widget_title="Risk Analysis",
                                                    table_title="CAPM Risk Profile",
                                                    graph_title="Risk-Return Plane",
                                                    layer = utilities.get_next_layer(self.objectName()))
        self.arg_widget = ArgumentWidget(calculate_function=self.calculate,
                                            clear_function=self.clear,
                                            controls= RiskReturnWidget._configure_control_skeleton(),
                                            layer = utilities.get_next_layer(self.objectName()))
        self.setLayout(QtWidgets.QHBoxLayout())

    def _arrange_profile_widgets(self):
        self.arg_widget.setSizePolicy(QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum,
                                                            QtWidgets.QSizePolicy.Expanding))
        self.layout().addWidget(self.composite_widget)
        self.layout().addWidget(self.arg_widget)

    @QtCore.Slot()
    def calculate(self):
        if self.composite_widget.graph_widget.figure.isVisible():
            self.composite_widget.graph_widget.figure.hide()

        symbols = helper.split_and_strip(self.arg_widget.get_symbol_input().text())

        self.composite_widget.table_widget.table.setRowCount(len(symbols))
        self.composite_widget.table_widget.table.setColumnCount(5)
        self.composite_widget.table_widget.table.setHorizontalHeaderLabels(['Return','Volatility', 'Sharpe', 'Beta', 'Equity Cost'])
        self.composite_widget.table_widget.table.setVerticalHeaderLabels(symbols)

        profiles = {}
        for i, symbol in enumerate(symbols):
            profiles[symbol] = statistics.calculate_risk_return(symbol)
            profiles[symbol][keys.keys['APP']['PROFILE']['SHARPE']] = markets.sharpe_ratio(symbol)
            profiles[symbol][keys.keys['APP']['PROFILE']['BETA']] = markets.market_beta(symbol)
            profiles[symbol][keys.keys['APP']['PROFILE']['EQUITY']] = markets.cost_of_equity(symbol)

            formatted_profile = formats.format_profile(profiles[symbol])

            for j, statistic in enumerate(formatted_profile.keys()):
                table_item = QtWidgets.QTableWidgetItem(formatted_profile[statistic])
                table_item.setTextAlignment(QtCore.Qt.AlignHCenter)
                self.composite_widget.table_widget.table.setItem(i, j, table_item)

        plotter.plot_profiles(symbols=symbols, profiles=profiles, show=False,
                                        savefile=f'{settings.TEMP_DIR}/{keys.keys["GUI"]["TEMP"]["PROFILE"]}')

        self.composite_widget.graph_widget.set_pixmap()
        self.composite_widget.table_widget.show_table()

    def resizeEvent(self, event: QtGui.QResizeEvent) -> None:
        if self.composite_widget.graph_widget.figure.isVisible():
            self.composite_widget.graph_widget.set_pixmap()
        return super().resizeEvent(event)

    @QtCore.Slot()
    def clear(self):
        self.composite_widget.graph_widget.figure.hide()
        self.composite_widget.table_widget.table.clear()
        self.arg_widget.get_symbol_input().clear()

class CorrelationWidget(QtWidgets.QWidget):
    def __init__(self, layer):
        super().__init__()
        self.setObjectName(layer)

    @staticmethod
    def _configure_control_skeleton():
        controls = generate_control_skeleton()
        controls['start_date'] = True
        controls['end_date'] = True
        return controls

    def _init_correlation_widgets(self):
        self.table_widget = TableWidget(widget_title="Correlation Matrix")
        self.arg_widget = ArgumentWidget(calculate_function=self.calculate,
                                            clear_function=self.clear,
                                            controls=CorrelationWidget._configure_control_skeleton(),
                                            layer=utilities.get_next_layer(self.objectName()))
        self.setLayout(QtWidgets.QVBoxLayout())

    def _arrange_correlation_widgets(self):
        self.layout().addWidget(self.table_widget)
        self.layout().addWidget(self.arg_widget)

    @QtCore.Slot()
    def calculate(self):
        if self.table_widget.table.isVisible():
            self.table_widget.table.clear()
            self.table_widget.table.hide()

        symbols = helper.split_and_strip(self.arg_widget.get_symbol_input().text())

        if len(symbols) > 1:
            self.table_widget.table.setRowCount(len(symbols))
            self.table_widget.table.setColumnCount(len(symbols))

            self.table_widget.table.setHorizontalHeaderLabels(symbols)
            self.table_widget.table.setVerticalHeaderLabels(symbols)

            matrix = statistics.correlation_matrix(tickers=symbols)
            for i in range(0, len(symbols)):
                for j in range(i, len(symbols)):
                    item_1 = QtWidgets.QTableWidgetItem(helper.format_float_percent(matrix[i][j]))
                    item_1.setTextAlignment(QtCore.Qt.AlignHCenter)

                    item_2 = QtWidgets.QTableWidgetItem(helper.format_float_percent(matrix[i][j]))
                    item_2.setTextAlignment(QtCore.Qt.AlignHCenter)

                    self.table_widget.table.setItem(j, i, item_1)
                    self.table_widget.table.setItem(i, j, item_2)
        else:
            print('error handling goes here')

        self.table_widget.show_table()

    @QtCore.Slot()
    def clear(self):
        self.arg_widget.get_symbol_input().clear()
        self.table_widget.table.clear()
        self.table_widget.table.hide()

class OptimizerWidget(QtWidgets.QWidget):
    def __init__(self, layer):
        super().__init__()
        self.setObjectName(layer)
        self._init_optimizer_widgets()
        self._arrange_optimizer_widgets()

    @staticmethod
    def _configure_control_skeleton():
        controls = generate_control_skeleton()
        controls['start_date'] = True
        controls['end_date'] = True
        return controls

    def _init_optimizer_widgets(self):
        self.table_widget = TableWidget(widget_title="Optimization Results")
        self.arg_widget = ArgumentWidget(calculate_function=self.optimize,
                                            clear_function=self.clear,
                                            controls=OptimizerWidget._configure_control_skeleton(),
                                            layer=utilities.get_next_layer(self.objectName()))
        self.setLayout(QtWidgets.QVBoxLayout())

    def _arrange_optimizer_widgets(self):
        self.layout().addWidget(self.table_widget)
        self.layout().addWidget(self.arg_widget)

    @QtCore.Slot()
    def optimize(self):
        if self.table_widget.table.isVisible():
            self.table_widget.table.clear()
            self.table_widget.table.hide()

        symbols = helper.split_and_strip(self.arg_widget.get_symbol_input().text())

        # TODO: better error checking
        if len(symbols) > 1:
            self.table_widget.table.setRowCount(len(symbols))
            self.table_widget.table.setVerticalHeaderLabels(symbols)

            # investment = self.portfolio_value.text()

            this_portfolio = Portfolio(tickers=symbols)
            allocation = optimizer.optimize_portfolio_variance(portfolio=this_portfolio)
            
            # self.result.setText(formats.format_allocation_profile_title(allocation, this_portfolio))
            
           # if not investment:
                # self.table_widget.table.setColumnCount(1)
                # labels = ['Allocation']
            # else:
                # self.table_widget.table.setColumnCount(2)
                # labels = ['Allocation', 'Shares']
                # shares = this_portfolio.calculate_approximate_shares(allocation, float(investment))

            # self.table_widget.table.setHorizontalHeaderLabels(labels)


            # for i in range(len(symbols)):
              #   item = QtWidgets.QTableWidgetItem(formats.format_allocation(allocation[i]))
                # item.setTextAlignment(QtCore.Qt.AlignHCenter)
                # self.table_widget.table.setItem(i, 0, item)
                # if investment:
                  #  share_item = QtWidgets.QTableWidgetItem(str(shares[i]))
                  #  share_item.setTextAlignment(QtCore.Qt.AlignHCenter)
                  #  self.table_widget.table.setItem(i, 1, share_item)
            
            # self.table_widget.table.resizeColumnsToContents()
            # self.table_widget.table.show()
            # self.result.show()
        
        # else:
          #   self.result.setText("Error Occurred. Check Input and Try Again.")
            # self.result.show()

    @QtCore.Slot()
    def clear(self):
        self.table_widget.table.clear()
        self.table_widget.table.hide()

class EfficientFrontierWidget(QtWidgets.QWidget):
    def __init__(self, layer):
        super().__init__()
        self.setObjectName(layer)
        self._init_frontier_widgets()
        self._arrange_frontier_widgets()
    @staticmethod
    def _configure_control_skeleton():
        controls = generate_control_skeleton()
        controls['start_date'] = True
        controls['end_date'] = True
        return controls

    def _init_frontier_widgets(self):
        self.graph_widget = GraphWidget(tmp_graph_key=keys.keys['GUI']['TEMP']['FRONTIER'])
        self.arg_widget = ArgumentWidget(calculate_function=self.calculate, 
                                            clear_function=self.clear,
                                            controls=EfficientFrontierWidget._configure_control_skeleton(),
                                            layer=utilities.get_next_layer(self.objectName()))
        self.setLayout(QtWidgets.QVBoxLayout())
        # TODO: portfolio tabs

    def _arrange_frontier_widgets(self):
        self.layout().addWidget(self.graph_widget)
        self.layout().addWidget(self.arg_widget)


    def resizeEvent(self, event: QtGui.QResizeEvent) -> None:
        if self.graph_widget.figure.isVisible():
            self.graph_widget.set_pixmap()
        return super().resizeEvent(event)

    @QtCore.Slot()
    def calculate(self):
        if self.graph_widget.figure.isVisible():
            self.graph_widget.figure.hide()

        symbols = helper.split_and_strip(self.arg_widget.get_symbol_input().text())

        this_portfolio = Portfolio(tickers=symbols)
        frontier = optimizer.calculate_efficient_frontier(portfolio=this_portfolio)
        plotter.plot_frontier(portfolio=this_portfolio, 
                                frontier=frontier, 
                                show=False, 
                                savefile=f'{settings.TEMP_DIR}/{keys.keys["GUI"]["TEMP"]["FRONTIER"]}')

        self.graph_widget.set_pixmap()
    
    @QtCore.Slot()
    def clear(self):
        self.graph_widget.figure.hide()
        self.arg_widget.get_symbol_input().clear()

class MovingAverageWidget(QtWidgets.QWidget):
    def __init__(self, layer):
        super().__init__()
        self.setObjectName(layer)
        self._init_average_widgets()
        self._arrange_average_widgets()

    def _init_average_widgets(self):
        self.graph_widget = GraphWidget(keys.keys['GUI']['TEMP']['AVERAGES'])
        self.arg_widget = ArgumentWidget(calculate_function=self.calculate,
                                            clear_function=self.clear,
                                            controls = generate_control_skeleton(),
                                            layer=utilities.get_next_layer(self.objectName()))
        self.setLayout(QtWidgets.QVBoxLayout())

    def _arrange_average_widgets(self):
        self.layout().addWidget(self.graph_widget)
        self.layout().addWidget(self.arg_widget)
        
    def resizeEvent(self, event: QtGui.QResizeEvent) -> None:
        if self.graph_widget.figure.isVisible():
            self.graph_widget.set_pixmap()
        return super().resizeEvent(event)

    @QtCore.Slot()
    def calculate(self):
        if self.graph_widget.figure.isVisible():
            self.graph_widget.figure.hide()

        symbols = helper.split_and_strip(self.arg_widget.get_symbol_input().text())

        moving_averages = statistics.calculate_moving_averages(symbols)
        periods = [settings.MA_1_PERIOD, settings.MA_2_PERIOD, settings.MA_3_PERIOD]
        plotter.plot_moving_averages(symbols=symbols, 
                                        averages_output=moving_averages, 
                                        periods=periods, 
                                        show=False, 
                                        savefile=f'{settings.TEMP_DIR}/averages')
        
        self.graph_widget.set_pixmap()
    
    @QtCore.Slot()
    def clear(self):
        self.arg_widget.get_symbol_input().clear()
        self.graph_widget.figure.hide()