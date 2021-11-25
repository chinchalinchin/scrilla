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

from datetime import date
from math import trunc, sqrt
from decimal import Decimal
from itertools import groupby
from typing import Callable, Dict, List, Union

# TODO: get rid of numpy functions.
#       dot, multiply and transpose should be easy to replicate
#       and it removes a big dependency from the package...
from numpy import dot, multiply, transpose

from scrilla import settings, errors
from scrilla.static import keys
from scrilla.util import outputter
# TODO: conditional import module based on analysis_mode, i.e. geometric versus mean reverting.
from scrilla.analysis.models.geometric.statistics import calculate_risk_return, correlation_matrix
from scrilla.analysis.models.geometric.probability import percentile, conditional_expected_value

logger = outputter.Logger(
    "scrilla.analysis.objects.portfolio", settings.LOG_LEVEL)

# TODO: allow user to specify bounds for equities, i.e. min and max allocations.


class Portfolio:
    r"""
    A class that represents a portfolio of assets defined by the supplied list of ticker symbols in the `tickers` array.

    The portfolio can be initialized with historical prices using the `start_date` and `end_date` parameters or the `sample_prices` parameter. If `start_date` and `end_date` are provided, the class will pass the dates to the PriceManager to query an external service for the required prices. If `sample_prices` is provided, the `start_date` and `end_date` are ignored and the `sample_prices` are used in lieu of an external query.

    The `return_function` and `volatility_function` methods accept an allocation of percentage weights corresponding to each ticker in the `tickers` array and return the overall portfolio return and volatility. The return is the dot product of the weight and the individual asset returns. The `volatility_function` is the result of applying matrix multiplication to the transposed weight allocations, the correlation matrix and the untransposed weight allocations. These formulations are consistent with Modern Portfolio Theory.

    Parameters
    ----------
    1. **tickers**: ``List[str]``
        An array of ticker symbols that decribe the assets in a portfolio.
    2. **start_date**: ``Union[date, None]``
        *Optional*. The start date for the range of historical prices over which the portfolio will be optimized. 
    3. **end_date**: ``Union[date, None]``
        *Optional*. The end date for the range of historical prices over which the portfolio will be optimized.
    4. **sample_prices**: ``Union[Dict[str, Dict[str, float]], None]``
        *Optional*. A list representing a sample of historical data over a time range. The list must be ordered in descending order, i.e. from latest to earliest. Must be formatted as: `{ 'ticker_1': { 'date' : { 'open': value, 'close': value},... }}
    5. **risk_profile** : ``Union[Dict[str, Dict[str, float]], None]``
        Optional: Rather than use sample statistics calculated from historical data, this argument can override the calculated values. Must be formatted as: `{ ticker: { 'annual_return': float, 'annual_volatility': float }}`
    6. **correlation_matrix**: ``Union[List[List[float]], None]``
        Optional: Rather than use correlations calculated from historical data, this argument can override the calculated vlaues.
    7. **asset_return_functions**: ``Union[List[Callable], None]``
        *Optional*. An array of function that describes the expected logarithmic rate of return of each asset in the portfolio with respect to time. The order between `asset_return_functions` and `tickers` be must be preserved, i.e. the index of tickers must correspond to the symbol described by the function with same index in `asset_return_functions`.
    8. **asset_volatility_funtions**: ``Union[List[Callable], None]``
        *Optional*. An array of functions that describe the mean volatility of each asset in the portfolio with respect to time. The order between `asset_volatility_functions` and `tickers` be must be preserved, i.e. the index of tickers must correspond to the symbol described by the function with the same index in `asset_volatility_functions`.

    Attributes
    ----------
    All parameters are exposed as properties on the class. With the exception of `asset_return_functions` and `asset_volatility_functions`, if optional parameters are not provided in the class constructor, they will be calculated based on available information. See *notes* for more details on how this class is constructed.

    .. notes::
    * While `start_date`, `end_date`, `sample_prices` are all by themselves optional, the `scrilla.analysis.objects.Portfolio` class must be initialized in one of three ways: 
        1. *Portfolio*(`start_date`, `end_date`) -> `start_date` and `end_date` are passed to service for external query request.
        2. *Portfolio*(`sample_prices`) -> `start_date` and `end_date` are ignored and `sample_prices` are used for statistical calculations.
        3. *Portfolio*(`risk_profile`) -> `start_date`, `end_date` and `sample_prices` are ignored and the statistics in `risk_profile` are used istead of manual calculations.
    *The priority hierarchy is as follows : `risk_profile` > `sample_prices` > (`start_date`, `end_date`).  If no arguments are provided to the constructor at all, the portfolio will default to the `scrilla.settings.DEFAULT_ANALYSIS_PERIOD` variable configured by the corresponding environment variable. If the environment variable is not set, this value will default to the last 100 trading days.
    * The `asset_return_functions` and `asset_volatility_functions` can be understood as the drift and noise functions for a random stochastic process,

    $$ \frac{dX(t)}{X(t)} = \mu(t) \cdot dt + \sigma(t) \cdot dB(t) $$

    where B(t) ~ \\(N(0, \Delta \cdot t)\\).
    """

    def __init__(self, tickers: List[str], start_date=Union[date, None], end_date=Union[date, None], sample_prices: Union[Dict[str, Dict[str, float]], None] = None, correl_matrix: Union[List[List[int]], None] = None, risk_profiles: Union[Dict[str, Dict[str, float]]] = None, risk_free_rate: Union[float, None] = None, asset_return_functions: Union[List[Callable], None] = None, asset_volatility_functions: Union[List[Callable], None] = None, method: str = settings.ESTIMATION_METHOD):
        self.estimation_method = method
        self.sample_prices = sample_prices
        self.tickers = tickers
        self.correl_matrix = correl_matrix
        self.asset_volatility_functions = asset_volatility_functions
        self.asset_return_functions = asset_return_functions
        self.risk_profiles = risk_profiles
        self.target_return = None

        if self.sample_prices is None:
            self.start_date = start_date
            self.end_date = end_date
        else:
            self.start_date = list(self.sample_prices.keys())[-1]
            self.end_date = list(self.sample_prices.keys())[0]

        if risk_free_rate is not None:
            self.risk_free_rate = risk_free_rate
        else:
            self.risk_free_rate = 0

        self._init_asset_types()
        self._init_dates()
        self._init_stats()

    def _init_asset_types(self):
        self.asset_types = []
        for ticker in self.tickers:
            self.asset_types.append(errors.validate_asset_type(ticker))

        self.mixed_assets = False
        self.asset_groups = 0
        for _ in groupby(sorted(self.asset_types)):
            self.asset_groups += 1

    def _init_dates(self):
        if self.asset_groups == 1 and self.asset_types[0] == keys.keys['ASSETS']['CRYPTO']:
            self.start_date, self.end_date = errors.validate_dates(self.start_date,
                                                                   self.end_date,
                                                                   keys.keys['ASSETS']['CRYPTO'])
            self.weekends = 1
        else:
            self.start_date, self.end_date = errors.validate_dates(self.start_date,
                                                                   self.end_date,
                                                                   keys.keys['ASSETS']['EQUITY'])
            self.weekends = 0

    def _init_stats(self):
        self.mean_return = []
        self.sample_vol = []

        # priority hierarchy: asset_functions -> risk_profiles -> sample_prices -> statistics.py calls
        if self.asset_volatility_functions is not None and self.asset_return_functions is not None:
            # TODO: implement ito integration and calculate asset return and volatilities!
            # use return and volatility functions to integrate over time period [0, infinity] for each asset. don't forget to
            #   discount! I(x) = discounted expected payoff
            #   Integral(d ln S) = Integral(Mean dt) + Integral(Vol dZ)
            #   Need methods to compute ito Integrals in...statistics.py? markets.py? Perhaps a new module.
            # https://math.stackexchange.com/questions/1780956/mean-and-variance-geometric-brownian-motion-with-not-constant-drift-and-volatili
            pass

        else:

            # TODO: there is a logical error here. if the portfolio is made up of mixed assets (crypto, equity),
            #       then calculate_risk_return will calculate the risk profile over a different time period than
            #       the correlation matrix. the reason is: risk_return is univariate, but correlation is bivariate,
            #       so when the correlation of an equity and crypto is calculated, it truncates the sample to dates
            #       where both assets trade, i.e. crypto prices on weekends get ignored. the risk_profile of the crypto
            #       will be over a shorter date range because the analysis will include weekends, whereas the crypto
            #       correlation will not include weekends if the asset types are mixed. the problem is further
            #       compounded since the correlation method will retrieve the univariate profile to use in its calculation.
            #       need a flag in the cache to tell the program the statistic includes/exclude weekend prices.

            if self.risk_profiles is None:
                for ticker in self.tickers:
                    if self.sample_prices is not None:
                        stats = calculate_risk_return(ticker=ticker,
                                                      sample_prices=self.sample_prices[ticker],
                                                      method=self.estimation_method,
                                                      weekends=self.weekends)
                    else:
                        stats = calculate_risk_return(ticker=ticker,
                                                      start_date=self.start_date,
                                                      end_date=self.end_date,
                                                      method=self.estimation_method,
                                                      weekends=self.weekends)

                    self.mean_return.append(stats['annual_return'])
                    self.sample_vol.append(stats['annual_volatility'])
            else:
                for ticker in self.risk_profiles:
                    self.mean_return.append(
                        self.risk_profiles[ticker]['annual_return'])
                    self.sample_vol.append(
                        self.risk_profiles[ticker]['annual_volatility'])

            if self.correl_matrix is None:
                self.correl_matrix = correlation_matrix(tickers=self.tickers,
                                                        start_date=self.start_date,
                                                        end_date=self.end_date,
                                                        sample_prices=self.sample_prices,
                                                        weekends=self.weekends,
                                                        method=self.estimation_method)

    def return_function(self, x):
        """
        Returns the portfolio return for a vector of allocations. It can be used as objective function input for `scipy.optimize`'s optimization methods. 

        Parameters
        ----------
        1. **x**: ``list``
            Vector representing the allocation of each asset in the portfolio. Must be preserve the order of `portfolio.tickers`, i.e. each element's index should map to each element of the `portfolio.tickers`'s list.

        Returns
        -------
        ``float``
            The portfolio return on an annualized basis.
        """
        return dot(x, self.mean_return)

    def volatility_function(self, x):
        """
        Returns the portfolio volatility for a vector of allocations. This function can be used as objective input function for `scipy.optimize`'s optimization or solver methods.\n\n

        Parameters
        ----------
        1. **x**: ``list``
            Vector representing the allocation of each asset in the portfolio. Must be preserve the order of `portfolio.tickers`, i.e. each element's index should map to each element of the `portfolio.tickers`'s list.

        Returns
        -------
        ``float``
            The portfolio volatility on an annualized basis.
        """
        return sqrt(multiply(x, self.sample_vol).dot(self.correl_matrix).dot(transpose(multiply(x, self.sample_vol))))

    def sharpe_ratio_function(self, x):
        """
        Returns the portfolio sharpe ratio for a vector of allocations. This function can be used as objective input function for `scipy.optimize`'s optimization or solver methods.\n\n

        Parameters
        ----------
        1. **x**: ``list``
            Vector representing the allocation of each asset in the portfolio. Must be preserve the order of `portfolio.tickers`, i.e. each element's index should map to each element of the `portfolio.tickers`'s list.

        Returns
        -------
        ``float``
            The portfolio sharpe ratio on an annualized basis.
        """
        return (dot(x, self.mean_return) - self.risk_free_rate) / (self.volatility_function(x))

    def percentile_function(self, x, time, prob):
        """
        Returns the given percentile of the portfolio's assumed distribution.\n\n

        Parameters
        ----------
        1. **x**: ``list``
            Vector representing the allocation of each asset in the portfolio. Must be preserve the order of `self.tickers`, i.e. each element's index should map to each element of the `self.tickers`'s list.
        2: **time**: ``float``
            time horizon (in years) of the value at risk, i.e. the period of time into the future at which the value at risk is being calculated 
        3. **prob**: ``float``
            percentile desired
        """
        portfolio_return = self.return_function(x) * time
        portfolio_volatility = self.volatility_function(x) * sqrt(time)

        return percentile(S0=1, vol=portfolio_volatility, ret=portfolio_return,
                          expiry=time, prob=prob)

    def conditional_value_at_risk_function(self, x, time, prob):
        """
        Calculates the conditional value at risk for a portfolio of stocks over a specified time horizon. The value will be given in percentage terms relative to the initial value of the portfolio at the beginning of the time horizon, i.e. a return value of 5% would mean 5% of your portfolio's initial value is at risk with probability `prob`. A negative value would indicate there is no value at risk, i.e. value would actually accrue. This function can be used as objective input function for `scipy.optimize`'s optimization or solver methods.

        Parameters
        ----------
        1. **x**: ``list``
            an array of decimals representing percentage allocations of the portfolio. Must preserve order with `self.tickers`.
        2. **time**: ``float``
            time horizon (in years) of the value at risk, i.e. the period of time into the future at which the value at risk is being calculated.
        3. **prob**: ``float``
            desired probability of loss.
        """
        portfolio_return = self.return_function(x) * time
        portfolio_volatility = self.volatility_function(x) * sqrt(time)
        value_at_risk = self.percentile_function(x=x, time=time, prob=prob)
        return (1 - conditional_expected_value(S0=1, vol=portfolio_volatility, ret=portfolio_return,
                                               expiry=time, conditional_value=value_at_risk))

    def get_init_guess(self):
        length = len(self.tickers)
        uniform_guess = 1/length
        guess = [uniform_guess for i in range(length)]
        return guess

    @staticmethod
    def get_constraint(x):
        return sum(x) - 1

    def get_default_bounds(self):
        return [[0, 1] for y in range(len(self.tickers))]

    def set_target_return(self, target):
        self.target_return = target

    def get_target_return_constraint(self, x):
        if self.target_return is not None:
            return (dot(x, self.mean_return) - self.target_return)
        return None

    @staticmethod
    def calculate_approximate_shares(x, total, latest_prices):
        shares = []
        for i, item in enumerate(x):
            price = latest_prices[i]
            share = Decimal(item) * Decimal(total) / Decimal(price)
            shares.append(trunc(share))

        return shares

    @staticmethod
    def calculate_actual_total(x, total, latest_prices):
        actual_total = 0
        shares = Portfolio.calculate_approximate_shares(
            x=x, total=total, latest_prices=latest_prices)
        for i, item in enumerate(shares):
            price = latest_prices[i]
            portion = Decimal(item) * Decimal(price)
            actual_total = actual_total + portion
        return actual_total
