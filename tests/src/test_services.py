import pytest 

from scrilla import services
from scrilla.static import keys

from .. import mock, settings
from httmock import HTTMock

@pytest.mark.parametrize("ticker,date,price", [
                                                ('ALLY', '2021-10-22', 50.70), 
                                                ('BX', '2021-09-08', 128.31), 
                                                ('DIS', '2021-10-04', 173.46)
])
def test_past_price(ticker, date, price):
    with HTTMock(mock.mock_prices):
        response = services.get_daily_price_history(ticker=ticker, start_date=settings.START, end_date=settings.END)
    response_price = response[date][keys.keys['PRICES']['CLOSE']]
    assert(float(response_price) == price)

@pytest.mark.parametrize("ticker,date,price", [
                                                ('ALLY', '2021-10-22', 50.70), 
                                                ('BX', '2021-09-08', 128.31), 
                                                ('DIS', '2021-10-04', 173.46)
])
def test_cache_price(ticker, date, price):
    with HTTMock(mock.mock_prices):
        response = services.get_daily_price_history(ticker=ticker, start_date=settings.START, end_date=settings.END)
    response_price = response[date][keys.keys['PRICES']['CLOSE']]
    assert(float(response_price) == price)

@pytest.mark.parametrize("maturity,date,yield_rate", [
                                                        ('ONE_MONTH',"2021-11-01", 0.05), 
                                                        ('THIRTY_YEAR',"2021-10-26", 2.05), 
                                                        ('ONE_YEAR', "2021-10-14", 0.1)
])
def test_past_interest(maturity,date,yield_rate):
    with HTTMock(mock.mock_interest):
        response = services.get_daily_interest_history(maturity=maturity, start_date=settings.START, end_date=settings.END)
    assert(response[date] == yield_rate)

@pytest.mark.parametrize("maturity,date,yield_rate", [
                                                        ('ONE_MONTH',"2021-11-01", 0.05), 
                                                        ('THIRTY_YEAR',"2021-10-26", 2.05), 
                                                        ('ONE_YEAR', "2021-10-14", 0.1)
])
def test_cache_interest(maturity,date,yield_rate):
    with HTTMock(mock.mock_interest):
        response = services.get_daily_interest_history(maturity=maturity, start_date=settings.START, end_date=settings.END)
    assert(response[date] == yield_rate)


