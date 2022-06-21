import pytest

from scrilla import settings as scrilla_settings
from scrilla.static import keys
from scrilla.cache import PriceCache, InterestCache, ProfileCache
from scrilla.files import clear_directory
from scrilla.services import get_daily_price_history, get_daily_interest_history

from .. import mock, settings as test_settings
from httmock import HTTMock
from moto import mock_dynamodb

@pytest.fixture(autouse=True)
def reset_cache():
    clear_directory(scrilla_settings.CACHE_DIR)


@pytest.fixture()
def price_cache():
    return PriceCache()


@pytest.fixture()
def interest_cache():
    return InterestCache()


@pytest.fixture()
def profile_cache():
    return ProfileCache()

@mock_dynamodb
def test_dynamo_transaction():
    # TODO
    pass

def test_sqlite_transaction():
    # TODO
    pass

@pytest.mark.parametrize("ticker,date,price", [
    ('ALLY', '2021-10-22', 50.70),
    ('BX', '2021-09-08', 128.31),
    ('DIS', '2021-10-04', 173.46)
])
def test_cache(ticker, date, price, price_cache):
    with HTTMock(mock.mock_prices):
        get_daily_price_history(
            ticker=ticker, start_date=test_settings.START, end_date=test_settings.END)
    cache_results = price_cache.filter_price_cache(
        ticker=ticker, start_date=date, end_date=date)
    assert(len(cache_results) ==
           1 and cache_results[date][keys.keys['PRICES']['CLOSE']] == price)


@pytest.mark.parametrize("maturity,date,yield_rate", [
    ('ONE_MONTH', "2021-11-01", 0.05),
    ('THIRTY_YEAR',
     "2021-10-26", 2.05),
    ('ONE_YEAR',
     "2021-10-14", 0.1)
])
def test_past_interest(maturity, date, yield_rate, interest_cache):
    with HTTMock(mock.mock_interest):
        get_daily_interest_history(
            maturity=maturity, start_date=test_settings.START, end_date=test_settings.END)
    cache_results = interest_cache.filter_interest_cache(
        maturity=maturity, start_date=date, end_date=date)
    assert(len(cache_results) == 1 and cache_results[date] == yield_rate)


@pytest.mark.parametrize('params,expected',[
    (
        {
            'a': 1,
            'b': 2
        },
        "UPDATE TABLE profile SET a=:a,b=:b WHERE ticker=:ticker AND start_date=:start_date AND end_date=:end_date AND method=:method AND weekends=:weekends"
    )
])
def test_profile_cache_construct_update_query(params, expected):
    assert ProfileCache._construct_update(params) == expected

@pytest.mark.parametrize('params,expected',[
    (
        {
            'a': 1,
            'b': 2
        },
        "INSERT INTO profile (ticker,start_date,end_date,a,b,method,weekends) VALUES (:ticker,:start_date,:end_date,:a,:b,:method,:weekends)"
    )
])
def test_profile_cache_construct_insert_query(params, expected):
    pass