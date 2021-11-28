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

bs_d1_cases = [
    (120, 122, 0.15, 0.03, 0.793650793650794, 0.121295502265128),
    (25, 30, 0.15, 0.05, 0.476190476190476, -1.47961680890385),
    (57.43, 50, 0.22, 0.03, 0.238095238095238, 1.41080550384298),
    (330, 400, 0.111, 0.041, 1.25, -1.07509558235642),
    (155, 162, 0.08, 0.03, 1.46825396825397, 0.047193567590656)
]

bs_d2_cases = [
    (120, 122, 0.15, 0.03, 0.793650793650794,-0.012335118691085),
    (25, 30, 0.15, 0.05, 0.476190476190476, -1.58312664280521),
    (57.43, 50, 0.22, 0.03, 0.238095238095238, 1.30345649581864),
    (330, 400, 0.111, 0.041, 1.25, -1.19919735510765),
    (155, 162, 0.08, 0.03, 1.46825396825397, -0.049743656409341)
]

bs_prob_d1_cases = [
    (120, 122, 0.15, 0.03, 0.793650793650794, 0.548271508805581),
    (25, 30, 0.15, 0.05, 0.476190476190476, 0.069487769054048),
    (57.43, 50, 0.22, 0.03, 0.238095238095238, 0.920849014407477),
    (330, 400, 0.111, 0.041, 1.25, 0.141165968553501),
    (155, 162, 0.08, 0.03, 1.46825396825397, 0.518820522934644)
]

bs_prob_d2_cases = [
    (120, 122, 0.15, 0.03, 0.793650793650794, 0.495079124410103),
    (25, 30, 0.15, 0.05, 0.476190476190476, 0.056696301070295),
    (57.43, 50, 0.22, 0.03, 0.238095238095238, 0.903790520239976),
    (330, 400, 0.111, 0.041, 1.25, 0.11522560773558),
    (155, 162, 0.08, 0.03, 1.46825396825397, 0.480163333358691)
]

bs_percentile_cases = [
    (120, 0.15, 0.03, 0.793650793650794, 0.75,133.287064146056),
    (25, 0.15, 0.05, 0.476190476190476, 0.6,26.142232822269),
    (57.43, 0.22, 0.03, 0.238095238095238, 0.99,73.8236324949752),
    (330, 0.111, 0.041, 1.25, 0.35,328.59404283136),
    (155, 0.08, 0.03, 1.46825396825397, 0.15,145.810137542904)
]

service_price_cases = [
    ('ALLY', '2021-11-12', '2021-11-12'),
    ('BX', '2021-10-29', '2021-11-05'),
    ('ALLY', '2021-08-04','2021-09-10'),
    ('BTC', '2021-03-10', '2021-04-12'),
    ('SPY', '2020-01-03', '2020-03-15'),
    ('ALGO', '2019-11-15', '2020-05-15'),
    ('DIS', '2020-01-02', '2020-12-31')
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

@urlmatch(netloc=r'(.*\.)?cloud\.iexapis\.com*$')
def mock_dividends(url, request):
    if 'ALLY' in request.url:
        return json.dumps(load_file(os.path.join(test_settings.MOCK_DIR, 'ally_div_response.json')))
    elif 'BX' in request.url:
        return json.dumps(load_file(os.path.join(test_settings.MOCK_DIR, 'bx_div_response.json')))
    elif 'DIS' in request.url:
        return json.dumps(load_file(os.path.join(test_settings.MOCK_DIR, 'dis_div_response.json')))
