import pytest 
from httmock import HTTMock

from scrilla.analysis.objects.portfolio import Portfolio

from .... import mock

END="2021-11-19"
START="2021-07-14"

@pytest.fixture()
def portfolios():
    return [
            Portfolio(tickers=['ALLY','BX'], start_dae=START, end_date=END), 
            Portfolio(tickers=['SPY','BTC'], start_date=START, end_date=END), 
            Portfolio(tickers=['BTC','ALGO'], start_date=START, end_date=END), 
            Portfolio(tickers=['ALLY','DIS','BX'], start_date=START, end_date=END),
            Portfolio(tickers=['SPY','GLD','BTC'], start_date=START, end_date=END),
            Portfolio(tickers=['ALLY','SPY','BTC','ALGO'], start_date=START, end_date=END)
            ]

def test_portfolio_initialization(portfolios):
    with HTTMock(mock.mock_prices):
        test_portfolios = Portfolio(*portfolios)
    start_date_init = all([portfolio.start_date is not None for portfolio in test_portfolios])
    end_date_init = all([portfolio.end_date is not None for portfolio in test_portfolios])
    asset_type_init = all([len(portfolio.asset_types) == len(portfolio.tickers) for portfolio in test_portfolios])
    return_init = all([len(portfolio.mean_return) == len(portfolio.tickers) for portfolio in test_portfolios])
    vol_init = all([len(portfolio.sample_vol) == len(portfolio.tickers) for portfolio in test_portfolios])
    correl_init = all([portfolio.correlation_matrix is not None for portfolio in test_portfolios])
    rf_init = all([portfolio.risk_free_rate is not None for portfolio in test_portfolios])
    assert(start_date_init)
    assert(end_date_init)
    assert(asset_type_init)
    assert(return_init)
    assert(vol_init)
    assert(correl_init)
    assert(rf_init)

@pytest.mark.parametrize('tickers,weekends', [
                                                (['ALLY','BX'], 0)
                                                (['BTC', 'ALGO', 1])
                                                (['BTC', 'ALLY', 0])
                                                (['BTC', 'ALGO'])
                                                (['BTC', 'ALGO', 'SPY', 0])
])
def test_weekend_initialization(tickers, weekends):
    with HTTMock(mock.mock_prices):
        test_portfolio = Portfolio(tickers=tickers, start_date=START, end_date=END)
    assert(test_portfolio.weekends == weekends)
