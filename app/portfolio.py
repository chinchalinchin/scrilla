import app.statistics as stat_calc

class Portfolio:
    
    def __init__(self, tickers):
        self.tickers = tickers
        self.calculate_stats()

    
    def calculate_stats(self):
        self.statistics = {}
        for ticker in tickers:
            self.statistics[ticker] = stat_calc.calculate_risk_return(ticker)
        for stat in self.statistics:
            print(statistics[stat])

    def return_function(self, x):
        weighted_return = 0
        for ticker in tickers:
            weighted_return = weighted_return + x[ticker]*statistics[ticker]['annual_return']
        return weighted_return

    def volatility_function(self, x):
        weighted_vol = 0
        for ticker in tickers:
            weighted_vol = weighted_vol + x[ticker]*statistics[ticker]['annual_volatility']
        return weighted_vol