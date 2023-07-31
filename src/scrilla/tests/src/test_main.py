import pytest
import json
from unittest.mock import patch, ANY

from httmock import HTTMock

from scrilla import settings as app_settings
from scrilla.main import do_program
from scrilla.cache import PriceCache, ProfileCache, InterestCache, CorrelationCache
from scrilla.files import clear_cache, init_static_data
from scrilla.static import keys, definitions
from scrilla.util.errors import InputValidationError, ModelError

from .. import mock_data, settings

init_static_data()

@pytest.fixture(autouse=True)
def reset_cache():
    clear_cache(mode='sqlite')
    PriceCache(mode='sqlite'), ProfileCache(mode='sqlite')
    InterestCache(mode='sqlite'), CorrelationCache(mode='sqlite')


def test_cli_general_help_msg(capsys):
    do_program(['help'])
    help_message = capsys.readouterr().out
    for definition in definitions.FUNC_DICT.values():
        assert definition['name'] in help_message
        assert all(val in help_message for val in definition['values'])

@pytest.mark.parametrize('args', [
    ['help', 'cor'],
    ['help', 'risk-profile'],
    ['help', 'ddm']
])
def test_cli_specific_help_msg(args, capsys):
    do_program(args)
    help_message = capsys.readouterr().out
    for definition in definitions.FUNC_DICT.values():
        if args[1] in definition['values']:
            assert definition['name'] in help_message
            assert all(val in help_message for val in definition['values'])

@patch('scrilla.files.os.remove')
def test_cli_clear_cache_sqlite_mode(delete_function):
    do_program(['clear-cache'])
    delete_function.assert_called()
    delete_function.assert_called_with(app_settings.CACHE_SQLITE_FILE)

# TODO: patching the os.environ dictionary doesn't work
#       need some way to override CACHE_MODE to test this...
# @patch('os.environ', { 'CACHE_MODE': 'dynamodb' })
# @patch('scrilla.cloud.aws.dynamo_drop_table')
# def test_clear_cache_dynamodb_mode(delete_function, environment):
#     environment.return_value = 'dynamodb'
#     do_program(['clear-cache'])
#     delete_function.assert_called()
#     delete_function.asset_called_with(['prices', 'interest', 'correlations', 'profile'])

@patch('scrilla.files.os.remove')
def test_cli_clear_static(delete_function):
    do_program(['clear-static'])
    delete_function.assert_called()
    delete_function.assert_called_with(ANY)
    # TODO: expand coverage here once this is answersed:
    #       https://stackoverflow.com/questions/72818706/python-assert-mock-function-was-called-with-a-string-containing-another-string

@patch('scrilla.files.os.remove')
def test_cli_clear_common(delete_function):
    do_program(['clear-common'])
    delete_function.assert_called()
    delete_function.assert_called_with(ANY)

@patch('scrilla.files.os.remove')
def test_cli_purge(delete_function):
    do_program(['purge'])
    delete_function.assert_called()
    delete_function.assert_called_with(ANY)

def test_cli_verison(capsys):
    do_program(['version'])
    version_text = capsys.readouterr().out
    version_array = version_text.split('.')
    for part in version_array:
        assert part.strip().isnumeric()
    assert len(version_array) == 3

def test_cli_yield_curve_json_format(capsys):
    with HTTMock(mock_data.mock_treasury):
        do_program(['yield-curve', '-json', '-start', settings.START_STR])
    rates = json.loads(capsys.readouterr().out)
    assert all(rates.get(maturity) is not None for maturity in keys.keys['YIELD_CURVE'])


@pytest.mark.parametrize('args, length', [
    (['correlation', 'ALLY', 'BX', '-json', '-start',
     settings.START_STR, '-end', settings.END_STR], 2),
    (['correlation', 'BTC', 'SPY', 'GLD', '-json', '-start',
     settings.START_STR, '-end', settings.END_STR], 3),
    (['correlation', 'GLD', 'SPY', 'DIS', 'BX', '-json',
     '-start', settings.START_STR, '-end', settings.END_STR], 4)
])
def test_cli_correlation_json_format(args, length, capsys):
    with HTTMock(mock_data.mock_prices), \
         HTTMock(mock_data.mock_treasury):
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
    with HTTMock(mock_data.mock_prices), \
         HTTMock(mock_data.mock_treasury):
            do_program(args)
    correl_matrix = json.loads(capsys.readouterr().out)
    # assert dimensions are correct length
    assert(len(correl_matrix['correlation_matrix']) == length)
    # assert all entries satisfy correlation bounds
    assert(all(all(bool((correl > -1 or correl == -1) and (correl < 1 or correl == 1))
                   for correl in correl_list) for correl_list in correl_matrix['correlation_matrix']))


