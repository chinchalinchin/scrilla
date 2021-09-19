# This file is part of scrilla: https://github.com/chinchalinchin/scrilla.

# scrilla is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 3
# as published by the Free Software Foundation.

# scrilla is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with scrilla.  If not, see <https://www.gnu.org/licenses/>
# or <https://github.com/chinchalinchin/scrilla/blob/develop/main/LICENSE>.

constants = {
    'ONE_TRADING_DAY': {
        'EQUITY': (1/252),
        'CRYPTO': (1/365)
    },
    'ACCURACY': 5,
    'BACKOFF_PERIOD': 30,
    'KEEP_FILE': '.gitkeep',
    'PRICE_YEAR_CUTOFF': 1950,
    'DENOMINATION': 'USD',
    'NPV_DELTA_TOLERANCE': 0.0000001,
    'OPTIMIZATION_METHOD': "SLSQP"
}
keys= {
    'PRICES': {
        'OPEN': 'open',
        'CLOSE': 'close'
    },
    'ESTIMATION': {
        'MOMENT': 'moments',
        'PERCENT': 'percents',
        'LIKE': 'likely'
    },
    'MODELS':{
        'GBM': 'geometric',
        'MEAN': 'reversion'
    },
    'YIELD_CURVE': ["ONE_MONTH", "TWO_MONTH", "THREE_MONTH", "SIX_MONTH", "ONE_YEAR", "TWO_YEAR", "THREE_YEAR", "FIVE_YEAR", "SEVEN_YEAR", "TEN_YEAR", "TWENTY_YEAR", "THIRTY_YEAR"],
    'STATISTICS': {
        'RETURN': 'annual_return',
        'VOLATILITY': 'annual_volatility',
        'BETA': 'asset_beta',
        'SHARPE': 'sharpe_ratio',
        'EQUITY': 'equity_cost',
        'CORRELATION': 'correlation'
    },
    'ASSETS':{
        'EQUITY': 'equity',
        'CRYPTO': 'crypto',
        'STAT': 'statistics',
        'BOND': 'bond'
    },
    'CACHE':{
        'PRICES': 'prices',
        'PROFILE': 'profile',
        'CORRELATION': 'correlation',
        'DIVIDENDS': 'dividends',
        'STATISTIC': 'statistic'
    },
    'PARAMETERS':{
        'TICKER': 'ticker',
        'TICKERS': 'tickers',
        'START':'start_date',
        'END':'end_date'
    },
    'SERVICES':{
        'PRICES':{
            'ALPHA_VANTAGE': {
                'MANAGER': 'alpha_vantage',
                'MAP': {
                    'KEYS':{
                        'EQUITY':{
                            'FIRST_LAYER': 'Time Series (Daily)',
                            'CLOSE': '4. close',
                            'OPEN': '1. open',
                            'HEADER': 'symbol'
                        },
                        'CRYPTO': {
                            'FIRST_LAYER' : 'Time Series (Digital Currency Daily)',
                            'CLOSE': f'4a. close ({constants["DENOMINATION"]})',
                            'OPEN': f'1a. open ({constants["DENOMINATION"]})',
                            'HEADER': 'currency code'
                        },
                        'ERROR': 'Error Message',
                        'THROTTLE': 'Note',
                        'LIMIT': 'Information'
                    },
                    'PARAMS':{
                        'TICKER': 'symbol',
                        'FUNCTION': 'function',
                        'DENOMINATION': 'market',
                        'KEY': 'apikey',
                        'SIZE': 'outputsize'
                    },
                    'ARGUMENTS': {
                        'EQUITY_DAILY': 'TIME_SERIES_DAILY',
                        'LISTING': 'LISTING_STATUS',
                        'CRYPTO_DAILY': 'DIGITAL_CURRENCY_DAILY',
                        'FULL': 'full'
                    }
                }
            }
        },
        'STATISTICS': {
            'QUANDL': {
                'MANAGER': 'quandl',
                'MAP':{
                    'PATHS':{
                        'FRED': 'FRED',
                        'YIELD': 'USTREASURY/YIELD'
                    },
                    'KEYS':{
                        'FIRST_LAYER': 'dataset',
                        'SECOND_LAYER': 'data',
                        'HEADER': 'code',
                        'ZIPFILE': 'FRED_metadata.csv'
                    },
                    'PARAMS':{
                        'KEY':'api_key',
                        'METADATA': 'metadata.json',
                        'START': 'start_date',
                        'END': 'end_date'
                    },
                    'YIELD_CURVE':{
                        'ONE_MONTH' : '1 MO',
                        'TWO_MONTH': '2 MO',
                        'THREE_MONTH': '3 MO',
                        'SIX_MONTH': '6 MO',
                        'ONE_YEAR': '1 YR',
                        'TWO_YEAR': '2 YR',
                        'THREE_YEAR': '3 YR',
                        'FIVE_YEAR': '5 YR',
                        'SEVEN_YEAR': '7 YR',
                        'TEN_YEAR': '10 YR',
                        'TWENTY_YEAR': '20 YR',
                        'THIRTY_YEAR': '30 YR'
                    }
                },
            }
        },
        'DIVIDENDS': {
            'IEX': {
                'MANAGER': 'iex'
            }
        }
    }
}

def get_trading_period(asset_type):
    """
    Description
    -----------
    Returns the value of one trading day measured in years of the asset_type passed in as an argument.

    Parameters
    ----------
    1. asset_type : str\n
    
    A string that represents a type of tradeable asset. Types are statically accessible through the ` settings` variables: ASSET_EQUITY and ASSET_CRYPTO.
    """
    if asset_type == keys['ASSETS']['CRYPTO']:
        return constants['ONE_TRADING_DAY']['CRYPTO']
    return constants['ONE_TRADING_DAY']['EQUITY']