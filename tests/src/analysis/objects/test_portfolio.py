import pytest 
from httmock import HTTMock

from scrilla.analysis.objects.portfolio import Portfolio

from .... import mock

@pytest.mark.parametrize("tickers", [('ALLY', 'BX', 'DIS')] )
def test_portfolio_initialization(tickers):
    with HTTMock(mock.mock_prices):
        pass
    pass
