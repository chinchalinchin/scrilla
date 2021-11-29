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
from scrilla.analysis import estimators, markets, optimizer, plotter
from scrilla.analysis.models.geometric import statistics
from scrilla.analysis.objects.portfolio import Portfolio
from scrilla.analysis.objects.cashflow import Cashflow

from scrilla.util import dater, outputter, helper

from scrilla.gui import formats, utilities
from scrilla.gui.widgets import factories, components

logger = outputter.Logger('gui.functions', settings.LOG_LEVEL)


class DistributionWidget(components.SkeletonWidget):
    def __init__(self, layer: str, parent: Union[QtWidgets.QWidget, None] = None):
        super().__init__(function='plot_return_dist', parent=parent)
        self.setObjectName(layer)
        self._init_widgets()
        self._arrange_widgets()
        self._stage_widgets()

    def _init_widgets(self):
        self.arg_widget = components.ArgumentWidget(calculate_function=self.calculate,
                                                    clear_function=self.clear,
                                                    controls=self.controls,
                                                    layer=utilities.get_next_layer(self.objectName()))
        self.title = factories.atomic_widget_factory(
            component='heading', title='Distribution of Returns')
        self.tab_container = factories.layout_factory(layout='vertical-box')
        self.tab_widget = QtWidgets.QTabWidget()
        self.setLayout(QtWidgets.QHBoxLayout())

    def _arrange_widgets(self):
        self.tab_container.layout().addWidget(self.tab_widget)
        self.layout().addWidget(self.tab_container)
        self.layout().addWidget(self.arg_widget)

    def _stage_widgets(self):
        self.arg_widget.prime()

    def resizeEvent(self, event: QtGui.QResizeEvent) -> None:
        for i in range(self.tab_widget.count()):
            if self.tab_widget.widget(i).figure.isVisible():
                self.tab_widget.widget(i).set_pixmap()
        return super().resizeEvent(event)

    @QtCore.Slot()
    def calculate(self):
        symbols = self.arg_widget.get_symbol_input()
        start_date = self.arg_widget.get_control_input('start_date')
        end_date = self.arg_widget.get_control_input('end_date')

        for symbol in symbols:
            qq_plot = components.GraphWidget(tmp_graph_key=f'{keys.keys["GUI"]["TEMP"]["QQ"]}_{symbol}',
                                             layer=utilities.get_next_layer(self.objectName()))
            dist_plot = components.GraphWidget(tmp_graph_key=f'{keys.keys["GUI"]["TEMP"]["DIST"]}_{symbol}',
                                               layer=utilities.get_next_layer(self.objectName()))
            returns = statistics.get_sample_of_returns(ticker=symbol,
                                                       start_date=start_date,
                                                       end_date=end_date,
                                                       daily=True)
            qq_series = estimators.qq_series_for_sample(sample=returns)
            plotter.plot_qq_series(ticker=symbol,
                                   qq_series=qq_series,
                                   show=False,
                                   savefile=f'{settings.TEMP_DIR}/{keys.keys["GUI"]["TEMP"]["QQ"]}_{symbol}')
            plotter.plot_return_histogram(ticker=symbol,
                                          sample=returns,
                                          show=False,
                                          savefile=f'{settings.TEMP_DIR}/{keys.keys["GUI"]["TEMP"]["DIST"]}_{symbol}',)
            dist_plot.set_pixmap()
            qq_plot.set_pixmap()
            self.tab_widget.addTab(qq_plot, f'{symbol} QQ Plot')
            self.tab_widget.addTab(dist_plot, f'{symbol} Distribution')
        self.tab_widget.show()
        self.arg_widget.fire()

    @QtCore.Slot()
    def clear(self):
        self.arg_widget.prime()
        total = self.tab_widget.count()
        for _ in range(total):
            self.tab_widget.removeTab(0)


class YieldCurveWidget(components.SkeletonWidget):
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
                                                    layer=utilities.get_next_layer(
                                                        self.objectName()),
                                                    mode=components.SYMBOLS_NONE)
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
        start_date = dater.this_date_or_last_trading_date(
            self.arg_widget.get_control_input('start_date'))
        start_string = dater.to_string(start_date)
        yield_curve[start_string] = []
        for maturity in keys.keys['YIELD_CURVE']:
            rate = services.get_daily_interest_history(maturity=maturity,
                                                       start_date=start_date,
                                                       end_date=start_date)
            yield_curve[start_string].append(rate[start_string])

        plotter.plot_yield_curve(yield_curve=yield_curve,
                                 show=False,
                                 savefile=f'{settings.TEMP_DIR}/{keys.keys["GUI"]["TEMP"]["YIELD"]}')
        self.graph_widget.set_pixmap()
        self.arg_widget.fire()

    @QtCore.Slot()
    def clear(self):
        self.graph_widget.clear()
        self.arg_widget.prime()


