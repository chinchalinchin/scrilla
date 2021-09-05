import numpy, math
from decimal import Decimal

import analysis.statistics as statistics
import analysis.blackscholes as blackscholes
import services
import settings
import files

import util.outputter as outputter 

logger = outputter.Logger("objects.portfolio", settings.LOG_LEVEL)

# TODO: allow user to specify bounds for equities, i.e. min and max allocations.
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
    5. risk_profile : { ticker: { 'annual_return': float, 'annual_volatility': float }} \n
        Optional: Rather than use sample statistics calculated from historical data, this argument can override the calculated values.
    6. correlation_matrix : [ float ][ float ] \n
        Optional: Rather than use correlations calculated from historical data, this argument can override the calculated vlaues.
    6. asset_return_functions: [ function(t) ] \n
        Optional. An array of function that describes the expected logarithmic rate of return of each asset in the portfolio with respect to time. The order between `asset_return_functions` and `tickers` be must be preserved, i.e. the index of tickers must correspond to the symbol described by the function with same index in `asset_return_functions`. \n \n 
    7. asset_volatility_funtions: [ function(t) ] \n
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
                    correlation_matrix=None, risk_profiles=None, risk_free_rate=None,
                    asset_return_functions=None, asset_volatility_functions=None):
        self.shares = None
        self.actual_total = None

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
        
        self.error = not self.calculate_stats()

        if risk_free_rate is None:
            self.risk_free_rate = services.get_risk_free_rate()
        else:
            self.risk_free_rate = risk_free_rate

        # todo: calculate stats with lambda functions.
    # Returns False if calculations fail
    def calculate_stats(self):
        self.mean_return = []
        self.sample_vol = []

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
                        stats = statistics.calculate_risk_return(ticker=ticker, sample_prices=self.sample_prices[ticker])
                    else: 
                        stats = statistics.calculate_risk_return(ticker=ticker, start_date=self.start_date, end_date=self.end_date)
                    if stats is None:
                        return False

                    self.mean_return.append(stats['annual_return'])
                    self.sample_vol.append(stats['annual_volatility'])
            else:
                for ticker in self.risk_profiles:
                    self.mean_return.append(self.risk_profiles[ticker]['annual_return'])
                    self.sample_vol.append(self.risk_profiles[ticker]['annual_volatility']) 

            if self.correlation_matrix is None:
                self.correlation_matrix =  statistics.ito_correlation_matrix(tickers=self.tickers,
                                                                start_date=self.start_date, end_date=self.end_date,
                                                                sample_prices=self.sample_prices)
            return True


    def return_function(self, x):
        return numpy.dot(x, self.mean_return)

    def volatility_function(self, x):
        return numpy.sqrt(numpy.multiply(x, self.sample_vol).dot(self.correlation_matrix).dot(numpy.transpose(numpy.multiply(x, self.sample_vol))))

    def sharpe_ratio_function(self, x):
        return (numpy.dot(x, self.mean_return) - self.risk_free_rate) / (self.volatility_function(x))

    def percentile_function(self, x, time, prob):
        """
        Description
        -----------

        Returns the normalized percentile. In other words, returns Z-score for the portfolio. \n

        Parameters
        ----------
        1. x: float[] \n
            an array of decimals representing percentage allocations of the portfolio. Must preserve order with self.tickers.\n \n
        2: time : float \n
            time horizon (in years) of the value at risk, i.e. the period of time into the future at which the value at risk is being calculated \n \n
        3. prob: float \b
            percentile desired
        """
        portfolio_return = self.return_function(x) * time
        portfolio_volatility = self.volatility_function(x) * numpy.sqrt(time)

        return blackscholes.percentile(S0=1, vol=portfolio_volatility, ret=portfolio_return, 
                                        expiry=time, percentile=prob)

    def conditional_value_at_risk_function(self, x, time, prob):
        """
        Description
        -----------
        Calculates the Black Scholes' conditional value at risk for a portfolio of stocks over a specified time horizon. The value will be given in percentage terms relative to the initial value of the portfolio at the beginning of the time horizon, i.e. a return value of 5% would mean 5% of your portfolio's initial value is at risk with probability `prob`. A negative value would indicate there is no value at risk, i.e. value would actually accrue. 

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
        return (1 - blackscholes.conditional_expected_value(S0=1,vol=portfolio_volatility, ret=portfolio_return,
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
                asset_type = files.get_asset_type(symbol=self.tickers[i])
                price = services.parse_price_from_date(prices=self.sample_prices[self.tickers[i]],
                                                        date=list(self.sample_prices[self.tickers[i]].keys())[0],
                                                        asset_type=asset_type)                                 
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
                asset_type = files.get_asset_type(symbol=self.tickers[i])
                price = services.parse_price_from_date(prices=self.sample_prices[self.tickers[i]],
                                                        date=list(self.sample_prices[self.tickers[i]].keys())[0],
                                                        asset_type=asset_type)                                   
            else:
                price = services.get_daily_price_latest(self.tickers[i])
            portion = Decimal(item) * Decimal(price)
            actual_total = actual_total + portion
        return actual_total