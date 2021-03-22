import app.statistics as statistics
import app.services as services
import app.settings as settings
import app.markets as markets

import util.outputter as outputter 

import numpy
import math
from decimal import Decimal

logger = outputter.Logger("app.objects.portfolio", settings.LOG_LEVEL)

class Portfolio:
    """
    Description
    -----------
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
    5. asset_return_functions: [ function(t) ] \n
    Optional. An array of function that describes the expected logarithmic rate of return of each asset in the portfolio with respect to time. The order between `asset_return_functions` and `tickers` be must be preserved, i.e. the index of tickers must correspond to the symbol described by the function with same index in `asset_return_functions`. \n \n 
    6. asset_volatility_funtions: [ function(t) ] \n
    Optional. An array of functions that describe the mean volatility of each asset in the portfolio with respect to time. The order between `asset_volatility_functions` and `tickers` be must be preserved, i.e. the index of tickers must correspond to the symbol described by the function with the same index in `asset_volatility_functions`. \n \n 

    Notes
    -----
    NOTE #1: While `start_date`, `end_date` and `sample_prices` are all by themselves optional, the Portfolio class must be initialized in one of two ways: \n
        1. Constructor args : (`start_date`, `end_date`) -> Dates are passed to service for external query. \n
        2. Constructor args : (`sample_prices`) -> Dates are ignored and sample is used instead of external query. \n 
    
    If all three are specified, `sample_prices` takes precedence and `start_date` and `end_date` are nulled. \n \n
    NOTE #2: The `asset_return_functions` and `asset_volatility_functions` can be understood as the drift and noise functions for a Geometric Brownian Motion stochastic process. \n \n
    """
    def __init__(self, tickers, start_date=None, end_date=None, sample_prices=None,
                    asset_return_functions=None, asset_volatility_functions=None):
        if sample_prices is None:
            self.start_date = start_date
            self.end_date = end_date
        else:
            self.start_date = None
            self.end_date = None

        self.tickers = tickers
        self.sample_prices = sample_prices
        self.asset_volatility_functions = asset_volatility_functions
        self.asset_return_functions = asset_return_functions
        
        self.error = not self.calculate_stats()

        self.risk_free_rate = markets.get_risk_free_rate()

        # todo: calculate stats with lambda functions.
    def calculate_stats(self):
        self.mean_return = []
        self.sample_vol = []
        self.correlation_matrix = [[0 for x in range(len(self.tickers))] for y in range(len(self.tickers))]

        if self.asset_volatility_functions is not None and self.asset_return_functions is not None:
            # use return and volatility functions to integrate over time period [0, infinity] for each asset. don't forget to 
            #   discount! I(x) = discounted expected payoff
            #   Integral(d ln S) = Integral(Mean dt) + Integral(Vol dZs)
            #   Need methods to compute ito Integrals in...statistics.py? markets.py? Perhaps a new module.
            # https://math.stackexchange.com/questions/1780956/mean-and-variance-geometric-brownian-motion-with-not-constant-drift-and-volatili
            pass

        else:
            for ticker in self.tickers:
                if self.sample_prices is not None:
                    stats = statistics.calculate_risk_return(ticker=ticker, start_date=self.start_date, end_date=self.end_date, 
                                                                sample_prices=self.sample_prices[ticker])
                else: 
                    stats = statistics.calculate_risk_return(ticker=ticker, start_date=self.start_date, end_date=self.end_date)

                if not stats:
                    return False
                self.mean_return.append(stats['annual_return'])
                self.sample_vol.append(stats['annual_volatility'])

            if(len(self.tickers) > 1):
                for i in range(len(self.tickers)):
                    for j in range(i+1, len(self.tickers)):
                        self.correlation_matrix[i][i] = 1
                        cor_list = statistics.calculate_ito_correlation(ticker_1 = self.tickers[i], ticker_2=self.tickers[j],
                                                                    start_date = self.start_date, end_date = self.end_date,
                                                                    sample_prices = self.sample_prices)
                        correlation = cor_list['correlation']
                        if not correlation:
                            return False
                        self.correlation_matrix[i][j] = correlation
                        self.correlation_matrix[j][i] = self.correlation_matrix[i][j]
                self.correlation_matrix[len(self.tickers) - 1][len(self.tickers) - 1] = 1
            return True


    def return_function(self, x):
        return numpy.dot(x, self.mean_return)

    def volatility_function(self, x):
        return numpy.sqrt(numpy.multiply(x, self.sample_vol).dot(self.correlation_matrix).dot(numpy.transpose(numpy.multiply(x, self.sample_vol))))

    def sharpe_ratio_function(self, x):
        return (numpy.dot(x, self.mean_return) - self.risk_free_rate) / (self.volatility_function(x))

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

    def calculate_approximate_shares(self, x, total):
        shares = []
        for i in range(len(x)):
            price = services.get_daily_price_latest(self.tickers[i])
            share = Decimal(x[i]) * Decimal(total) / Decimal(price)
            shares.append(math.trunc(share))
        return shares

    def calculate_actual_total(self, x, total):
        actual_total = 0
        shares = self.calculate_approximate_shares(x, total)
        for i in range(len(shares)):
            price = services.get_daily_price_latest(self.tickers[i])
            portion = Decimal(shares[i]) * Decimal(price)
            actual_total = actual_total + portion
        return actual_total