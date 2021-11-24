import pytest

from scrilla import errors
from scrilla.static import keys


@pytest.mark.parametrize('ticker,asset_type', [
    ('ALLY', keys['ASSETS']['EQUITY']),
    ('BTC', keys['ASSETS']['CRYPTO']),
    ('ALGO', keys['ASSETS']['CRYPTO']),
    ('SPY', keys['ASSETS']['EQUITY']),
    ('SPY', keys['ASSETS']['EQUITY']),
])
def test_asset_type_validation(ticker,asset_type):
    assert(errors.validate_asset_type(ticker) == asset_type)

@pytest.mark.parametrize('ticker,asset_type,start_date,end_date,expected_start,expected_end', [
    # weekend start, weekend end
    ('ALLY', keys['ASSETS']['EQUITY'], '2021-11-07', '2021-11-14', '2021-11-05', '2021-11-12'),
    ('BTC', keys['ASSETS']['CRYPTO'], '2021-11-07', '2021-11-14', '2021-11-07', '2021-11-14'),
    # holiday start, weekend ed
    ('ALGO', keys['ASSETS']['CRYPTO'], '2021-01-01', '2021-01-10', '2021-01-01', '2021-01-10'),
    ('SPY', keys['ASSETS']['EQUITY'], '2021-01-01', '2021-01-10', '2020-12-30','2021-01-08'),
    # weekday start, weekday end
    ('DIS', keys['ASSETS']['EQUITY'], '2021-09-01', '2021-09-09', '2021-09-01', '2021-09-09'),
    ('BTC', keys['ASSETS']['EQUITY'], '2021-09-01', '2021-09-09', '2021-09-01', '2021-09-09'),

])
def test_date_validation(ticker, asset_type, start_date, end_date, expected_start, expected_end):
    validated_start, validated_end = errors.validate_dates(start_date, end_date, asset_type)
    assert(validated_start == expected_start and validated_end == expected_end)
