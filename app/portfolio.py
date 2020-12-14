import app.statistics as stat_calc
import numpy, math

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
        return numpy.multiply(x, self.sample_vol).dot(self.correlation_matrix).dot(numpy.transpose(numpy.multiply(x, self.sample_vol)))

    def get_init_guess(self):
        length = len(self.tickers)
        uniform_guess = 1/length
        guess = []
        for ticker in self.tickers:
            guess.append(uniform_guess)
        return guess
    
    def get_constraint(self, x):
        return sum(x) - 1
    
    def get_bounds(self, tickers):
        return [ [0, 1] for y in range(len(tickers)) ] 