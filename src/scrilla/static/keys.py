from scrilla.static.constants import constants

keys = {
    'PRICES': {
        'OPEN': 'open',
        'CLOSE': 'close'
    },
    'ESTIMATION': {
        'MOMENT': 'moments',
        'PERCENT': 'percentiles',
        'LIKE': 'likelihood'
    },
    'SDE': {
        'GBM': 'geometric',
        'MEAN': 'reversion'
    },
    'MODELS': {
        'DDM': 'discount_dividend',
        'DCF': 'discount_cashflow'
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
    'ASSETS': {
        'EQUITY': 'equity',
        'CRYPTO': 'crypto',
        'STAT': 'statistics',
        'BOND': 'bond'
    },
    'CACHE': {
        'PRICES': 'prices',
        'PROFILE': 'profile',
        'CORRELATION': 'correlation',
        'DIVIDENDS': 'dividends',
        'STATISTIC': 'statistic'
    },
    'PARAMETERS': {
        'TICKER': 'ticker',
        'TICKERS': 'tickers',
        'START': 'start_date',
        'END': 'end_date'
    },
    'SERVICES': {
        'PRICES': {
            'ALPHA_VANTAGE': {
                'MANAGER': 'alpha_vantage',
                'MAP': {
                    'KEYS': {
                        'EQUITY': {
                            'FIRST_LAYER': 'Time Series (Daily)',
                            'CLOSE': '4. close',
                            'OPEN': '1. open',
                            'HEADER': 'symbol'
                        },
                        'CRYPTO': {
                            'FIRST_LAYER': 'Time Series (Digital Currency Daily)',
                            'CLOSE': f'4a. close ({constants["DENOMINATION"]})',
                            'OPEN': f'1a. open ({constants["DENOMINATION"]})',
                            'HEADER': 'currency code'
                        },
                        'ERROR': 'Error Message',
                        'THROTTLE': 'Note',
                        'LIMIT': 'Information'
                    },
                    'PARAMS': {
                        'TICKER': 'symbol',
                        'FUNCTION': 'function',
                        'DENOMINATION': 'market',
                        'KEY': 'apikey',
                        'SIZE': 'outputsize'
                    },
                    'ARGUMENTS': {
                        'EQUITY_DAILY': 'TIME_SERIES_DAILY',
                        'EQUITY_LISTING': 'LISTING_STATUS',
                        'CRYPTO_DAILY': 'DIGITAL_CURRENCY_DAILY',
                        'FULL': 'full'
                    },
                    'ERRORS': {
                        'RATE_THROTTLE': 'Note',
                        'RATE_LIMIT': 'Information',
                        'INVALID': 'Error Message'
                    }
                }
            }
        },
        'STATISTICS': {
            'QUANDL': {
                'MANAGER': 'quandl',
                'MAP': {
                    'PATHS': {
                        'FRED': 'FRED',
                        'YIELD': 'USTREASURY/YIELD'
                    },
                    'KEYS': {
                        'FIRST_LAYER': 'dataset',
                        'SECOND_LAYER': 'data',
                        'HEADER': 'code',
                        'ZIPFILE': 'FRED_metadata.csv'
                    },
                    'PARAMS': {
                        'KEY': 'api_key',
                        'METADATA': 'metadata.json',
                        'START': 'start_date',
                        'END': 'end_date'
                    },
                    'YIELD_CURVE': {
                        'ONE_MONTH': '1 MO',
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
                'MANAGER': 'iex',
                'MAP': {
                    'PATHS': {
                        'DIV': 'dividends'
                    },
                    'KEYS': {
                        'DATE': 'paymentDate',
                        'AMOUNT': 'amount'
                    },
                    'PARAMS': {
                        'FULL': '5y',
                        'KEY': 'token'
                    }
                }
            }
        }
    },
    'GUI': {
        'TEMP': {
            'PROFILE': 'profile',
            'AVERAGES': 'averages',
            'FRONTIER': 'frontier',
            'DIST': 'distribution',
            'DIVIDEND': 'dividends',
            'YIELD': 'yieldcurve',
            'QQ': 'qqplot'
        },
        'SHORTCUTS': {
            'CORREL': 'Ctrl+1',
            'DIVIDEND': 'Ctrl+2',
            'FRONTIER': 'Ctrl+3',
            'AVERAGES': 'Ctrl+4',
            'OPTIMIZE': 'Ctrl+5'
        }
    },
    'APP': {
        'PROFILE': {
            'RET': 'annual_return',
            'VOL': 'annual_volatility',
            'BETA': 'asset_beta',
            'SHARPE': 'sharpe_ratio',
            'EQUITY': 'equity_cost'
        }
    }
}
