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
        "UPDATE profile SET a=:a,b=:b WHERE ticker=:ticker AND start_date=:start_date AND end_date=:end_date AND method=:method AND weekends=:weekends"
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
    assert ProfileCache._construct_insert(params) == expected


@pytest.mark.parametrize('ticker,prices,expected',[
    (
        'ALLY',
        {
            '2020-01-01': {
                'open': 51,
                'close': 53
            },
            '2020-01-02': {
                'open': 52,
                'close': 12
            }
        },
        [
            {
                'ticker': 'ALLY',
                'date': '2020-01-01',
                'open': 51,
                'close': 53,
            },
            {
                'ticker': 'ALLY',
                'date': '2020-01-02',
                'open': 52,
                'close': 12,
            }
        ]
    )
])
def test_price_cache_to_params(ticker, prices, expected):
    assert PriceCache()._to_params(ticker, prices) == expected

@pytest.mark.parametrize('rates,expected',[
    (
        {
            '2020-01-01': [0.01, 0.02, 0.03, 0.04, 0.05, 0.06, 0.07, 0.08, 0.09, 0.10, 0.11, 0.12]
            # '2020-01-01':{
            #     "ONE_MONTH": 0.01, 
            #     "TWO_MONTH": 0.02, 
            #     "THREE_MONTH": 0.03, 
            #     "SIX_MONTH": 0.04, 
            #     "ONE_YEAR": 0.05, 
            #     "TWO_YEAR": 0.06, 
            #     "THREE_YEAR": 0.07, 
            #     "FIVE_YEAR": 0.08, 
            #     "SEVEN_YEAR": 0.09, 
            #     "TEN_YEAR": 0.10, 
            #     "TWENTY_YEAR": 0.11, 
            #     "THIRTY_YEAR": 0.12
            # },
        },
        [
            {
                'date': '2020-01-01',
                'value': 0.01,
                'maturity': 'ONE_MONTH'
            },
            {
                'date': '2020-01-01',
                'value': 0.02,
                'maturity': 'TWO_MONTH'
            },
            {
                'date': '2020-01-01', 
                'value': 0.03,
                'maturity': 'THREE_MONTH' 
            },
            {
                'date': '2020-01-01',
                'value': 0.04,
                'maturity': 'SIX_MONTH' 
            },
            {
                'date': '2020-01-01',
                'value': 0.05,
                'maturity': 'ONE_YEAR' 
            },
            {
                'date': '2020-01-01',
                'value': 0.06,
                'maturity': 'TWO_YEAR' 
            },
            {
                'date': '2020-01-01',
                'value': 0.07,
                'maturity': 'THREE_YEAR' 
            },
            {
                'date': '2020-01-01',
                'value': 0.08,
                'maturity': 'FIVE_YEAR' 
            },
            {
                'date': '2020-01-01',
                'value': 0.09,
                'maturity': 'SEVEN_YEAR' 
            },
            {
                'date': '2020-01-01',
                'value': 0.10, 
                'maturity': 'TEN_YEAR'
            },
            {
                'date': '2020-01-01',
                'value': 0.11, 
                'maturity': 'TWENTY_YEAR'
            },
            {
                'date': '2020-01-01',
                'value': 0.12,
                'maturity': 'THIRTY_YEAR'
            }
        ]
    )
])
def test_interest_cache_to_params(rates, expected):
    assert InterestCache()._to_params(rates) == expected

@pytest.mark.parametrize('results,expected',[
    (
        [ 
            {
                'date': '2020-01-04',
                'value': 0.01,
            },
            {
                'date': '2020-01-01',
                'value': 0.02,
            },
            {
                'date': '2020-01-02', 
                'value': 0.03,
            },
            {
                'date': '2020-01-03',
                'value': 0.04,
            },
        ],
        {
            '2020-01-04': 0.01,
            '2020-01-03': 0.04,
            '2020-01-02': 0.03,
            '2020-01-01': 0.02
        }

    ),
])
def test_interest_cache_to_dict_dynamodb(results, expected):
    assert InterestCache().to_dict(results, 'dynamodb') == expected