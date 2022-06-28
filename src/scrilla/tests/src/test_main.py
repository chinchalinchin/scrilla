import pytest
import json

from httmock import HTTMock
import ast

from scrilla.main import do_program
from scrilla.cache import PriceCache, ProfileCache, InterestCache, CorrelationCache
from scrilla.files import clear_cache, init_static_data
from scrilla.static import keys
from scrilla.util.outputter import risk_profile

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
        do_program(args)
    correl_matrix = json.loads(capsys.readouterr().out)
    # assert dimensions are correct length
    assert(len(correl_matrix['correlation_matrix']) == length)
    # assert all entries satisfy correlation bounds
    assert(all(all(bool((correl > -1 or correl == -1) and (correl < 1 or correl == 1))
                   for correl in correl_list) for correl_list in correl_matrix['correlation_matrix']))

# TODO: need mock dividend response to test cli

@pytest.mark.parametrize('args, tickers', [
    (
        ['risk-profile', 'ALLY', '-json', '-start', settings.START_STR, '-end', settings.END_STR],
        ['ALLY']
    ),
    (
        ['risk-profile', 'BX', 'DIS', '-json', '-start', settings.START_STR, '-end', settings.END_STR],
        ['BX', 'SONY']
    ),
    (
        ['risk-profile', 'SPY', 'BX', 'DIS', '-json', '-start', settings.START_STR, '-end', settings.END_STR],
        ['SPY', 'BX', 'DIS']
    )
])
def test_cli_risk_profile_json_format(args, tickers, capsys):
    with HTTMock(mock_data.mock_prices):
        do_program(args)
    profile = json.loads(capsys.readouterr().out)
    profile_keys = [ key for key in keys.keys['STATISTICS'].values() if key not in ['conditional_value_at_risk', 'value_at_risk']]
    for ticker in tickers:
        for key in profile_keys:
            assert key in profile[ticker].keys()

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
        do_program(args)
    cvar = json.loads(capsys.readouterr().out)
    for ticker in tickers:
        assert keys.keys['STATISTICS']['CVAR'] in cvar[ticker].keys()

@pytest.mark.parametrize('args,ticker',[
    (['close', 'ALLY', '-start', settings.START_STR, '-end', settings.END_STR, '-json'], 'ALLY')
])
def test_cli_close_price_json_format(args, ticker, capsys):
    with HTTMock(mock_data.mock_prices):
        do_program(args)
    prices = json.loads(capsys.readouterr().out)
    assert prices.get(ticker) is not None
    assert prices[ticker].get(settings.START_STR) is not None
    assert prices[ticker].get(settings.END_STR) is not None
    assert prices[ticker][settings.START_STR].get(keys.keys['PRICES']['OPEN']) is not None
    assert prices[ticker][settings.END_STR].get(keys.keys['PRICES']['CLOSE']) is not None