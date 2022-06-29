import pytest
import json
from unittest.mock import patch, ANY

from httmock import HTTMock

from scrilla.main import do_program
from scrilla.cache import PriceCache, ProfileCache, InterestCache, CorrelationCache
from scrilla.files import clear_cache, init_static_data
from scrilla.static import keys

from .. import mock_data, settings

init_static_data()

@pytest.fixture(autouse=True)
def reset_cache():
    clear_cache(mode='sqlite')
    PriceCache(mode='sqlite'), ProfileCache(mode='sqlite')
    InterestCache(mode='sqlite'), CorrelationCache(mode='sqlite')


@pytest.mark.parametrize('args, length', [
    (['correlation', 'ALLY', 'BX', '-json', '-start',
     settings.START_STR, '-end', settings.END_STR], 2),
    (['correlation', 'BTC', 'SPY', 'GLD', '-json', '-start',
     settings.START_STR, '-end', settings.END_STR], 3),
    (['correlation', 'GLD', 'SPY', 'DIS', 'BX', '-json',
     '-start', settings.START_STR, '-end', settings.END_STR], 4)
])
def test_cli_correlation_json_format(args, length, capsys):
    with HTTMock(mock_data.mock_prices):
        with HTTMock(mock_data.mock_treasury):
            do_program(args)
    correl_matrix = json.loads(capsys.readouterr().out)
    # assert dimensions are correct length
    assert(len(correl_matrix['correlation_matrix']) == length)
    # assert all entries satisfy correlation bounds
    assert(all(all(bool((correl > -1 or correl == -1) and (correl < 1 or correl == 1))
           for correl in correl_list) for correl_list in correl_matrix['correlation_matrix']))


@pytest.mark.parametrize('args, length', [
    (['correlation', 'ALLY', 'BX', '-json', '-likelihood',
     '-start', settings.START_STR, '-end', settings.END_STR], 2),
    (['correlation', 'BTC', 'SPY', 'GLD', '-json', '-likelihood',
     '-start', settings.START_STR, '-end', settings.END_STR], 3),
    (['correlation', 'GLD', 'SPY', 'DIS', 'BX', '-json', '-likelihood',
     '-start', settings.START_STR, '-end', settings.END_STR], 4)
])
def test_cli_correlation_json_format_with_likelihood(args, length, capsys):
    with HTTMock(mock_data.mock_prices):
        with HTTMock(mock_data.mock_treasury):
            do_program(args)
    correl_matrix = json.loads(capsys.readouterr().out)
    # assert dimensions are correct length
    assert(len(correl_matrix['correlation_matrix']) == length)
    # assert all entries satisfy correlation bounds
    assert(all(all(bool((correl > -1 or correl == -1) and (correl < 1 or correl == 1))
                   for correl in correl_list) for correl_list in correl_matrix['correlation_matrix']))

# TODO: need mock dividend response to test cli

@pytest.mark.parametrize('args,tickers', [
    (
        ['risk-profile', 'ALLY', '-json', '-start', settings.START_STR, '-end', settings.END_STR],
        ['ALLY']
    ),
    (
        ['risk-profile', 'BX', 'DIS', '-json', '-start', settings.START_STR, '-end', settings.END_STR],
        ['BX', 'DIS']
    ),
    (
        ['risk-profile', 'SPY', 'BX', 'DIS', '-json', '-start', settings.START_STR, '-end', settings.END_STR],
        ['SPY', 'BX', 'DIS']
    )
])
def test_cli_risk_profile_json_format(args, tickers, capsys):
    with patch('scrilla.util.dater.get_last_trading_date') as date_function:
        date_function.return_value = settings.END
        with HTTMock(mock_data.mock_prices):
            with HTTMock(mock_data.mock_treasury):
                do_program(args)
    profile = json.loads(capsys.readouterr().out)
    profile_keys = [ key for key in keys.keys['STATISTICS'].values() if key not in ['conditional_value_at_risk', 'value_at_risk', 'correlation']]
    for ticker in tickers:
        for key in profile_keys:
            assert key in profile[ticker].keys()

@patch('scrilla.files.save_file')
@patch('scrilla.util.dater.get_last_trading_date')
@pytest.mark.parametrize('args,filename',[
    (
        ['risk-profile', 'ALLY', '-json', '-start', settings.START_STR, '-end', settings.END_STR, '-save', 'test_path'],
        'test_path'
    )
])
def test_cli_risk_profile_save_file(date_function, save_function, args, filename):
    date_function.return_value = settings.END
    with HTTMock(mock_data.mock_prices):
        with HTTMock(mock_data.mock_treasury):
            do_program(args)
    save_function.assert_called()
    save_function.assert_called_with(file_to_save=ANY, file_name=filename)

