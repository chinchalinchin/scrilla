import sys, os

PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(PROJECT_DIR)


from analysis import optimizer
from analysis.objects.portfolio import Portfolio


if __name__=="__main__":
    test_tickers = ['ALLY','BX', 'SNE']
    portfolio = Portfolio(tickers=test_tickers)
    allocation = optimizer.optimize_portfolio_variance(portfolio=portfolio)
    print(portfolio.conditional_value_at_risk_function(x=allocation, time=0.5, prob=0.95))
