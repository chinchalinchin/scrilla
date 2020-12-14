import app.statistics as stat_calc

class Portfolio:
    
    def __init__(self, tickers):
        self.tickers = tickers
        self.calculate_stats()

    
    def calculate_stats(self):
        self.statistics = {}
        for ticker in self.tickers:
            self.statistics[ticker] = stat_calc.calculate_risk_return(ticker)
        for stat in self.statistics:
            print(self.statistics[stat])

    def return_function(self, x):
        weighted_return = 0
        for ticker in self.tickers:
            weighted_return = weighted_return + x[ticker]*self.statistics[ticker]['annual_return']
        return weighted_return

    def volatility_function(self, x):
        weighted_vol = 0
        for ticker in self.tickers:
            weighted_vol = weighted_vol + x[ticker]*self.statistics[ticker]['annual_volatility']
        return weighted_vol

    def get_init_guess(self):
        length = len(self.tickers)
        uniform_guess = 1/length
        guess = []
        for ticker in self.tickers:
            guess.append(uniform_guess)
        return guess