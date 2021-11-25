import os
import json

from httmock import urlmatch

from scrilla import settings
from scrilla.files import load_file
from scrilla.util.outputter import Logger

from . import settings as test_settings

logger = Logger("tests.mock", settings.LOG_LEVEL)

univariate_data = {
    'case_1': [16, -12, -17, 1, -3, -4, 17, 0, -14, 16],
    'case_2':  [53, 73, 49, 3, 2, 24, 29, 69, 24, 96],
    'case_3': [73, 71, 3, 4, 42, 52, 34, 32, 21, 39],
    'case_4': [77, 74, 64, 49, 31, 7, 35, 46, 15, 70],
    'case_5': [21, 8, 30, 62, 47, 29, 38, 71, 78, 7]
}
recursive_univariate_data = [
    (univariate_data['case_1'][:-1], univariate_data['case_1'][1:]),
    (univariate_data['case_2'][:-1], univariate_data['case_2'][1:]),
    (univariate_data['case_3'][:-1], univariate_data['case_3'][1:]),
    (univariate_data['case_4'][:-1], univariate_data['case_4'][1:]),
    (univariate_data['case_5'][:-1], univariate_data['case_5'][1:]),
]
bivariate_data = {
    'case_1': (univariate_data['case_1'], univariate_data['case_2']),
    'case_2': (univariate_data['case_1'], univariate_data['case_3']),
    'case_3': (univariate_data['case_1'], univariate_data['case_4']),
    'case_4': (univariate_data['case_1'], univariate_data['case_5'])
}

mean_cases = [
    (univariate_data['case_1'], 0),
    (univariate_data['case_2'], 42.2),
    (univariate_data['case_3'], 37.1),
    (univariate_data['case_4'],  46.8),
    (univariate_data['case_5'],  39.1),
]
variance_cases = [
    (univariate_data['case_1'], 161.777777777778),
    (univariate_data['case_2'], 968.177777777778),
    (univariate_data['case_3'], 582.322222222222),
    (univariate_data['case_4'],  608.4),
    (univariate_data['case_5'],  625.433333333333),
]
covariance_cases = [
    (bivariate_data['case_1'][0],
     bivariate_data['case_1'][1], 81.4444444444444),
    (bivariate_data['case_2'][0],
     bivariate_data['case_2'][1], 93.6666666666667),
    (bivariate_data['case_3'][0],
     bivariate_data['case_3'][1], 76.5555555555556),
    (bivariate_data['case_4'][0],
     bivariate_data['case_4'][1], -88.7777777777778),
]
correlation_cases = [
    (bivariate_data['case_1'][0],
     bivariate_data['case_1'][1], 0.205790099581043),
    (bivariate_data['case_2'][0],
     bivariate_data['case_2'][1], 0.305171484680075),
    (bivariate_data['case_3'][0],
     bivariate_data['case_3'][1], 0.244018457215175),
    (bivariate_data['case_4'][0],
     bivariate_data['case_4'][1], -0.279096458172889),

]
# alpha, beta
regression_cases = [
    (bivariate_data['case_1'][0], bivariate_data['case_1']
     [1], 42.2, 0.503434065934066),
    (bivariate_data['case_2'][0], bivariate_data['case_2']
     [1], 37.1, 0.578983516483516),
    (bivariate_data['case_3'][0], bivariate_data['case_3']
     [1], 46.8, 0.473214285714286),
    (bivariate_data['case_4'][0], bivariate_data['case_4']
     [1], 39.1, -0.548763736263736),
]

@urlmatch(netloc=r'(.*\.)?alphavantage\.co*$')
def mock_prices(url, request):
    logger.info('Returning mock AlphaVantage data')
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
    logger.info('Returning mock Quandl data')
    return json.dumps(load_file(os.path.join(test_settings.MOCK_DIR, 'yield_response.json')))
