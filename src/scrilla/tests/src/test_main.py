import pytest
import json

from httmock import HTTMock

from scrilla.main import do_program
from scrilla.cache import PriceCache, ProfileCache, InterestCache, CorrelationCache
from scrilla.files import clear_cache, init_static_data

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
    assert(len(correl_matrix) == length)
    # assert all entries satisfy correlation bounds
    assert(all(all(bool((correl > -1 or correl == -1) and (correl < 1 or correl == 1))
           for correl in correl_list) for correl_list in correl_matrix))


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
    assert(len(correl_matrix) == length)
    # assert all entries satisfy correlation bounds
    assert(all(all(bool((correl > -1 or correl == -1) and (correl < 1 or correl == 1))
                   for correl in correl_list) for correl_list in correl_matrix))

# TODO: need mock dividend response to test cli