@pytest.mark.parametrize('args,tickers', [
    (
        ['cvar', 'ALLY', '-json', '-start', settings.START_STR, '-end', settings.END_STR],
        ['ALLY']
    ),
    (
        ['cvar', 'SPY', 'GLD', 'BX', 'ALLY', '-json', '-start', settings.START_STR, '-end', settings.END_STR],
        ['SPY', 'GLD', 'BX', 'ALLY',]
    ), 
])
def test_cli_cvar_json_format(args, tickers, capsys):
    with HTTMock(mock_data.mock_prices):
        with HTTMock(mock_data.mock_treasury):
            do_program(args)
    cvar = json.loads(capsys.readouterr().out)
    for ticker in tickers:
        assert keys.keys['STATISTICS']['CVAR'] in cvar[ticker].keys()

@pytest.mark.parametrize('args,ticker',[
    (['close', 'ALLY', '-json'], 'ALLY')
])
def test_cli_close_price_json_format(args, ticker, capsys):
    with patch('scrilla.util.dater.this_date_or_last_trading_date') as date_function:
        date_function.return_value = settings.END
        with HTTMock(mock_data.mock_prices):
            with HTTMock(mock_data.mock_treasury):
                do_program(args)
    prices = json.loads(capsys.readouterr().out)
    assert prices.get(ticker) is not None
    assert isinstance(prices[ticker], float)


@pytest.mark.parametrize('args,ticker,expected',[
    (['asset', 'ALLY'], 'ALLY', 'equity'),
    (['asset', 'BX'],'BX', 'equity'),
    (['asset', 'BTC'],'BTC', 'crypto'),
    (['asset', 'ETH'], 'ETH', 'crypto')
])
def test_cli_asset_type(args, ticker, expected, capsys):
    do_program(args)
    result = capsys.readouterr().out
    assert ticker in result
    assert expected in result

@pytest.mark.parametrize('args,tickers',[
    (
        ['var', 'ALLY', '-start', settings.START_STR, '-end', settings.END_STR, '-json', '-prob', '0.05', '-expiry', '0.5'], 
        ['ALLY']
    ),
    (
        ['var', 'GLD', 'SPY', '-start', settings.START_STR, '-end', settings.END_STR, '-json', '-prob', '0.05', '-expiry', '0.5'], 
        ['GLD', 'SPY']
    ),
    (
        ['var', 'DIS', 'BX', 'GLD', 'SPY', '-start', settings.START_STR, '-end', settings.END_STR, '-json', '-prob', '0.05', '-expiry', '0.5'], 
        ['DIS', 'BX', 'GLD', 'SPY']
    )
])
def test_cli_value_at_risk_json_format(args, tickers, capsys):
    with HTTMock(mock_data.mock_prices):
        with HTTMock(mock_data.mock_treasury):
            do_program(args)
    results = json.loads(capsys.readouterr().out)
    for ticker in tickers:
        assert ticker in list(results.keys())
        assert keys.keys['STATISTICS']['VAR'] in list(results[ticker].keys())
        assert isinstance(results[ticker][keys.keys['STATISTICS']['VAR']], float)

@pytest.mark.parametrize('args,tickers',[
    (
        ['cvar', 'ALLY', '-start', settings.START_STR, '-end', settings.END_STR, '-json', '-prob', '0.05', '-expiry', '0.5'], 
        ['ALLY']
    ),
    (
        ['cvar', 'GLD', 'SPY', '-start', settings.START_STR, '-end', settings.END_STR, '-json', '-prob', '0.05', '-expiry', '0.5'], 
        ['GLD', 'SPY']
    ),
    (
        ['cvar', 'DIS', 'BX', 'GLD', 'SPY', '-start', settings.START_STR, '-end', settings.END_STR, '-json', '-prob', '0.05', '-expiry', '0.5'], 
        ['DIS', 'BX', 'GLD', 'SPY']
    )
])
def test_cli_conditional_value_at_risk_json_format(args, tickers, capsys):
    with HTTMock(mock_data.mock_prices):
        with HTTMock(mock_data.mock_treasury):
            do_program(args)
    results = json.loads(capsys.readouterr().out)
    for ticker in tickers:
        assert ticker in list(results.keys())
        assert keys.keys['STATISTICS']['CVAR'] in list(results[ticker].keys())
        assert isinstance(results[ticker][keys.keys['STATISTICS']['CVAR']], float)