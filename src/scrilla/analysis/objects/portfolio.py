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

import numpy, math
from decimal import Decimal

from scrilla import services, settings, files, errors
import scrilla.util.outputter as outputter 

# TODO: conditional import module based on analysis_mode, i.e. geometric versus mean reverting.
import scrilla.analysis.models.geometric.statistics as statistics
import scrilla.analysis.models.geometric.probability as probability

logger = outputter.Logger("analysis.objects.portfolio", settings.LOG_LEVEL)

# TODO: allow user to specify bounds for equities, i.e. min and max allocations.

# TODO: i think the portfolio will need to know the estimation_method. 
class Portfolio:
    """
    A class that represents a portfolio of assets defined by the supplied list of ticker symbols in the `tickers` array. \n \n

    The portfolio can be initialized with historical prices using the 'start_date' and 'end_date' parameters or the `sample_prices` parameter. If `start_date` and `end_date` are provided, the class will pass the dates to the PriceManager to query an external service for the required prices. If `sample_prices` is provided, the `start_date` and `end_date` are ignored and the `sample_prices` are used in lieu of an external query. \n \n

    The `return_function` and `volatility_function` methods accept an allocation of percentage weights corresponding to each ticker in the `tickers` array and return the overall portfolio return and volatility. The return is the dot product of the weight and the individual asset returns. The `volatility_function` is the result of applying matrix multiplication to the transposed weight allocations, the correlation matrix and the untransposed weight allocations. These formulations are consistent with Modern Portfolio Theory.\n \n

    Parameters
    ----------
    1. tickers : [ str ] \n
        Required. An array of ticker symbols that define the assets in a portfolio. \n \n
    2. start_date: datetime.date \n
        Optional. The start date for the range of historical prices over which the portfolio will be optimized. 
    \n \n
    3. end_date: datetime.date \n
        Optional. The end date for the range of historical prices over which the portfolio will be optimized. \n \n
    4. sample_prices: { 'date' : 'price', 'date': 'price' } \n
        Optional. A list representing a sample of historical data over a time range. The list must be ordered in descending order, i.e. from latest to earliest. \n \n 
    5. risk_profile : { ticker: { 'annual_return': float, 'annual_volatility': float }} \n
        Optional: Rather than use sample statistics calculated from historical data, this argument can override the calculated values. \n \n
    6. correlation_matrix : ``[ list ]``\n
        Optional: Rather than use correlations calculated from historical data, this argument can override the calculated vlaues.
    6. asset_return_functions: [ function(t) ] \n
        Optional. An array of function that describes the expected logarithmic rate of return of each asset in the portfolio with respect to time. The order between `asset_return_functions` and `tickers` be must be preserved, i.e. the index of tickers must correspond to the symbol described by the function with same index in `asset_return_functions`. \n \n 
    7. asset_volatility_funtions: [ function(t) ] \n
        Optional. An array of functions that describe the mean volatility of each asset in the portfolio with respect to time. The order between `asset_volatility_functions` and `tickers` be must be preserved, i.e. the index of tickers must correspond to the symbol described by the function with the same index in `asset_volatility_functions`. \n \n 

    Notes
    -----
    NOTE: While `start_date`, `end_date`, `sample_prices` are all by themselves optional, the Portfolio class must be initialized in one of three ways: \n
        1. *Portfolio*(`start_date`, `end_date`) -> `start_date` and `end_date` are passed to service for external query request. \n
        2. *Portfolio*(`sample_prices`) -> `start_date` and `end_date` are ignored and `sample_prices` are used for statistical calculations. \n 
        3. *Portfolio*(`risk_profile`) -> `start_date`, `end_date` and `sample_prices` are ignored and the statistics in `risk_profile` are used instead of manual calculations.

    The priority hierarchy is as follows : `risk_profile` > `sample_prices` > (`start_date`, `end_date`).  If no arguments are provided to the constructor at all, the portfolio will default to the `scrilla.settings.DEFAULT_ANALYSIS_PERIOD` variable configured by the corresponding environment variable. If the environment variable is not set, this value will default to the last 100 trading days.\n \n

    NOTE: The `asset_return_functions` and `asset_volatility_functions` can be understood as the drift and noise functions for a random stochastic process. \n \n
    """
    def __init__(self, tickers, start_date=None, end_date=None, sample_prices=None,
                    correlation_matrix=None, risk_profiles=None, risk_free_rate=None,
                    asset_return_functions=None, asset_volatility_functions=None,
                    method=settings.ESTIMATION_METHOD):
        self.shares = None
        self.actual_total = None
        self.risk_free_rate = None
        self.estimation_method = method

        if sample_prices is None:
            self.start_date = start_date
            self.end_date = end_date
        else:
            self.start_date = list(sample_prices.keys())[-1]
            self.end_date = list(sample_prices.keys())[0]

        self.tickers = tickers
        self.sample_prices = sample_prices
        self.correlation_matrix = correlation_matrix
        self.asset_volatility_functions = asset_volatility_functions
        self.asset_return_functions = asset_return_functions
        self.risk_profiles = risk_profiles

        if risk_free_rate is not None:
            self.risk_free_rate = risk_free_rate
        else:
            self.risk_free_rate = services.get_risk_free_rate()        
        
        self.calculate_stats()


        # todo: calculate stats with lambda functions.
    # Returns False if calculations fail
    def calculate_stats(self):
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

            if self.risk_profiles is None:
                for ticker in self.tickers:
                    if self.sample_prices is not None:
                        stats = statistics.calculate_risk_return(ticker=ticker, 
                                                                    sample_prices=self.sample_prices[ticker],
                                                                    method=self.estimation_method)
                    else: 
                        stats = statistics.calculate_risk_return(ticker=ticker, 
                                                                    start_date=self.start_date, 
                                                                    end_date=self.end_date,
                                                                    method=self.estimation_method)

                    self.mean_return.append(stats['annual_return'])
                    self.sample_vol.append(stats['annual_volatility'])
            else:
                for ticker in self.risk_profiles:
                    self.mean_return.append(self.risk_profiles[ticker]['annual_return'])
                    self.sample_vol.append(self.risk_profiles[ticker]['annual_volatility']) 

            if self.correlation_matrix is None:
                self.correlation_matrix =  statistics.correlation_matrix(tickers=self.tickers,
                                                                            start_date=self.start_date, 
                                                                            end_date=self.end_date,
                                                                            sample_prices=self.sample_prices,
                                                                            method=self.estimation_method)

    def return_function(self, x):
        """
        Returns the portfolio return for a vector of allocations. It can be used as objective function input for `scipy.optimize`'s optimization methods. 

        Parameters
        ----------
        1. x : ``list`` \n
            Vector representing the allocation of each asset in the portfolio. Must be preserve the order of `portfolio.tickers`, i.e. each element's index should map to each element of the `portfolio.tickers`'s list.\n\n

        Returns
        -------
        ``float``\n
            The portfolio return on an annualized basis.
        """
        return numpy.dot(x, self.mean_return)

    def volatility_function(self, x):
        """
        Returns the portfolio volatility for a vector of allocations. This function can be used as objective input function for `scipy.optimize`'s optimization or solver methods.\n\n

        Parameters
        ----------
        1. x : ``list`` \n
            Vector representing the allocation of each asset in the portfolio. Must be preserve the order of `portfolio.tickers`, i.e. each element's index should map to each element of the `portfolio.tickers`'s list.\n\n

        Returns
        -------
        ``float``\n
            The portfolio volatility on an annualized basis.
        """
        return numpy.sqrt(numpy.multiply(x, self.sample_vol).dot(self.correlation_matrix).dot(numpy.transpose(numpy.multiply(x, self.sample_vol))))

    def sharpe_ratio_function(self, x):
        """
        Returns the portfolio sharpe ratio for a vector of allocations. This function can be used as objective input function for `scipy.optimize`'s optimization or solver methods.\n\n

        Parameters
        ----------
        1. x : ``list`` \n
            Vector representing the allocation of each asset in the portfolio. Must be preserve the order of `portfolio.tickers`, i.e. each element's index should map to each element of the `portfolio.tickers`'s list.\n\n

        Returns
        -------
        ``float``
            The portfolio sharpe ratio on an annualized basis.
        """
        return (numpy.dot(x, self.mean_return) - self.risk_free_rate) / (self.volatility_function(x))

    def percentile_function(self, x, time, prob):
        """
        Returns the given percentile of the portfolio's assumed distribution.\n\n

        Parameters
        ----------
        1. x: list \n
            Vector representing the allocation of each asset in the portfolio. Must be preserve the order of `portfolio.tickers`, i.e. each element's index should map to each element of the `portfolio.tickers`'s list.\n\n
        2: time : float \n
            time horizon (in years) of the value at risk, i.e. the period of time into the future at which the value at risk is being calculated \n \n
        3. prob: float \b
            percentile desired
        """
        portfolio_return = self.return_function(x) * time
        portfolio_volatility = self.volatility_function(x) * numpy.sqrt(time)

        return probability.percentile(S0=1, vol=portfolio_volatility, ret=portfolio_return, 
                                        expiry=time, percentile=prob)

    def conditional_value_at_risk_function(self, x, time, prob):
        """
        Calculates the conditional value at risk for a portfolio of stocks over a specified time horizon. The value will be given in percentage terms relative to the initial value of the portfolio at the beginning of the time horizon, i.e. a return value of 5% would mean 5% of your portfolio's initial value is at risk with probability `prob`. A negative value would indicate there is no value at risk, i.e. value would actually accrue. This function can be used as objective input function for `scipy.optimize`'s optimization or solver methods.\n\n

        Parameters
        ----------
        1. x : float[] \n
            an array of decimals representing percentage allocations of the portfolio. Must preserve order with self.tickers.\n \n
        2. time : float \n
            time horizon (in years) of the value at risk, i.e. the period of time into the future at which the value at risk is being calculated \n \n
        3. prob : float \n
            desired probability of loss. \n
        """
        portfolio_return = self.return_function(x) * time
        portfolio_volatility = self.volatility_function(x) * numpy.sqrt(time)
        value_at_risk = self.percentile_function(x=x, time=time,prob=prob)
        return (1 - probability.conditional_expected_value(S0=1,vol=portfolio_volatility, ret=portfolio_return,
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
        return [ [0, 1] for y in range(len(self.tickers)) ] 

    def set_target_return(self, target):
        self.target_return = target

    def get_target_return_constraint(self, x):
        return (numpy.dot(x, self.mean_return) - self.target_return)

    def calculate_approximate_shares(self, x, total, latest_prices=None):
        shares = []
        for i, item in enumerate(x):
            if latest_prices is not None:
                price = latest_prices[i]
            elif self.sample_prices is not None:
                price = self.sample_prices[self.tickers[i]][0]                               
            else:
                price = services.get_daily_price_latest(self.tickers[i])

            share = Decimal(item) * Decimal(total) / Decimal(price) 
            shares.append(math.trunc(share))

        return shares

    def calculate_actual_total(self, x, total, latest_prices=None):
        actual_total = 0
        shares = self.calculate_approximate_shares(x=x, total=total, latest_prices=latest_prices)
        for i, item in enumerate(shares):
            if latest_prices is not None:
                price = latest_prices[i]
            elif self.sample_prices is not None:
                price = self.sample_prices[self.tickers[i]][0]                                     
            else:
                price = services.get_daily_price_latest(self.tickers[i])
            portion = Decimal(item) * Decimal(price)
            actual_total = actual_total + portion
        return actual_total