class DiscountDividendWidget(components.SkeletonWidget):
    def __init__(self, layer: str, parent: Union[QtWidgets.QWidget, None] = None):
        super().__init__(function='discount_dividend', parent=parent)
        self.setObjectName(layer)
        self._init_widgets()
        self._arrange_widgets()
        self._stage_widgets()

    def _init_widgets(self):
        self.tab_container = factories.layout_factory(layout='vertical-box')
        self.tab_widget = QtWidgets.QTabWidget()
        self.arg_widget = components.ArgumentWidget(calculate_function=self.calculate,
                                                    clear_function=self.clear,
                                                    controls=self.controls,
                                                    layer=utilities.get_next_layer(self.objectName()))
        # TODO: restrict arg symbol input to one symbol somehow
        self.setLayout(QtWidgets.QHBoxLayout())

    def _arrange_widgets(self):
        self.tab_container.layout().addWidget(self.tab_widget)
        self.layout().addWidget(self.tab_container)
        self.layout().addWidget(self.arg_widget)

    def _stage_widgets(self):
        self.arg_widget.prime()

    def resizeEvent(self, event: QtGui.QResizeEvent) -> None:
        for i in range(self.tab_widget.count()):
            if self.tab_widget.widget(i).figure.isVisible():
                self.tab_widget.widget(i).set_pixmap()
        return super().resizeEvent(event)

    @QtCore.Slot()
    def calculate(self):
        symbols = self.arg_widget.get_symbol_input()
        discount = self.arg_widget.get_control_input('discount')

        for symbol in symbols:
            if discount is None:
                discount = markets.cost_of_equity(ticker=symbol,
                                                  start_date=self.arg_widget.get_control_input(
                                                      'start_date'),
                                                  end_date=self.arg_widget.get_control_input('end_date'))
            dividends = services.get_dividend_history(ticker=symbol)
            cashflow = Cashflow(sample=dividends, discount_rate=discount)
            graph_widget = components.GraphWidget(tmp_graph_key=f'{keys.keys["GUI"]["TEMP"]["DIVIDEND"]}_{symbol}',
                                                  layer=utilities.get_next_layer(self.objectName()))
            plotter.plot_cashflow(ticker=symbol,
                                  cashflow=cashflow,
                                  show=False,
                                  savefile=f'{settings.TEMP_DIR}/{keys.keys["GUI"]["TEMP"]["DIVIDEND"]}_{symbol}')

            graph_widget.set_pixmap()
            self.tab_widget.addTab(graph_widget, f'{symbol} DDM PLOT')
        self.tab_widget.show()
        self.arg_widget.fire()

    @QtCore.Slot()
    def clear(self):
        self.arg_widget.prime()
        total = self.tab_widget.count()
        for _ in range(total):
            self.tab_widget.removeTab(0)


class RiskProfileWidget(components.SkeletonWidget):
    def __init__(self, layer: str, parent: Union[QtWidgets.QWidget, None] = None):
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
                                                           layer=utilities.get_next_layer(self.objectName()))
        self.arg_widget = components.ArgumentWidget(calculate_function=self.calculate,
                                                    clear_function=self.clear,
                                                    controls=self.controls,
                                                    layer=utilities.get_next_layer(self.objectName()))
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
                                                      columns=['Return', 'Volatility', 'Sharpe', 'Beta', 'Equity Cost'])

        profiles = {}
        for i, symbol in enumerate(symbols):
            profiles[symbol] = statistics.calculate_risk_return(ticker=symbol,
                                                                start_date=self.arg_widget.get_control_input(
                                                                    'start_date'),
                                                                end_date=self.arg_widget.get_control_input('end_date'))
            profiles[symbol][keys.keys['APP']['PROFILE']
                             ['SHARPE']] = markets.sharpe_ratio(symbol)
            profiles[symbol][keys.keys['APP']['PROFILE']
                             ['BETA']] = markets.market_beta(symbol)
            profiles[symbol][keys.keys['APP']['PROFILE']
                             ['EQUITY']] = markets.cost_of_equity(symbol)

            formatted_profile = formats.format_profile(profiles[symbol])

            for j, statistic in enumerate(formatted_profile.keys()):
                table_item = factories.atomic_widget_factory(
                    component='table-item', title=formatted_profile[statistic])
                self.composite_widget.table_widget.table.setItem(
                    i, j, table_item)

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
        self.composite_widget.graph_widget.clear()
        self.composite_widget.table_widget.table.clear()
        self.composite_widget.table_widget.table.hide()
        self.arg_widget.prime()