@pytest.mark.parametrize('args,length',[
    (['correlation', 'ALLY', 'BX', '-json', '-likelihood',
     '-start', settings.START_STR, '-end', settings.END_STR], 2),
    (['correlation', 'BTC', 'SPY', 'GLD', '-json', '-likelihood',
     '-start', settings.START_STR, '-end', settings.END_STR], 3),
    (['correlation', 'GLD', 'SPY', 'DIS', 'BX', '-json', '-likelihood',
     '-start', settings.START_STR, '-end', settings.END_STR], 4)
])
def test_cli_correlation_json_format_with_percentiles(args, length, capsys):
    with HTTMock(mock_data.mock_prices),\
         HTTMock(mock_data.mock_treasury):
            do_program(args)
    correl_matrix = json.loads(capsys.readouterr().out)
    # assert dimensions are correct length
    assert(len(correl_matrix['correlation_matrix']) == length)
    # assert all entries satisfy correlation bounds
    assert(all(all(bool((correl > -1 or correl == -1) and (correl < 1 or correl == 1))
                   for correl in correl_list) for correl_list in correl_matrix['correlation_matrix']))

@patch('scrilla.files.save_file')
@pytest.mark.parametrize('args,filename',[
    (['correlation', 'ALLY', 'BX', '-likelihood', '-start', settings.START_STR, '-end', settings.END_STR, 
        '-save', 'test_path'], 'test_path'),
])
def test_cli_correlation_save_file(save_function, args, filename):
    with HTTMock(mock_data.mock_prices),\
         HTTMock(mock_data.mock_treasury):
            do_program(args)
    save_function.assert_called()
    save_function.assert_called_with(file_to_save=ANY, file_name=filename)


@patch('scrilla.util.dater.get_last_trading_date')
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
def test_cli_risk_profile_json_format(date_function, args, tickers, capsys):
    date_function.return_value = settings.END
    with HTTMock(mock_data.mock_prices), \
         HTTMock(mock_data.mock_treasury):
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
    with HTTMock(mock_data.mock_prices), \
         HTTMock(mock_data.mock_treasury):
            do_program(args)
    save_function.assert_called()
    save_function.assert_called_with(file_to_save=ANY, file_name=filename)


@patch('scrilla.util.dater.this_date_or_last_trading_date')
@pytest.mark.parametrize('args,ticker',[
    (['close', 'ALLY', '-json'], 'ALLY')
])
def test_cli_close_price_json_format(date_function, args, ticker, capsys):
    date_function.return_value = settings.END
    with HTTMock(mock_data.mock_prices), \
         HTTMock(mock_data.mock_treasury):
            do_program(args)
    prices = json.loads(capsys.readouterr().out)
    assert prices.get(ticker) is not None
    assert isinstance(prices[ticker], float)

@patch('scrilla.files.save_file')
@patch('scrilla.util.dater.this_date_or_last_trading_date')
@pytest.mark.parametrize('args,filename',[
    (['close', 'ALLY', '-json', '-save', 'test_path'], 'test_path')
])
def test_cli_close_price_save_file(date_function, save_function, args, filename):
    date_function.return_value = settings.END
    with HTTMock(mock_data.mock_prices), \
         HTTMock(mock_data.mock_treasury):
            do_program(args)
    save_function.assert_called()
    save_function.assert_called_with(file_to_save=ANY, file_name=filename)

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
        ['var', 'ALLY', '-start', settings.START_STR, '-end', settings.END_STR, 
            '-json', '-prob', '0.05', '-expiry', '0.5'], 
        ['ALLY']
    ),
    (
        ['var', 'GLD', 'SPY', '-start', settings.START_STR, '-end', settings.END_STR, 
            '-json', '-prob', '0.05', '-expiry', '0.5'], 
        ['GLD', 'SPY']
    ),
    (
        ['var', 'DIS', 'BX', 'GLD', 'SPY', '-start', settings.START_STR, '-end', settings.END_STR, 
            '-json', '-prob', '0.05', '-expiry', '0.5'], 
        ['DIS', 'BX', 'GLD', 'SPY']
    )
])
def test_cli_value_at_risk_json_format(args, tickers, capsys):
    with HTTMock(mock_data.mock_prices), \
         HTTMock(mock_data.mock_treasury):
            do_program(args)
    results = json.loads(capsys.readouterr().out)
    for ticker in tickers:
        assert ticker in list(results.keys())
        assert keys.keys['STATISTICS']['VAR'] in list(results[ticker].keys())
        assert isinstance(results[ticker][keys.keys['STATISTICS']['VAR']], float)

