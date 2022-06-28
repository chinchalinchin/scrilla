import pytest

from scrilla.static import keys
from scrilla.cache import PriceCache, InterestCache, ProfileCache
from scrilla.files import clear_cache
from scrilla.services import get_daily_price_history, get_daily_interest_history
from scrilla.util import dater

from unittest.mock import MagicMock, patch
from .. import mock_data, settings as test_settings
from httmock import HTTMock
from moto import mock_dynamodb

# NOTE: moto hasn't implemented a mock backend for `execute_statement`, `execute_transaction` or `execute_batch_statements`,
#       and the dynamodb cache functionality is implemented entirely (with the exception of creating and dropping tables)
#       through PartiQL statements and transactions. Until moto supports needed operations will need to find another way to 

price_internal_cache_case = (
        'ALLY',
        {
            '2020-01-10': {
                'open': 51,
                'close':53
            },
            '2020-01-09':{
                'open': 50,
                'close': 11
            },
            '2020-01-04': {
                'open': 49,
                'close': 12.4
            },
            '2020-01-02': {
                'open': 52,
                'close': 12
            },

        },
        [
            {
                '2020-01-10': {
                    'open': 51,
                    'close':53
                }
            },
            {
               '2020-01-09':{
                    'open': 50,
                    'close': 11
                } 
            },
            {
                '2020-01-04': {
                    'open': 49,
                    'close': 12.4
                },
            },
            {
                '2020-01-02': {
                    'open': 52,
                    'close': 12
                },
            }
        ]
    )
price_internal_cache_case_query_results = (*price_internal_cache_case, [
    ['2020-01-10',51,53],
    ['2020-01-09', 50, 11],
    ['2020-01-04', 49, 12.4],
    ['2020-01-02', 52,12]
])


interest_internal_cache_case = [
    (
        {
            '2020-01-01': [0.01, 0.02, 0.03, 0.04, 0.05, 0.06, 0.07, 0.08, 0.09, 0.10, 0.11, 0.12],
            '2020-01-02': [0.02, 0.03, 0.04, 0.05, 0.06, 0.07, 0.08, 0.09, 0.10, 0.11, 0.12, 0.13],
        },
        [
            {
                '2020-01-01': 0.01
            },
            {
                '2020-01-01': 0.02
            },
            {
                '2020-01-01': 0.03
            },
            {
                '2020-01-01': 0.04
            },
            {
                '2020-01-01': 0.05
            },
            {
                '2020-01-01': 0.06
            },
            {
                '2020-01-01': 0.07
            },
            {
                '2020-01-01': 0.08
            },
            {
                '2020-01-01': 0.09
            },
            {
                '2020-01-01': 0.10
            },
            {
                '2020-01-01': 0.11
            },
            {
                '2020-01-01': 0.12
            },
            {
                '2020-01-02': 0.02
            },
            {
                '2020-01-02': 0.03
            },
            {
                '2020-01-02': 0.04
            },
            {
                '2020-01-02': 0.05
            },
            {
                '2020-01-02': 0.06
            },
            {
                '2020-01-02': 0.07
            },
            {
                '2020-01-02': 0.08
            },
            {
                '2020-01-02': 0.09
            },
            {
                '2020-01-02': 0.10
            },
            {
                '2020-01-02': 0.11
            },
            {
                '2020-01-02': 0.12
            },
            {
                '2020-01-02': 0.13
            },
            
        ]
    )
]

@pytest.fixture(autouse=True)
def mock_aws():
    dynamo = mock_dynamodb()
    dynamo.start()
    yield
    dynamo.stop()


@pytest.fixture(autouse=True)
def reset_cache():
    clear_cache(mode='sqlite')


@pytest.fixture()
def sqlite_price_cache():
    return PriceCache(mode='sqlite')


@pytest.fixture()
def sqlite_interest_cache():
    return InterestCache(mode='sqlite')


@pytest.fixture()
def sqlite_profile_cache():
    return ProfileCache(mode='sqlite')


@pytest.fixture()
def dynamodb_price_cache():
    return PriceCache(mode='dynamodb')


@pytest.fixture()
def dynamodb_interest_cache():
    return InterestCache(mode='dynamodb')


@pytest.fixture()
def dynamodb_profile_cache():
    return ProfileCache(mode='dynamodb')


