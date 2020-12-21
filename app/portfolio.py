import app.statistics as stat_calc
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
            stats = stat_calc.calculate_risk_return(ticker)
            self.mean_return.append(stats['annual_return'])
            self.sample_vol.append(stats['annual_volatility'])

        if(len(self.tickers) > 1):
            for i in range(len(self.tickers)):
                for j in range(i+1, len(self.tickers)):
                    self.correlation_matrix[i][i] = 1
                    self.correlation_matrix[i][j] = stat_calc.calculate_correlation(self.tickers[i], self.tickers[j])['correlation']
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

    def calculate_shares(self, x, total):
        shares = []
        for i in range(len(x)):
            prices = stat_calc.retrieve_stock_data(self.tickers[i])
            final_date = list(prices.keys())[0]
            final_price = prices[final_date]['4. close']
            share = Decimal(x[i]) * Decimal(total) / Decimal(final_price)
            shares.append(math.trunc(share))
        return shares

    def calculate_total(self, shares):
        total = 0
        for i in range(len(shares)):
            prices = stat_calc.retrieve_stock_data(self.tickers[i])
            final_date = list(prices.keys())[0]
            final_price = prices[final_date]['4. close']
            portion = Decimal(shares[i]) * Decimal(final_price)
            total = total + portion
        return total