@patch('scrilla.files.save_file')
@pytest.mark.parametrize('args,filename',[
    (
        ['var', 'ALLY', '-start', settings.START_STR, '-end', settings.END_STR, 
            '-json', '-prob', '0.05', '-expiry', '0.5', '-save', 'test_path'], 
        'test_path'
    ),
])
def test_cli_value_at_risk_save_file(save_function, args, filename):
    with HTTMock(mock_data.mock_prices), \
         HTTMock(mock_data.mock_treasury):
            do_program(args)
    save_function.assert_called()
    save_function.assert_called_with(file_to_save=ANY, file_name=filename)

@pytest.mark.parametrize('args,tickers',[
    (
        ['cvar', 'ALLY', '-start', settings.START_STR, '-end', settings.END_STR, 
            '-json', '-prob', '0.05', '-expiry', '0.5'], 
        ['ALLY']
    ),
    (
        ['cvar', 'GLD', 'SPY', '-start', settings.START_STR, '-end', settings.END_STR, 
            '-json', '-prob', '0.05', '-expiry', '0.5'], 
        ['GLD', 'SPY']
    ),
    (
        ['cvar', 'DIS', 'BX', 'GLD', 'SPY', '-start', settings.START_STR, '-end', settings.END_STR, 
            '-json', '-prob', '0.05', '-expiry', '0.5'], 
        ['DIS', 'BX', 'GLD', 'SPY']
    )
])
def test_cli_conditional_value_at_risk_json_format(args, tickers, capsys):
    with HTTMock(mock_data.mock_prices), \
         HTTMock(mock_data.mock_treasury):
            do_program(args)
    results = json.loads(capsys.readouterr().out)
    for ticker in tickers:
        assert ticker in list(results.keys())
        assert keys.keys['STATISTICS']['CVAR'] in list(results[ticker].keys())
        assert isinstance(results[ticker][keys.keys['STATISTICS']['CVAR']], float)

@patch('scrilla.files.save_file')
@pytest.mark.parametrize('args,filename',[
    (
        ['cvar', 'ALLY', '-json', '-start', settings.START_STR, '-end', settings.END_STR,
             '-save', 'test_path', '-prob', '0.05', '-expiry', '0.5'], 
        'test_path'
    ),
])
def test_cli_conditional_value_at_risk_save_file(save_function, args, filename):
    with HTTMock(mock_data.mock_prices), \
         HTTMock(mock_data.mock_treasury):
            do_program(args)
    save_function.assert_called()
    save_function.assert_called_with(file_to_save=ANY, file_name=filename)

@patch('scrilla.util.dater.get_last_trading_date')
@pytest.mark.parametrize('args,tickers', [
    (
        ['capm-equity', 'ALLY', '-start', settings.START_STR, '-end', settings.END_STR, 
            '-json'],
        ['ALLY']
    ),
    (
        ['capm-equity', 'ALLY', 'BX', '-start', settings.START_STR, '-end', settings.END_STR, 
            '-json'],
        ['ALLY', 'BX']
    ),
])
def test_cli_cost_of_equity_json_format(date_function, args, tickers, capsys):
    date_function.return_value = settings.END
    with HTTMock(mock_data.mock_prices), \
         HTTMock(mock_data.mock_treasury):
            do_program(args)
    costs = json.loads(capsys.readouterr().out)
    for ticker in tickers:
        assert costs.get(ticker) is not None
        assert costs[ticker].get(keys.keys['STATISTICS']['EQUITY']) is not None
        assert isinstance(costs[ticker][keys.keys['STATISTICS']['EQUITY']], float)

@patch('scrilla.util.dater.get_last_trading_date')
@patch('scrilla.files.save_file')
@pytest.mark.parametrize('args,filename', [
    (
        ['capm-equity', 'ALLY', '-start', settings.START_STR, '-end', settings.END_STR, 
            '-json', '-save', 'test_path'],
        'test_path'
    )
])
def test_cli_cost_of_equity_save_file(save_function, date_function, args, filename):
    date_function.return_value = settings.END
    with HTTMock(mock_data.mock_prices), \
         HTTMock(mock_data.mock_treasury):
            do_program(args)
    save_function.assert_called()
    save_function.assert_called_with(file_to_save=ANY, file_name=filename)

@pytest.mark.parametrize('args,tickers', [
    (
        ['capm-beta', 'ALLY', '-start', settings.START_STR, '-end', settings.END_STR, 
            '-json'],
        ['ALLY']
    ),
    (
        ['capm-beta', 'ALLY', 'BX', '-start', settings.START_STR, '-end', settings.END_STR, 
            '-json'],
        ['ALLY', 'BX']
    ),
])
def test_cli_asset_beta_json_format(args, tickers, capsys):
    with HTTMock(mock_data.mock_prices), \
         HTTMock(mock_data.mock_treasury):
            do_program(args)
    costs = json.loads(capsys.readouterr().out)
    for ticker in tickers:
        assert costs.get(ticker) is not None
        assert costs[ticker].get(keys.keys['STATISTICS']['BETA']) is not None
        assert isinstance(costs[ticker][keys.keys['STATISTICS']['BETA']], float)

