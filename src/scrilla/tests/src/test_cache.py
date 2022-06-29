import uuid
import pytest

from scrilla import settings
from scrilla.static import keys, config
from scrilla.cache import CorrelationCache, PriceCache, InterestCache, ProfileCache
from scrilla.files import clear_cache
from scrilla.services import get_daily_price_history, get_daily_interest_history
from scrilla.util import dater

from unittest.mock import patch
from .. import mock_data, settings as test_settings
from httmock import HTTMock
from moto import mock_dynamodb
import boto3

# NOTE: moto hasn't implemented a mock backend for `execute_statement`, `execute_transaction` or `execute_batch_statements`,
#       and the dynamodb cache functionality is implemented entirely (with the exception of creating and dropping tables)
#       through PartiQL statements and transactions. Until moto supports needed operations will need to find another way to 

# (ticker, prices, expected)


@pytest.fixture(autouse=True)
def mock_aws():
    dynamo = mock_dynamodb()
    dynamo.start()
    yield
    dynamo.stop()


@pytest.fixture(autouse=True)
def reset_cache():
    clear_cache(mode='sqlite')
    PriceCache(mode='sqlite')._table()
    InterestCache(mode='sqlite')._table()
    CorrelationCache(mode='sqlite')._table()
    ProfileCache(mode='sqlite')._table()


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
def sqlite_correlation_cache():
    return CorrelationCache(mode='sqlite')

@pytest.fixture()
def dynamodb_price_cache():
    return PriceCache(mode='dynamodb')

@pytest.fixture()
def dynamodb_correlation_cache():
    return CorrelationCache(mode='dynamodb')

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
        ticker=ticker, start_date=dater.parse(date), end_date=dater.parse(date))
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
    with HTTMock(mock_data.mock_treasury):
        get_daily_interest_history(
            maturity=maturity, start_date=test_settings.START, end_date=test_settings.END)
    cache_results = sqlite_interest_cache.filter(
        maturity=maturity, start_date=dater.parse(date), end_date=dater.parse(date))
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


@pytest.mark.parametrize('ticker,prices,expected',
    [mock_data.price_cache_to_param_case])
def test_price_cache_to_params(ticker, prices, expected):
    assert PriceCache._to_params(ticker, prices) == expected

@pytest.mark.parametrize('rates,expected', 
    [mock_data.interest_cache_to_param_case])
def test_interest_cache_to_params(rates, expected):
    assert InterestCache._to_params(rates) == expected

@pytest.mark.parametrize('results,expected',[mock_data.interest_cache_to_dict_dynamodb_case])
def test_interest_cache_to_dict_dynamodb(results, expected):
    actual = InterestCache.to_dict(results, 'dynamodb')
    actual_keys = list(actual.keys())
    assert InterestCache().to_dict(results, 'dynamodb') == expected
    assert all( dater.parse(actual_keys[i]) < dater.parse(actual_keys[i-1])
                    for i in range(1,len(actual_keys)))
                    
@pytest.mark.parametrize('results,expected', 
    [mock_data.price_cache_to_dict_dynamodb_case])
def test_price_cache_to_dict_dynamodb(results, expected):
    actual = PriceCache.to_dict(results, 'dynamodb')
    actual_keys = list(actual.keys())

    assert actual == expected
    assert all( dater.parse(actual_keys[i]) < dater.parse(actual_keys[i-1])
                    for i in range(1,len(actual_keys)))


@pytest.mark.parametrize('ticker,prices,expected', 
    [mock_data.price_internal_cache_case])
def test_price_internal_cache_save_hook(prices, ticker, expected, sqlite_price_cache):
    with patch('scrilla.cache.sqlite3'):
        sqlite_price_cache.save_rows(ticker, prices)
        for index, date in enumerate(prices.keys()):
            real_date = dater.parse(date)
            assert sqlite_price_cache._retrieve_from_internal_cache(ticker, real_date, real_date) == expected[index]

@pytest.mark.parametrize('rates,expected', 
    [mock_data.interest_internal_cache_case])
def test_interest_internal_cache_save_hook(rates, expected, sqlite_interest_cache):
    with patch('scrilla.cache.sqlite3'):
        sqlite_interest_cache.save_rows(rates)
        for date_index, date in enumerate(rates.keys()):
            real_date = dater.parse(date)
            for yield_index, maturity in enumerate(keys.keys['YIELD_CURVE']):
                sqlite_interest_cache._retrieve_from_internal_cache(maturity, real_date, real_date) ==\
                    expected[date_index*len(keys.keys['YIELD_CURVE'])+yield_index]


@pytest.mark.parametrize('ticker,prices,expected,query_results', 
    [mock_data.price_internal_cache_case_query_results])
def test_price_internal_cache_update_hook(ticker, prices, expected, query_results, sqlite_price_cache):
    with patch('scrilla.cache.sqlite3') as mocksqlite:
        mocksqlite.connect().cursor().execute().fetchall.return_value = query_results
        for index, date in enumerate(prices.keys()):
            start_date = dater.parse(date)
            sqlite_price_cache.filter(ticker, start_date, start_date)
            internal_cache = sqlite_price_cache._retrieve_from_internal_cache(ticker, start_date, start_date)
            assert internal_cache == expected[index]

@pytest.mark.parametrize('maturity,rates,expected,query_results', 
    [mock_data.interest_internal_cache_case_query_results])
def test_interest_internal_cache_update_hook(maturity, rates, expected, query_results, sqlite_interest_cache):
    with patch('scrilla.cache.sqlite3') as mocksqlite:
        mocksqlite.connect().cursor().execute().fetchall.return_value = query_results
        for index, date in enumerate(rates.keys()):
            start_date = dater.parse(date)
            sqlite_interest_cache.filter(maturity, start_date, start_date)
            internal_cache = sqlite_interest_cache._retrieve_from_internal_cache(maturity, start_date, start_date)
            assert internal_cache == expected[index]

# TODO: update and save hook tests for profile and correlation cache

def test_dynamodb_table_creation(dynamodb_price_cache, dynamodb_profile_cache, dynamodb_correlation_cache, dynamodb_interest_cache):
    dynamo_tables = boto3.client('dynamodb').list_tables()['TableNames']
    table_names = [
        config.dynamo_price_table_conf['TableName'],
        config.dynamo_interest_table_conf['TableName'],
        config.dynamo_correlation_table_conf['TableName'],
        config.dynamo_profile_table_conf['TableName']
    ]
    for table_name in table_names:
        assert table_name in dynamo_tables

def test_price_cache_singularity():
    cache1 = PriceCache(mode='sqlite')
    cache2 = PriceCache(mode='sqlite')
    assert cache1.uuid == cache2.uuid

def test_interest_cache_singularity():
    cache1 = InterestCache(mode='sqlite')
    cache2 = InterestCache(mode='sqlite')
    assert cache1.uuid == cache2.uuid

def test_profile_cache_singularity():
    cache1 = ProfileCache(mode='sqlite')
    cache2 = ProfileCache(mode='sqlite')
    assert cache1.uuid == cache2.uuid

def test_correlation_cache_singularity():
    cache1 = CorrelationCache(mode='sqlite')
    cache2 = CorrelationCache(mode='sqlite')
    assert cache1.uuid == cache2.uuid