class CorrelationWidget(components.SkeletonWidget):
    def __init__(self, layer: str, parent: Union[QtWidgets.QWidget, None] = None):
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
                                                   start_date=self.arg_widget.get_control_input(
                                                       'start_date'),
                                                   end_date=self.arg_widget.get_control_input('end_date'))
            for i in range(0, len(symbols)):
                for j in range(i, len(symbols)):
                    item_upper = factories.atomic_widget_factory(
                        component='table-item', title=helper.format_float_percent(matrix[i][j]))
                    item_lower = factories.atomic_widget_factory(
                        component='table-item', title=helper.format_float_percent(matrix[j][i]))
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
        self.table_widget.download_button.hide()


class OptimizerWidget(components.SkeletonWidget):
    def __init__(self, layer: str, parent: Union[QtWidgets.QWidget, None] = None):
        super().__init__(function='optimize_portfolio', parent=parent)
        self.setObjectName(layer)
        self._init_widgets()
        self._arrange_widgets()
        self._stage_widgets()

    def _init_widgets(self):
        self.title = factories.atomic_widget_factory(
            component='heading', title=None)
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
                                       start_date=self.arg_widget.get_control_input(
                                           'start_date'),
                                       end_date=self.arg_widget.get_control_input('end_date'))
            allocation = optimizer.optimize_portfolio_variance(portfolio=this_portfolio,
                                                               target_return=self.arg_widget.get_control_input('target'))
            self.title.setText(formats.format_allocation_profile_title(
                allocation, this_portfolio))

            prices = services.get_daily_prices_latest(tickers=symbols)

            if investment is None:
                self.table_widget.init_table(
                    rows=symbols, columns=['Allocation'])
            else:
                self.table_widget.init_table(rows=symbols, columns=[
                                             'Allocation', 'Shares'])
                shares = this_portfolio.calculate_approximate_shares(
                    allocation, float(investment), prices)

            for i in range(len(symbols)):
                item = factories.atomic_widget_factory(
                    component='table-item', title=helper.format_float_percent(allocation[i]))
                self.table_widget.table.setItem(i, 0, item)

                if investment is not None:
                    share_item = factories.atomic_widget_factory(
                        component='table-item', title=str(shares[i]))
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


class EfficientFrontierWidget(components.SkeletonWidget):
    def __init__(self, layer: str, parent: Union[QtWidgets.QWidget, None] = None):
        super().__init__(function='efficient_frontier', parent=parent)
        self.setObjectName(layer)
        self._init_widgets()
        self._arrange_widgets()
        self._stage_widgets()

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
                                   start_date=self.arg_widget.get_control_input(
                                       'start_date'),
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


class MovingAverageWidget(components.SkeletonWidget):
    def __init__(self, layer: str, parent: Union[QtWidgets.QWidget, None] = None):
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
                                                    controls=self.controls,
                                                    layer=utilities.get_next_layer(
                                                        self.objectName()),
                                                    mode=components.SYMBOLS_SINGLE)
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

        moving_averages = statistics.calculate_moving_averages(ticker=self.arg_widget.get_symbol_input()[0],
                                                               start_date=self.arg_widget.get_control_input(
                                                                   'start_date'),
                                                               end_date=self.arg_widget.get_control_input('end_date'))

        plotter.plot_moving_averages(ticker=self.arg_widget.get_symbol_input()[0],
                                     averages=moving_averages,
                                     show=False,
                                     savefile=f'{settings.TEMP_DIR}/{keys.keys["GUI"]["TEMP"]["AVERAGES"]}')
        self.graph_widget.set_pixmap()
        self.arg_widget.fire()

    @QtCore.Slot()
    def clear(self):
        self.arg_widget.prime()
        self.graph_widget.clear()
