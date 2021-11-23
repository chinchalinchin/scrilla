import pytest 

from scrilla.analysis.objects.portfolio import Portfolio

from .. import mock, settings
from httmock import HTTMock

@pytest.fixture()
def portfolios():
    with HTTMock(mock.mock_prices):
        with HTTMock(mock.mock_interest):
            portfolios = [
                Portfolio(tickers=['ALLY','BX'], start_date=settings.START, end_date=settings.END), 
                Portfolio(tickers=['SPY','BTC'], start_date=settings.START, end_date=settings.END), 
                Portfolio(tickers=['BTC','ALGO'], start_date=settings.START, end_date=settings.END), 
                Portfolio(tickers=['ALLY','DIS','BX'], start_date=settings.START, end_date=settings.END),
                Portfolio(tickers=['SPY','GLD','BTC'], start_date=settings.START, end_date=settings.END),
                Portfolio(tickers=['ALLY','SPY','BTC','ALGO'], start_date=settings.START, end_date=settings.END)
            ]
    return portfolios

def test_portfolio_initialization(portfolios):
    start_date_init = all([portfolio.start_date is not None for portfolio in portfolios])
    end_date_init = all([portfolio.end_date is not None for portfolio in portfolios])
    asset_type_init = all([len(portfolio.asset_types) == len(portfolio.tickers) for portfolio in portfolios])
    return_init = all([len(portfolio.mean_return) == len(portfolio.tickers) for portfolio in portfolios])
    vol_init = all([len(portfolio.sample_vol) == len(portfolio.tickers) for portfolio in portfolios])
    correl_init = all([portfolio.correlation_matrix is not None for portfolio in portfolios])
    rf_init = all([portfolio.risk_free_rate is not None for portfolio in portfolios])
    assert(False)
    assert(end_date_init)
    assert(asset_type_init)
    assert(return_init)
    assert(vol_init)
    assert(correl_init)
    assert(rf_init)

@pytest.mark.parametrize('tickers,weekends', [
                                                (['ALLY', 'BX'], 0),
                                                (['BTC', 'ALGO'], 1),
                                                (['BTC', 'ALLY'], 0),
                                                (['BTC', 'ALGO', 'SPY'], 0)
])
def test_weekend_initialization(tickers, weekends):
    with HTTMock(mock.mock_prices):
        with HTTMock(mock.mock_interest):
            test_portfolio = Portfolio(tickers=tickers, start_date=settings.START, end_date=settings.END)
    assert(test_portfolio.weekends == weekends)
