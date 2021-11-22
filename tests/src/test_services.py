import pytest 
from httmock import HTTMock

from scrilla import settings as scrilla_settings
from scrilla.files import clear_directory
clear_directory(scrilla_settings.CACHE_DIR)

from scrilla import services
from scrilla.static import keys

from .. import mock


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

@pytest.mark.parametrize("maturity, yield_rate", [
                                                    ('ONE_MONTH', 0.11), 
                                                    ('THIRTY_YEAR', 1.91), 
                                                    ('ONE_YEAR', 0.18)] )
def test_latest_interest(maturity, yield_rate):
    with HTTMock(mock.mock_interest):
        response = services.get_daily_interest_latest(maturity=maturity)
    assert(float(response) == yield_rate)


@pytest.mark.parametrize("maturity,date,yield_rate", [
                                                        ('ONE_MONTH',"2021-11-01", 0.05), 
                                                        ('THIRTY_YEAR',"2021-10-26", 2.05), 
                                                        ('ONE_YEAR', "2021-10-14", 0.1)
                                                    ])
def test_past_interest(maturity,date,yield_rate):
    with HTTMock(mock.mock_interest):
        response = services.get_daily_interest_history(maturity=maturity)
    assert(response[date] == yield_rate)

