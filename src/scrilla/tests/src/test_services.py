import pytest

from scrilla import services
from scrilla.util.errors import validate_dates
from scrilla.util import dater
from scrilla.static.keys import keys

from scrilla import settings as scrilla_settings
from scrilla.cache import PriceCache, InterestCache, ProfileCache
from scrilla.files import clear_cache, init_static_data

from .. import mock_data, settings
from httmock import HTTMock


init_static_data()

@pytest.fixture(autouse=True)
def reset_cache():
    clear_cache(mode='sqlite')
    PriceCache(mode='sqlite')
    InterestCache(mode='sqlite')
    

@pytest.mark.parametrize("ticker,date,price", [
    ('ALLY', '2021-10-22', 50.70),
    ('BX', '2021-09-08', 128.31),
    ('DIS', '2021-10-04', 173.46)
])
def test_past_price(ticker, date, price):
    with HTTMock(mock_data.mock_prices):
        response = services.get_daily_price_history(
            ticker=ticker, start_date=settings.START, end_date=settings.END)
    response_price = response[date][keys['PRICES']['CLOSE']]
    assert(float(response_price) == price)


@pytest.mark.parametrize('ticker,asset_type', [
    ('ALLY', keys['ASSETS']['EQUITY']),
    ('BTC', keys['ASSETS']['CRYPTO']),
    ('ALGO', keys['ASSETS']['CRYPTO']),
    ('SPY', keys['ASSETS']['EQUITY'])
])
def test_service_date_validation(ticker, asset_type):
    with HTTMock(mock_data.mock_prices):
        response = services.get_daily_price_history(
            ticker=ticker, start_date=settings.START, end_date=settings.END)
    validated_start, validated_end = validate_dates(start_date=settings.START, end_date=settings.END,
                                                    asset_type=asset_type)
    assert(dater.to_string(validated_start) in list(response.keys()))
    assert(dater.to_string(validated_end) in list(response.keys()))


@pytest.mark.parametrize("maturity,date,yield_rate", [
    ('ONE_MONTH', "2021-11-01", 0.05),
    ('THIRTY_YEAR',
     "2021-10-26", 2.05),
    ('ONE_YEAR',
     "2021-10-14", 0.1)
])
def test_past_interest(maturity, date, yield_rate):
    with HTTMock(mock_data.mock_treasury):
        response = services.get_daily_interest_history(
            maturity=maturity, start_date=settings.START, end_date=settings.END)
    assert(response[date] == yield_rate)

@pytest.mark.parametrize('ticker,date,amount',[
    ('ALLY', '2021-08-16', 0.25),
    ('DIS', '2020-01-16', 0.88)
])
def test_past_dividend(ticker, date, amount):
    with HTTMock(mock_data.mock_dividends):
        response = services.get_dividend_history(ticker)
    assert response[date] == amount