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

from typing import Union
from PySide6 import QtGui, QtCore, QtWidgets


from scrilla import settings, services
from scrilla.static import keys, definitions
# TODO: conditional import based on ANALYSIS_MODE
from scrilla.analysis import markets, optimizer
from scrilla.analysis.models.geometric import statistics
from scrilla.analysis.objects.portfolio import Portfolio
from scrilla.analysis.objects.cashflow import Cashflow

from scrilla.util import dater, outputter, helper, plotter

from scrilla.gui import formats, utilities
from scrilla.gui.widgets import factories, components

logger = outputter.Logger('gui.functions', settings.LOG_LEVEL)

class SkeletonWidget(QtWidgets.QWidget):
    def __init__(self, function: str, parent: QtWidgets.QWidget):
        super(SkeletonWidget, self).__init__(parent)
        self._configure_control_skeleton(function)
    
    def _configure_control_skeleton(self, function: str):
        self.controls = factories.generate_control_skeleton()

        for arg in definitions.FUNC_DICT[function]['args']:
            if not definitions.ARG_DICT[arg]['cli_only']:
                self.controls[arg] = True

class YieldCurveWidget(SkeletonWidget):
    def __init__(self, layer: str, parent: Union[QtWidgets.QWidget, None] = None):
        super().__init__(function='yield_curve', parent=parent)
        self.setObjectName(layer)
        self._init_widgets()
        self._arrange_widgets()
        self._stage_widgets()

    def _init_widgets(self):
        self.graph_widget = components.GraphWidget(tmp_graph_key=keys.keys['GUI']['TEMP']['YIELD'],
                                                    layer=utilities.get_next_layer(self.objectName()))
        self.arg_widget = components.ArgumentWidget(calculate_function=self.calculate,
                                                    clear_function=self.clear, 
                                                    controls=self.controls,
                                                    layer=utilities.get_next_layer(self.objectName()))
        # TODO: initialize arg widget WITHOUT tickers

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

        yield_curve = {}
        start_string = dater.date_to_string(self.arg_widget.get_control_input('start_date'))
        yield_curve[start_string] = []
        for maturity in keys.keys['YIELD_CURVE']:
            rate = services.get_daily_interest_history(maturity=maturity, 
                                                            start_date=self.arg_widget.get_control_input('start_date'),
                                                            end_date=self.arg_widget.get_control_input('start_date'))
            yield_curve[start_string].append(rate[start_string])
        
        plotter.plot_yield_curve(yield_curve=yield_curve, 
                                        show=False,
                                        savefile=f'{settings.TEMP_DIR}/{keys.keys["GUI"]["TEMP"]["YIELD"]}')
        self.graph_widget.set_pixmap()
        self.arg_widget.fire()

    @QtCore.Slot()
    def clear(self):
        self.graph_widget.figure.hide()
        self.arg_widget.prime()

class DiscountDividendWidget(SkeletonWidget):
    def __init__(self, layer: str, parent: Union[QtWidgets.QWidget, None] = None):
        super().__init__(function='discount_dividend', parent=parent)
        self.setObjectName(layer)
        self._init_widgets()
        self._arrange_widgets()
        self._stage_widgets()

    def _init_widgets(self):
        self.graph_widget = components.GraphWidget(tmp_graph_key=keys.keys['GUI']['TEMP']['DIVIDEND'],
                                                    layer=utilities.get_next_layer(self.objectName()))
        self.arg_widget = components.ArgumentWidget(calculate_function=self.calculate,
                                                    clear_function=self.clear, 
                                                    controls=self.controls,
                                                    layer=utilities.get_next_layer(self.objectName()))
        # TODO: restrict arg symbol input to one symbol somehow
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

        symbol = self.arg_widget.get_symbol_input()[0]
        discount = self.arg_widget.get_control_input('discount')

        print(discount)
        if discount is None:
            discount = markets.cost_of_equity(ticker=symbol, 
                                                start_date=self.arg_widget.get_control_input('start_date'),
                                                end_date=self.arg_widget.get_control_input('end_date'))
        dividends = services.get_dividend_history(ticker=symbol)
        cashflow = Cashflow(sample=dividends, discount_rate=discount)

        plotter.plot_cashflow(ticker=symbol, 
                                cashflow=cashflow, 
                                show=False,
                                savefile=f'{settings.TEMP_DIR}/{keys.keys["GUI"]["TEMP"]["DIVIDEND"]}')

        self.graph_widget.set_pixmap()
        self.arg_widget.fire()

    @QtCore.Slot()
    def clear(self):
        self.graph_widget.figure.hide()
        self.arg_widget.prime()

