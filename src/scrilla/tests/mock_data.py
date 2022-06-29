import os
import json

from httmock import urlmatch

from scrilla import settings
from scrilla.files import load_file
from scrilla.util.outputter import Logger

from . import settings as test_settings

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
    (120, 122, 0.15, 0.03, 0.793650793650794, -0.012335118691085),
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
    (120, 0.15, 0.03, 0.793650793650794, 0.75, 133.287064146056),
    (25, 0.15, 0.05, 0.476190476190476, 0.6, 26.142232822269),
    (57.43, 0.22, 0.03, 0.238095238095238, 0.99, 73.8236324949752),
    (330, 0.111, 0.041, 1.25, 0.35, 328.59404283136),
    (155, 0.08, 0.03, 1.46825396825397, 0.15, 145.810137542904)
]

service_price_cases = [
    ('BX', '2021-10-29', '2021-11-05'),
    ('ALLY', '2021-08-04', '2021-09-10'),
    ('BTC', '2021-03-10', '2021-04-12'),
    ('SPY', '2020-01-03', '2020-03-15'),
    ('ALGO', '2019-11-15', '2020-05-15'),
    ('DIS', '2020-01-02', '2020-12-31')
]

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

# (ticker, prices, expected, query_results)
price_internal_cache_case_query_results = (*price_internal_cache_case, 
    [
        ['2020-01-10',51,53],
        ['2020-01-09', 50, 11],
        ['2020-01-04', 49, 12.4],
        ['2020-01-02', 52,12]
    ]
)

price_cache_to_param_case = (
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

price_cache_to_dict_dynamodb_case = (
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

# (rates, expected)
interest_internal_cache_case = (
    {
        '2020-01-01': [0.01, 0.02, 0.03, 0.04, 0.05, 0.06, 0.07, 0.08, 0.09, 0.10, 0.11, 0.12],
        '2020-01-02': [0.02, 0.03, 0.04, 0.05, 0.06, 0.07, 0.08, 0.09, 0.10, 0.11, 0.12, 0.13],
    },
    [
        { '2020-01-01': 0.01 },
        { '2020-01-01': 0.02 },
        { '2020-01-01': 0.03 },
        { '2020-01-01': 0.04 },
        { '2020-01-01': 0.05 },
        { '2020-01-01': 0.06 },
        { '2020-01-01': 0.07 },
        { '2020-01-01': 0.08 },
        { '2020-01-01': 0.09 },
        { '2020-01-01': 0.10 },
        { '2020-01-01': 0.11 },
        { '2020-01-01': 0.12 },
        { '2020-01-02': 0.02 },
        { '2020-01-02': 0.03 },
        { '2020-01-02': 0.04 },
        { '2020-01-02': 0.05 },
        { '2020-01-02': 0.06 },
        { '2020-01-02': 0.07 },
        { '2020-01-02': 0.08 },
        { '2020-01-02': 0.09 },
        { '2020-01-02': 0.10 },
        { '2020-01-02': 0.11 },
        { '2020-01-02': 0.12 },
        { '2020-01-02': 0.13 },
    ]
)

# (maturity, rates, expected, query_results)
interest_internal_cache_case_query_results=(
    'ONE_YEAR',
    interest_internal_cache_case[0],
    [
        {
            '2020-01-01':0.05
        },
        {
            '2020-01-02': 0.06
        }
    ],
    [
        ['2020-01-01', 0.05],
        ['2020-01-02', 0.06]
    ]
)

# (rates, expected)
interest_cache_to_param_case = (
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

interest_cache_to_dict_dynamodb_case=(
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
)


def load_test_file(file, extension = 'json'):
    if extension == 'json':
        return json.dumps(load_file(os.path.join(test_settings.MOCK_DIR, file)))
    return load_file(os.path.join(test_settings.MOCK_DIR), file)

@urlmatch(netloc=r'(.*\.)?alphavantage\.co*$')
def mock_prices(url, request):
    if 'ALLY' in request.url:
        return load_test_file('ally_response.json')
    elif 'BX' in request.url:
        return load_test_file('bx_response.json')
    elif 'DIS' in request.url:
        return load_test_file('dis_response.json')
    elif 'SPY' in request.url:
        return load_test_file( 'spy_response.json')
    elif 'GLD' in request.url:
        return load_test_file('gld_response.json')
    elif 'BTC' in request.url:
        return load_test_file('btc_response.json')
    elif 'ALGO' in request.url:
        return load_test_file('algo_response.json')
    raise KeyError('No mock data for request!')


@urlmatch(netloc=r'(.*\.)?quandl\.com*$')
def mock_quandl(url, request):
    return load_test_file('yield_response.json')

@urlmatch(netloc=r'(.*\.)?home\.treasury\.gov*$')
def mock_treasury(url, request):
    return load_test_file('treasury_response', 'xml')

@urlmatch(netloc=r'(.*\.)?cloud\.iexapis\.com*$')
def mock_dividends(url, request):
    if 'ALLY' in request.url:
        return load_test_file('ally_div_response.json')
    elif 'BX' in request.url:
        return load_test_file('bx_div_response.json')
    elif 'DIS' in request.url:
        return load_file('dis_div_response.json')