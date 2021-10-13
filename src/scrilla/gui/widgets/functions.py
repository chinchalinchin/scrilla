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
from scrilla.static import keys, definitions
# TODO: conditional import based on ANALYSIS_MODE
from scrilla.analysis import markets, optimizer
from scrilla.analysis.models.geometric import statistics
from scrilla.analysis.objects.portfolio import Portfolio

from scrilla.util import outputter, helper, plotter

from scrilla.gui import formats, utilities
from scrilla.gui.widgets import factories, components

logger = outputter.Logger('gui.functions', settings.LOG_LEVEL)

class RiskReturnWidget(QtWidgets.QWidget):
    def __init__(self, layer):
        super().__init__()
        self.setObjectName(layer)
        self._init_widgets()
        self._arrange_widgets()
        self._stage_widgets()

    @staticmethod
    def _configure_control_skeleton():
        controls = factories.generate_control_skeleton()

        for arg in definitions.FUNC_DICT['risk_profile']['args']:
            if not definitions.ARG_DICT[arg]['cli_only']:
                controls[arg] = True

        return controls

    def _init_widgets(self):
        self.composite_widget = components.CompositeWidget(keys.keys['GUI']['TEMP']['PROFILE'], 
                                                            widget_title="Risk Analysis",
                                                            table_title="CAPM Risk Profile",
                                                            graph_title="Risk-Return Plane",
                                                            layer = utilities.get_next_layer(self.objectName()))
        self.arg_widget = components.ArgumentWidget(calculate_function=self.calculate,
                                                    clear_function=self.clear,
                                                    controls= RiskReturnWidget._configure_control_skeleton(),
                                                    layer = utilities.get_next_layer(self.objectName()))
        self.setLayout(QtWidgets.QHBoxLayout())

    def _arrange_widgets(self):
        self.layout().addWidget(self.composite_widget)
        self.layout().addWidget(self.arg_widget)

    def _stage_widgets(self):
        self.arg_widget.prime()

    @QtCore.Slot()
    def calculate(self):
        if self.composite_widget.graph_widget.figure.isVisible():
            self.composite_widget.graph_widget.figure.hide()

        symbols = self.arg_widget.get_symbol_input()

        self.composite_widget.table_widget.init_table(rows=symbols, 
                                                        columns=['Return','Volatility', 'Sharpe', 'Beta', 'Equity Cost'])

        profiles = {}
        for i, symbol in enumerate(symbols):
            profiles[symbol] = statistics.calculate_risk_return(symbol)
            profiles[symbol][keys.keys['APP']['PROFILE']['SHARPE']] = markets.sharpe_ratio(symbol)
            profiles[symbol][keys.keys['APP']['PROFILE']['BETA']] = markets.market_beta(symbol)
            profiles[symbol][keys.keys['APP']['PROFILE']['EQUITY']] = markets.cost_of_equity(symbol)

            formatted_profile = formats.format_profile(profiles[symbol])

            for j, statistic in enumerate(formatted_profile.keys()):
                table_item = factories.atomic_widget_factory(format='table-item', title=formatted_profile[statistic] )
                self.composite_widget.table_widget.table.setItem(i, j, table_item)

        plotter.plot_profiles(symbols=symbols, profiles=profiles, show=False,
                                        savefile=f'{settings.TEMP_DIR}/{keys.keys["GUI"]["TEMP"]["PROFILE"]}')

        self.composite_widget.graph_widget.set_pixmap()
        self.composite_widget.table_widget.show_table()
        self.arg_widget.fire()

    def resizeEvent(self, event: QtGui.QResizeEvent) -> None:
        if self.composite_widget.graph_widget.figure.isVisible():
            self.composite_widget.graph_widget.set_pixmap()
        return super().resizeEvent(event)

    @QtCore.Slot()
    def clear(self):
        self.composite_widget.graph_widget.figure.hide()
        self.composite_widget.table_widget.table.clear()
        self.composite_widget.table_widget.table.hide()
        self.arg_widget.prime()

