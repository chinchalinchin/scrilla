import os
import json

from httmock import urlmatch

from scrilla.files import load_file

from . import settings as test_settings

@urlmatch(netloc=r'(.*\.)?alphavantage\.co*$')
def mock_prices(url, request):
    if 'ALLY' in request.url:
        return json.dumps(load_file(os.path.join(test_settings.MOCK_DIR, 'ally_response.json')))
    elif 'BX' in request.url:
        return json.dumps(load_file(os.path.join(test_settings.MOCK_DIR, 'bx_response.json')))
    elif 'DIS' in request.url:
        return json.dumps(load_file(os.path.join(test_settings.MOCK_DIR, 'dis_response.json')))
    elif 'SPY' in request.url:
        return json.dumps(load_file(os.path.join(test_settings.MOCK_DIR, 'spy_response.json')))
    elif 'GLD' in request.url:
        return json.dumps(load_file(os.path.join(test_settings.MOCK_DIR, 'gld_response.json')))
    elif 'BTC' in request.url:
        return json.dumps(load_file(os.path.join(test_settings.MOCK_DIR, 'btc_response.json')))
    elif 'ALGO' in request.url:
        return json.dumps(load_file(os.path.join(test_settings.MOCK_DIR, 'algo_response.json')))
    raise KeyError('No mock data for request!')

@urlmatch(netloc=r'(.*\.)?quandl\.com*$')
def mock_interest(url, request):
    return json.dumps(load_file(os.path.join(test_settings.MOCK_DIR, 'yield_response.json')))