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
        'CORRELATION': 'correlation',
        'CVAR': 'conditional_value_at_risk',
        'VAR': 'value_at_risk'
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
                        'YIELD': 'USTREASURY/YIELD.json'
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
            },
            'TREASURY': {
                'MANAGER': 'treasury',
                'MAP': {
                    'PATHS': {
                        'YIELD': 'interest-rates/pages/xml'
                    },
                    'KEYS': {
                        'FIRST_LAYER': '{http://www.w3.org/2005/Atom}entry',
                        'RATE_XPATH': './{http://www.w3.org/2005/Atom}content/{http://schemas.microsoft.com/ado/2007/08/dataservices/metadata}properties/{http://schemas.microsoft.com/ado/2007/08/dataservices}',
                        'PAGE_LENGTH': 300,
                        'DATE': 'NEW_DATE'
                    },
                    'PARAMS': {
                        'DATA': 'data',
                        'END': 'field_tdr_date_value',
                        'PAGE': 'page'
                    },
                    'ARGUMENTS': {
                        'DAILY': 'daily_treasury_yield_curve',
                    },
                    'YIELD_CURVE': {
                        'ONE_MONTH': 'BC_1MONTH',
                        'TWO_MONTH': 'BC_2MONTH',
                        'THREE_MONTH': 'BC_3MONTH',
                        'SIX_MONTH': 'BC_6MONTH',
                        'ONE_YEAR': 'BC_1YEAR',
                        'TWO_YEAR': 'BC_2YEAR',
                        'THREE_YEAR': 'BC_3YEAR',
                        'FIVE_YEAR': 'BC_5YEAR',
                        'SEVEN_YEAR': 'BC_7YEAR',
                        'TEN_YEAR': 'BC_10YEAR',
                        'TWENTY_YEAR': 'BC_20YEAR',
                        'THIRTY_YEAR': 'BC_30YEAR'
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