class CorrelationWidget(QtWidgets.QWidget):
    def __init__(self, layer):
        super().__init__()
        self.setObjectName(layer)
        self._init_widgets()
        self._arrange_widgets()
        self._stage_widgets()

    @staticmethod
    def _configure_control_skeleton():
        controls = factories.generate_control_skeleton()

        for arg in definitions.FUNC_DICT['correlation']['args']:
            if not definitions.ARG_DICT[arg]['cli_only']:
                controls[arg] = True

        return controls

    def _init_widgets(self):
        self.table_widget = components.TableWidget(widget_title="Correlation Matrix",
                                                    layer=utilities.get_next_layer(self.objectName()))
        self.arg_widget = components.ArgumentWidget(calculate_function=self.calculate,
                                                    clear_function=self.clear,
                                                    controls=CorrelationWidget._configure_control_skeleton(),
                                                    layer=utilities.get_next_layer(self.objectName()))
        self.setLayout(QtWidgets.QHBoxLayout())

    def _arrange_widgets(self):
        self.layout().addWidget(self.table_widget)
        self.layout().addWidget(self.arg_widget)
    
    def _stage_widgets(self):
        self.arg_widget.prime()

    @QtCore.Slot()
    def calculate(self):
        if self.table_widget.table.isVisible():
            self.table_widget.table.clear()
            self.table_widget.table.hide()

        symbols = self.arg_widget.get_symbol_input()

        if len(symbols) > 1:
            self.table_widget.init_table(rows=symbols, columns=symbols)

            matrix = statistics.correlation_matrix(tickers=symbols)
            for i in range(0, len(symbols)):
                for j in range(i, len(symbols)):
                    item_upper = factories.atomic_widget_factory(format='table-item', title = helper.format_float_percent(matrix[i][j]))
                    item_lower = factories.atomic_widget_factory(format='table-item', title = helper.format_float_percent(matrix[j][i]))
                    self.table_widget.table.setItem(j, i, item_upper)
                    self.table_widget.table.setItem(i, j, item_lower)
        else:
            print('error handling goes here')

        self.table_widget.show_table()
        self.arg_widget.fire()

    @QtCore.Slot()
    def clear(self):
        self.arg_widget.prime()
        self.table_widget.table.clear()
        self.table_widget.table.hide()

class OptimizerWidget(QtWidgets.QWidget):
    def __init__(self, layer):
        super().__init__()
        self.setObjectName(layer)
        self._init_widgets()
        self._arrange_widgets()
        self._stage_widgets()

    @staticmethod
    def _configure_control_skeleton():
        controls = factories.generate_control_skeleton()
        
        for arg in definitions.FUNC_DICT['optimize_portfolio']['args']:
            if not definitions.ARG_DICT[arg]['cli_only']:
                controls[arg] = True

        return controls

    def _init_widgets(self):
        self.title = factories.atomic_widget_factory(format='heading', title=None)
        self.table_widget = components.TableWidget(widget_title="Optimization Results",
                                                    layer=utilities.get_next_layer(self.objectName()))
        self.arg_widget = components.ArgumentWidget(calculate_function=self.optimize,
                                                    clear_function=self.clear,
                                                    controls=OptimizerWidget._configure_control_skeleton(),
                                                    layer=utilities.get_next_layer(self.objectName()))
        self.setLayout(QtWidgets.QHBoxLayout())

    def _arrange_widgets(self):
        self.layout().addWidget(self.table_widget)
        self.layout().addWidget(self.arg_widget)
    
    def _stage_widgets(self):
        self.arg_widget.prime()

    @QtCore.Slot()
    def optimize(self):
        if self.table_widget.table.isVisible():
            self.table_widget.table.clear()
            self.table_widget.table.hide()

        symbols = self.arg_widget.get_symbol_input()

        # TODO: better error checking
        if len(symbols) > 1:
            investment = self.arg_widget.get_control_input('investment')
            this_portfolio = Portfolio(tickers=symbols, 
                                        start_date=self.arg_widget.get_control_input('start_date'),
                                        end_date=self.arg_widget.get_control_input('end_date'))
            allocation = optimizer.optimize_portfolio_variance(portfolio=this_portfolio,
                                                                target_return=self.arg_widget.get_control_input('target'))
            self.title.setText(formats.format_allocation_profile_title(allocation, this_portfolio))
            
            if investment is None:
                self.table_widget.init_table(rows=symbols,columns=['Allocation'])
            else:
                self.table_widget.init_table(rows=symbols,columns=['Allocation', 'Shares'])
                shares = this_portfolio.calculate_approximate_shares(allocation, float(investment))

            for i in range(len(symbols)):
                item = factories.atomic_widget_factory(format='table-item', title=helper.format_float_percent(allocation[i]))
                self.table_widget.table.setItem(i, 0, item)

                if investment is not None:
                    share_item = factories.atomic_widget_factory(format='table-item', title=str(shares[i]))
                    self.table_widget.table.setItem(i, 1, share_item)
            
            # TODO: display amount vested per equity
            # TODO: display total portfolio return and volatility
            # TODO: display actual investment
            self.table_widget.show_table()
            self.arg_widget.fire()
        
        else:
            print('something went wrong')

    @QtCore.Slot()
    def clear(self):
        self.table_widget.table.clear()
        self.table_widget.table.hide()
        self.arg_widget.prime()