@pytest.mark.parametrize("ticker,date,price", [
    ('ALLY', '2021-10-22', 50.70),
    ('BX', '2021-09-08', 128.31),
    ('DIS', '2021-10-04', 173.46)
])
def test_sqlite_price_cache(ticker, date, price, sqlite_price_cache):
    with HTTMock(mock_data.mock_prices):
        get_daily_price_history(
            ticker=ticker, start_date=test_settings.START, end_date=test_settings.END)
    cache_results = sqlite_price_cache.filter(
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
def test_sqlite_interest_cache(maturity, date, yield_rate, sqlite_interest_cache):
    with HTTMock(mock_data.mock_interest):
        get_daily_interest_history(
            maturity=maturity, start_date=test_settings.START, end_date=test_settings.END)
    cache_results = sqlite_interest_cache.filter(
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
        "INSERT INTO profile (a,b) VALUES (:a,:b)"
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
    assert PriceCache._to_params(ticker, prices) == expected

@pytest.mark.parametrize('rates,expected',[
    (
        {
            '2020-01-01': [0.01, 0.02, 0.03, 0.04, 0.05, 0.06, 0.07, 0.08, 0.09, 0.10, 0.11, 0.12]
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
    assert InterestCache._to_params(rates) == expected

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
    actual = InterestCache.to_dict(results, 'dynamodb')
    actual_keys = list(actual.keys())
    assert InterestCache().to_dict(results, 'dynamodb') == expected
    assert all( dater.parse(actual_keys[i]) < dater.parse(actual_keys[i-1])
                    for i in range(1,len(actual_keys)))
                    
@pytest.mark.parametrize('results,expected',[
    (
        [
            {
                'ticker': 'ALLY',
                'date': '2020-01-10',
                'open': 51,
                'close': 53,
            },
            {
                'ticker': 'ALLY',
                'date': '2020-01-02',
                'open': 52,
                'close': 12,
            },
            {
                'ticker': 'ALLY',
                'date': '2020-01-09',
                'open': 50,
                'close': 11,
            },{
                'ticker': 'ALLY',
                'date': '2020-01-04',
                'open': 49,
                'close': 12.4,
            }
        ],
        {
            '2020-01-10': {
                'open': 51,
                'close':53
            },
            '2020-01-09':{
                'open': 50,
                'close': 11
            },
            '2020-01-04': {
                'open': 49,
                'close': 12.4
            },
            '2020-01-02': {
                'open': 52,
                'close': 12
            },

        }
    )
])
def test_price_cache_to_dict_dynamodb(results, expected):
    actual = PriceCache.to_dict(results, 'dynamodb')
    actual_keys = list(actual.keys())

    assert actual == expected
    assert all( dater.parse(actual_keys[i]) < dater.parse(actual_keys[i-1])
                    for i in range(1,len(actual_keys)))


@pytest.mark.parametrize('ticker,prices,expected', [price_internal_cache_case])
def test_price_internal_cache_save_hook(prices, ticker, expected, sqlite_price_cache):
    sqlite_price_cache.save_rows(ticker, prices)
    for index, date in enumerate(prices.keys()):
        real_date = dater.parse(date)
        assert sqlite_price_cache._retrieve_from_internal_cache(ticker, real_date, real_date) == expected[index]
# test: create caches, save_rows, check the internal cache was updated

@pytest.mark.parametrize('rates,expected', [interest_internal_cache_case])
def test_interest_internal_cache_save_hook(rates, expected, sqlite_interest_cache):
    sqlite_interest_cache.save_rows(rates)
    for date_index, date in enumerate(rates.keys()):
        real_date = dater.parse(date)
        for yield_index, maturity in enumerate(keys.keys['YIELD_CURVE']):
            sqlite_interest_cache._retrieve_from_internal_cache(maturity, real_date, real_date) ==\
                expected[date_index*len(keys.keys['YIELD_CURVE'])+yield_index]

# TODO: mock sqlite and filter cache, check to see if internal cache was updated
# TODO: same for profile, but make sure both insert/update paths are hit


@pytest.mark.parametrize('ticker,prices,expected', [price_internal_cache_case_query_results])
def test_price_internal_cache_update_hook(ticker, prices, expected, query_results, sqlite_price_cache):
    with patch('scrilla.cache.sqlite3') as mocksqlite:
        mocksqlite.connect().cursor().fetchall.return_value = query_results
        for index, date in enumerate(prices.keys()):
            start_date = dater.parse(date)
            sqlite_price_cache.filter(ticker, start_date, start_date)
            internal_cache = sqlite_price_cache._retrieve_from_internal_cache(ticker, start_date, start_date)
            assert internal_cache == expected[index]