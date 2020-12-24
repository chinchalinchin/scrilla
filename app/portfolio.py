import app.statistics as statistics
import app.services as services
import app.settings as settings

import numpy
import math
from decimal import Decimal

class Portfolio:
    
    def __init__(self, tickers):
        self.tickers = tickers
        self.calculate_stats()

    def calculate_stats(self):
        self.mean_return = []
        self.sample_vol = []
        self.correlation_matrix = [[0 for x in range(len(self.tickers))] for y in range(len(self.tickers))]

        for ticker in self.tickers:
            stats = statistics.calculate_risk_return(ticker)
            self.mean_return.append(stats['annual_return'])
            self.sample_vol.append(stats['annual_volatility'])

        if(len(self.tickers) > 1):
            for i in range(len(self.tickers)):
                for j in range(i+1, len(self.tickers)):
                    self.correlation_matrix[i][i] = 1
                    self.correlation_matrix[i][j] = statistics.calculate_correlation(self.tickers[i], self.tickers[j])['correlation']
                    self.correlation_matrix[j][i] = self.correlation_matrix[i][j]
            self.correlation_matrix[len(self.tickers) - 1][len(self.tickers) - 1] = 1

    def return_function(self, x):
        return numpy.dot(x, self.mean_return)

    def volatility_function(self, x):
        return numpy.sqrt(numpy.multiply(x, self.sample_vol).dot(self.correlation_matrix).dot(numpy.transpose(numpy.multiply(x, self.sample_vol))))

    def get_init_guess(self):
        length = len(self.tickers)
        uniform_guess = 1/length
        guess = [uniform_guess for i in range(length)]
        return guess
    
    def get_constraint(self, x):
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
            prices = services.retrieve_prices_from_cache_or_web(self.tickers[i])
            final_date = list(prices.keys())[0]
            final_price = prices[final_date][settings.AV_EQUITY_CLOSE_PRICE]
            share = Decimal(x[i]) * Decimal(total) / Decimal(final_price)
            shares.append(math.trunc(share))
        return shares

    def calculate_actual_total(self, x, total):
        actual_total = 0
        shares = self.calculate_approximate_shares(x, total)
        for i in range(len(shares)):
            prices = services.retrieve_prices_from_cache_or_web(self.tickers[i])
            final_date = list(prices.keys())[0]
            final_price = prices[final_date][settings.AV_EQUITY_CLOSE_PRICE]
            portion = Decimal(shares[i]) * Decimal(final_price)
            actual_total = actual_total + portion
        return actual_total