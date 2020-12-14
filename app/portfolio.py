import app.statistics as stat_calc
import numpy 

class Portfolio:
    
    def __init__(self, tickers):
        self.tickers = tickers
        self.calculate_stats()

    
    def calculate_stats(self):
        self.mean_return = []
        self.sample_vol = []

        for ticker in self.tickers:
            stats = stat_calc.calculate_risk_return(ticker)
            self.mean_return.append(stats['annual_return'])
            self.sample_vol.append(stats['annual_volatility'])

        for ret in self.mean_return:
            print(ret)

    def return_function(self, x):
        return numpy.dot(x, self.mean_return)

    def volatility_function(self, x):
        return numpy.dot(x, self.sample_vol)

    def get_init_guess(self):
        length = len(self.tickers)
        uniform_guess = 1/length
        guess = []
        for ticker in self.tickers:
            guess.append(uniform_guess)
        return guess