import pytest 
from httmock import HTTMock

from scrilla import services
from scrilla.static import keys

from . import mock


@pytest.mark.parametrize("ticker,price", [('ALLY', 47.93), ('BX', 146.44), ('DIS', 154.00)] )
def test_latest_price(ticker, price):
    with HTTMock(mock.mock_prices):
        response = services.get_daily_price_latest(ticker=ticker)
    assert(float(response) == price)

@pytest.mark.parametrize("ticker,date,price", [
                                                ('ALLY', '2021-10-22', 50.70), 
                                                ('BX', '2021-09-08', 128.31), 
                                                ('DIS', '2021-10-04', 173.46)
                                            ])
def test_past_price(ticker, date, price):
    with HTTMock(mock.mock_prices):
        response = services.get_daily_price_history(ticker=ticker)
    response_price = response[date][keys.keys['PRICES']['CLOSE']]
    assert(float(response_price) == price)