@patch('scrilla.files.save_file')
@pytest.mark.parametrize('args,filename', [
    (
        ['capm-beta', 'ALLY', '-start', settings.START_STR, '-end', settings.END_STR, 
            '-json', '-save', 'test_path'],
        'test_path'
    )
])
def test_cli_asset_beta_save_file(save_function, args, filename):
    with HTTMock(mock_data.mock_prices),\
         HTTMock(mock_data.mock_treasury):
            do_program(args)
    save_function.assert_called()
    save_function.assert_called_with(file_to_save=ANY, file_name=filename)

@patch('scrilla.analysis.markets.cost_of_equity')
@pytest.mark.parametrize('args,tickers', [
    (['ddm','ALLY', '-json'], ['ALLY']),
    (['ddm','ALLY','-discount', '0.05', '-json'], ['ALLY']),
    (['ddm', 'ALLY', 'BX', '-json'], ['ALLY', 'BX'])
])
def test_cli_discount_dividend_model_json_format(equity_function, args, tickers, capsys):
    equity_function.return_value = 0.05
    with HTTMock(mock_data.mock_prices), \
         HTTMock(mock_data.mock_dividends):
            do_program(args)
    ddm_price = json.loads(capsys.readouterr().out)
    for ticker in tickers:
        assert ddm_price.get(ticker) is not None
        assert ddm_price[ticker].get(keys.keys['MODELS']['DDM']) is not None
        assert isinstance(ddm_price[ticker][keys.keys['MODELS']['DDM']], float)

@pytest.mark.parametrize('args', [
    (['ddm','ALLY','-discount', '-0.05'])
])
def test_cli_discount_dividend_model_bad_args(args):
    with pytest.raises(Exception) as model_error, \
         HTTMock(mock_data.mock_prices), \
         HTTMock(mock_data.mock_dividends):
                do_program(args)
    assert model_error.type == ModelError

@pytest.mark.parametrize('args, tickers',[
    (['dividends', 'ALLY', '-json'], ['ALLY']),
    (['dividends', 'ALLY', 'BX', '-json'], ['ALLY', 'BX'])
])
def test_cli_dividend_history_json_format(args, tickers, capsys):
    with HTTMock(mock_data.mock_dividends):
        do_program(args)
    histories = json.loads(capsys.readouterr().out)
    assert all(ticker in list(histories.keys()) for ticker in tickers)
    assert all(isinstance(histories[ticker], dict) for ticker in tickers)

@pytest.mark.parametrize('args,tickers',[
    (['efficient-frontier', 'ALLY', 'DIS','BX','-start', settings.START_STR, 
        '-end', settings.END_STR, '-json'], 
     ['ALLY','BX','DIS']),
    (['efficient-frontier', 'GLD', 'BTC', 'SPY','-start', settings.START_STR,
        '-end', settings.END_STR, '-json', '-sh'], 
     ['GLD', 'BTC', 'SPY']),
     (['efficient-frontier', 'ALLY', 'DIS','BX', 'GLD', 'BTC', 'SPY','-start', settings.START_STR,
        '-end', settings.END_STR, '-json', '-sh'], 
     ['ALLY', 'DIS','BX', 'GLD', 'BTC', 'SPY']),
])
def test_cli_efficient_frontier_json_format(args, tickers, capsys):
    with HTTMock(mock_data.mock_prices), \
         HTTMock(mock_data.mock_treasury):
         do_program(args)
    frontiers = json.loads(capsys.readouterr().out)
    assert len(frontiers) == app_settings.FRONTIER_STEPS
    for frontier in frontiers:
        assert frontier.get('holdings') is not None
        assert len(frontier['holdings']) == len(tickers)
        assert frontier.get('portfolio_return') is not None
        assert isinstance(frontier['portfolio_return'], float)
        assert frontier.get('portfolio_volatility') is not None
        assert isinstance(frontier['portfolio_volatility'], float)
        assert frontier['portfolio_volatility'] > 0


@pytest.mark.parametrize('args',[
    (['max-return', 'ALLY', 'BX', 'DIS', '-start', settings.START_STR, '-end', settings.END_STR, '-json']),
])
def test_cli_maximize_portfolio_no_investment_json_format(args, capsys):
    with HTTMock(mock_data.mock_prices), \
         HTTMock(mock_data.mock_treasury):
        do_program(args)
    portfolio = json.loads(capsys.readouterr().out)
    # TODO: finish
    pass