class EfficientFrontierWidget(QtWidgets.QWidget):
    def __init__(self, layer):
        super().__init__()
        self.setObjectName(layer)
        self._init_widgets()
        self._arrange_widgets()

    @staticmethod
    def _configure_control_skeleton():
        controls = factories.generate_control_skeleton()

        for arg in definitions.FUNC_DICT['efficient_frontier']['args']:
            if not definitions.ARG_DICT[arg]['cli_only']:
                controls[arg] = True

        return controls

    def _init_widgets(self):
        self.graph_widget = components.GraphWidget(tmp_graph_key=keys.keys['GUI']['TEMP']['FRONTIER'],
                                                    layer=utilities.get_next_layer(self.objectName()))
        self.arg_widget = components.ArgumentWidget(calculate_function=self.calculate, 
                                                    clear_function=self.clear,
                                                    controls=EfficientFrontierWidget._configure_control_skeleton(),
                                                    layer=utilities.get_next_layer(self.objectName()))
        self.setLayout(QtWidgets.QHBoxLayout())
        # TODO: portfolio tabs

    def _arrange_widgets(self):
        self.layout().addWidget(self.graph_widget)
        self.layout().addWidget(self.arg_widget)

    def _stage_widgets(self):
        self.arg_widget.prime()

    def resizeEvent(self, event: QtGui.QResizeEvent) -> None:
        if self.graph_widget.figure.isVisible():
            self.graph_widget.set_pixmap()
        return super().resizeEvent(event)

    @QtCore.Slot()
    def calculate(self):
        if self.graph_widget.figure.isVisible():
            self.graph_widget.figure.hide()

        this_portfolio = Portfolio(tickers=self.arg_widget.get_symbol_input())
        frontier = optimizer.calculate_efficient_frontier(portfolio=this_portfolio)
        plotter.plot_frontier(portfolio=this_portfolio, 
                                frontier=frontier, 
                                show=False, 
                                savefile=f'{settings.TEMP_DIR}/{keys.keys["GUI"]["TEMP"]["FRONTIER"]}')

        self.graph_widget.set_pixmap()
        self.arg_widget.fire()
    
    @QtCore.Slot()
    def clear(self):
        self.graph_widget.figure.hide()
        self.arg_widget.prime()

class MovingAverageWidget(QtWidgets.QWidget):
    def __init__(self, layer):
        super().__init__()
        self.setObjectName(layer)
        self._init_widgets()
        self._arrange_widgets()
        self._stage_widgets()

    def _init_widgets(self):
        self.graph_widget = components.GraphWidget(keys.keys['GUI']['TEMP']['AVERAGES'],
                                                    layer=utilities.get_next_layer(self.objectName()))
        self.arg_widget = components.ArgumentWidget(calculate_function=self.calculate,
                                                    clear_function=self.clear,
                                                    controls = factories.generate_control_skeleton(),
                                                    layer=utilities.get_next_layer(self.objectName()))
        self.setLayout(QtWidgets.QHBoxLayout())

    def _arrange_widgets(self):
        self.layout().addWidget(self.graph_widget)
        self.layout().addWidget(self.arg_widget)
    
    def _stage_widgets(self):
        self.arg_widget.prime()
        
    def resizeEvent(self, event: QtGui.QResizeEvent) -> None:
        if self.graph_widget.figure.isVisible():
            self.graph_widget.set_pixmap()
        return super().resizeEvent(event)

    @QtCore.Slot()
    def calculate(self):
        if self.graph_widget.figure.isVisible():
            self.graph_widget.figure.hide()

        symbols = self.arg_widget.get_symbol_input()

        moving_averages = statistics.calculate_moving_averages(symbols)
        periods = [settings.MA_1_PERIOD, settings.MA_2_PERIOD, settings.MA_3_PERIOD]
        plotter.plot_moving_averages(symbols=symbols, 
                                        averages_output=moving_averages, 
                                        periods=periods, 
                                        show=False, 
                                        savefile=f'{settings.TEMP_DIR}/{keys.keys["GUI"]["TEMP"]["AVERAGES"]}')
        self.graph_widget.set_pixmap()
        self.arg_widget.fire()
    
    @QtCore.Slot()
    def clear(self):
        self.arg_widget.prime()
        self.graph_widget.figure.hide()