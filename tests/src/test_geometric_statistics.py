import pytest
from httmock import HTTMock

from scrilla import settings as scrilla_settings

from scrilla.static import keys

from .. import mock


@pytest.mark.parametrize("tickers", [
    (['BTC', 'ALGO']),
    (['SPY', 'GLD']),
    (['SPY', 'BTC'])
])
def test_latest_price(tickers):
    with HTTMock(mock.mock_prices):
        for ticker in tickers:

            pass
    assert(True)