class RiskProfileWidget(SkeletonWidget):
    def __init__(self, layer: str, parent:Union[QtWidgets.QWidget,None] = None):
        super().__init__(function='risk_profile', parent=parent)
        self.setObjectName(layer)
        self._init_widgets()
        self._arrange_widgets()
        self._stage_widgets()

    def _init_widgets(self):
        self.composite_widget = components.CompositeWidget(keys.keys['GUI']['TEMP']['PROFILE'], 
                                                            widget_title="Risk Analysis",
                                                            table_title="CAPM Risk Profile",
                                                            graph_title="Risk-Return Plane",
                                                            layer = utilities.get_next_layer(self.objectName()))
        self.arg_widget = components.ArgumentWidget(calculate_function=self.calculate,
                                                    clear_function=self.clear,
                                                    controls= self.controls,
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
            profiles[symbol] = statistics.calculate_risk_return(ticker=symbol,
                                                                start_date=self.arg_widget.get_control_input('start_date'),
                                                                end_date=self.arg_widget.get_control_input('end_date'))
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

class CorrelationWidget(SkeletonWidget):
    def __init__(self, layer: str, parent: Union[QtWidgets.QWidget, None]=None):
        super().__init__(function='correlation', parent=parent)
        self.setObjectName(layer)
        self._init_widgets()
        self._arrange_widgets()
        self._stage_widgets()

    def _init_widgets(self):
        self.table_widget = components.TableWidget(widget_title="Correlation Matrix",
                                                    layer=utilities.get_next_layer(self.objectName()))
        self.arg_widget = components.ArgumentWidget(calculate_function=self.calculate,
                                                    clear_function=self.clear,
                                                    controls=self.controls,
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

            matrix = statistics.correlation_matrix(tickers=symbols, 
                                                    start_date=self.arg_widget.get_control_input('start_date'),
                                                    end_date=self.arg_widget.get_control_input('end_date'))
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

class OptimizerWidget(SkeletonWidget):
    def __init__(self, layer: str, parent: Union[QtWidgets.QWidget, None]=None):
        super().__init__(function='optimize_portfolio', parent=parent)
        self.setObjectName(layer)
        self._init_widgets()
        self._arrange_widgets()
        self._stage_widgets()

    def _init_widgets(self):
        self.title = factories.atomic_widget_factory(format='heading', title=None)
        self.table_widget = components.TableWidget(widget_title="Optimization Results",
                                                    layer=utilities.get_next_layer(self.objectName()))
        self.arg_widget = components.ArgumentWidget(calculate_function=self.optimize,
                                                    clear_function=self.clear,
                                                    controls=self.controls,
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

class EfficientFrontierWidget(SkeletonWidget):
    def __init__(self, layer: str, parent: Union[QtWidgets.QWidget, None]=None):
        super().__init__(function='efficient_frontier', parent=parent)
        self.setObjectName(layer)
        self._init_widgets()
        self._arrange_widgets()

    def _init_widgets(self):
        self.graph_widget = components.GraphWidget(tmp_graph_key=keys.keys['GUI']['TEMP']['FRONTIER'],
                                                    layer=utilities.get_next_layer(self.objectName()))
        self.arg_widget = components.ArgumentWidget(calculate_function=self.calculate, 
                                                    clear_function=self.clear,
                                                    controls=self.controls,
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

        this_portfolio = Portfolio(tickers=self.arg_widget.get_symbol_input(),
                                    start_date=self.arg_widget.get_control_input('start_date'),
                                    end_date=self.arg_widget.get_control_input('end_date'))
        frontier = optimizer.calculate_efficient_frontier(portfolio=this_portfolio,
                                                            steps=self.arg_widget.get_control_input('steps'))
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

class MovingAverageWidget(SkeletonWidget):
    def __init__(self, layer: str, parent: Union[QtWidgets.QWidget, None]=None):
        super().__init__(function='moving_averages', parent=parent)
        self.setObjectName(layer)
        self._init_widgets()
        self._arrange_widgets()
        self._stage_widgets()

    def _init_widgets(self):
        self.graph_widget = components.GraphWidget(keys.keys['GUI']['TEMP']['AVERAGES'],
                                                    layer=utilities.get_next_layer(self.objectName()))
        self.arg_widget = components.ArgumentWidget(calculate_function=self.calculate,
                                                    clear_function=self.clear,
                                                    controls = self.controls,
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

        moving_averages = statistics.calculate_moving_averages(tickers=self.arg_widget.get_symbol_input(),
                                                                start_date=self.arg_widget.get_control_input('start_date'),
                                                                end_date=self.arg_widget.get_control_input('end_date'))
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