keys= {
    'PRICES': {
        'OPEN': 'open',
        'CLOSE': 'close'
    },
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
        'CRYPTO': 'crypto'
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
        'PRICE':{
            'ALPHA_VANTAGE': 'alpha_vantage',
        },
        'STATISTICS': {
            'QUANDL': 'quandl'
        },
        'DIVIDENDS': {
            'IEX': 'iex'
        }
    }
}
constants = {
    'ONE_TRADING_DAY': {
        'EQUITY': (1/252),
        'CRYPTO': (1/365)
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