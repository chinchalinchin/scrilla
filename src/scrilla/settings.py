import os, sys, dotenv, json

APP_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(APP_DIR)
ROOT_DIR = os.path.dirname(PROJECT_DIR)

sys.path.append(APP_DIR)

import util.outputter as outputter

## APPLICATION CONFIGURATION
"""
Application Configuration
-------------------------
Not to be confused with server.scrilla_api.core.settings, which configures the server side of the 
application. The settings in this file only affect the optimization and statistical calculations 
performed by the application. \n \n

Attributes
----------
1. APP_NAME: Name of the application. \n \n
2. VERSION: Version of the application. \n \n
3. APP_DIR: Folder containing this file. \n \n
4. APP_ENV: Application environment. \n \n
5. LOG_LEVEL: Debug output level. \n \n
6. CONFIG_FILE: Location of secondary credentials file. \n \n
7. CACHE_DIR: Folder where cached price histories reside. \n \n
8. CACHE_PRO_KEY: File name where risk-profile calculations are saved. \n \n
9. FILE_EXT: File extension used in CACHE_DIR. \n \n
10. STATIC_DIR: Folder where static data reside. \n \n
11. FILE_EXT: File extension used in STATIC_DIR. \n \n
12. STATIC_TICKERS_FILE: File containing a list of all equity ticker symbols with price histories that can be retrieved from external services. \n \n
13. STATIC_ECON_FILE: File containg a list of all economic statistics with sample histories that can be retrieved from external services. \n \n
14. STATIC_CRYPTO_FILE: File containing a list of all crypto ticker symbols with price histories that can be retrieved from external services. \n \n
15. ACCURACY: Number of decimals place saved in calculations. \n \n
16. POPUP_WIDTH: Width of popup that prompts for API keys. \n \n
17. POPUP_HEIGHT: Height of popup that prompts for API keys. \n \n
18. GUI_WIDTH: Width of root widget in GUI. \n \n
19. GUI_HEIGHT: Height of root widget in GUI. \n \n
20. OPTIMIZATION_METHOD: Scipy method used to optimize portfolios. \n \n
21. INVESTMENT_MODE: Determines if output is percentage or absolute. \n \n
22. FRONTIER_STEPS: Number of points in efficient frontier output. \n \n
23. MA_1_PERIOD: Number of days in first moving average period. \n \n
24. MA_2_PERIOD: Number of days in second moving average period. \n \n
25. MA_3_PERIOD: Number of days in first moving average period. \n \n
26. ONE_TRADING_DAY: Length of trading day in years. \n \n
27. PRICE_YEAR_CUTOFF: Earliest year considered in price histories. \n \n
28. DENOMINATION: Denomination in which prices are quoted. \n \n 
29. NPV_DELTA_TOLERANCE: NPV calculations stop when the next value adds less than this amount. \n \n 
29. RISK_FREE_RATE: Interest rate used for cashflow valuations. \n \n
30. MARKET_PROXY: Ticker symbol used to calculate market rate of return
28. ASSET_EQUITY: Constant for assets of type equity. \n \n
29. ASSET_CRYPTO: Constant for assets of type crypto. \n \n
30. STAT_ECON: Constant for economic statistics. \n \n
31. INIT: Flag to initialize STATIC_DIR \n \n
32. PRICE_MANAGER: Service in charge of price histories. \n \n
33. STAT_MANAGER: Service in charge of statistic histories. \n \n
34. DIVIDEND_MANAGER: Service in charge of dividend payment histories. \n \n
34. AV_URL: Base URL for AlphaVantage query. \n \n
35. AV_KEY: Credentials for AlphaVantage query. \n \n
36. AV_CRYPTO_LIST: URL for crypto metadata AlphaVantage query. \n \n
37. AV_RES_EQUITY_FIRST_LAYER: First key in AlphaVantage equity response. \n \n
38. AV_RES_EQUITY_CLOSE_PRICE: Column key in AlphaVantage response. \n \n
39. AV_RES_EQUITY_KEY: Column key in AlphaVantage response.  \n \n
40. AV_RES_CRYPTO_FIRST_LAYER: First key in AlphaVantage crypto response. \n \n
41. AV_RES_CRYPTO_KEY: Column key in AlphaVantage response. \n \n
42. AV_RES_CRYPTO_CLOSE_PRICE: Column key in AlphaVantage response. \n \n
43. AV_RES_ERROR: Key for error messages in AlphaVantage response. \n \n
44. AV_RES_LIMIT: Key for rate limit in AlphaVantage response. \n \n
45. PARAM_AV_TICKER: AlphaVantage ticker symbol query parameter. \n \n
46. PARAM_AV_FUNC: AlphaVantage function query parameter. \n \n
47. PARAM_AV_DENOM: AlphaVantage denomination query parameter. \n \n
48. PARAM_AV_KEY: AlphaVantage API Key query parameter. \n \n
49. PARAM_AV_SIZE: AlphaVantage sample size query parameter. \n \n
50. ARG_AV_FUNC_EQUITY_DAILY: : AlphaVantage query constant for daily equity prices. \n \n
51. ARG_AV_FUNC_EQUITY_LISTINGS: AlphaVantage query constant for equity metadata. \n \n
52. ARG_AV_FUNC_CRYPTO_DAILY: AlphaVantage query constant for daily crypto prices. \n \n
53. ARG_AV_SIZE_FULL: AlphaVantage query constant for full price history. \n \n
54. Q_URL: Base URL for Quandl query. \n \n
55. Q_KEY: Credentials for Quandl query. \n \n
56. Q_META_URL: URL for economic statistics data. \n \n
57. Q_FIRST_LAYER: First key for Quandl response. \n \n
58. Q_SECOND_LAYER: Second key for Quandl response. \n \n
59. Q_RES_STAT_KEY: Column key for Quandl response. \n \n
60. Q_RES_STAT_ZIP_KEY: Column key for Quandl response. \n \n
61. PATH_Q_FRED: Path parameter for Quandl query. \n \n
62. PARAM_Q_KEY: Quandl API key query parameter. \n \n
63. PARAM_Q_METADATA: Quandl metadata query parameter. \n \n
64. PARAM_Q_START: Quandl start date query parameter. \n \n
65. PARAM_Q_END: Quandl end date query parameter. \n \n
66. ARG_Q_YIELD_CURVE: Quandl constant for interest rate histories. \n \n
"""

APP_NAME="scrilla"

VERSION="0.0.1"

APP_ENV = os.environ.setdefault('APP_ENV', 'local')

# NOTE: Load in local.env file if not running application container. Container should 
# already have the container.env file preloaded in its environment.
if APP_ENV != 'container':
    dotenv.load_dotenv(os.path.join(os.path.join(ROOT_DIR,'env'), '.env'))

LOG_LEVEL = str(os.environ.setdefault("LOG_LEVEL", "info")).lower()

logger = outputter.Logger('settings', LOG_LEVEL)

# TODO: CACHE only supports JSON currently. Future file extensions: csv and txt.
FILE_EXT = os.environ.setdefault("FILE_EXT", "json")
KEEP_EXT = ".gitkeep"

CACHE_DIR = os.path.join(APP_DIR, 'data', 'cache')
CACHE_PRO_KEY="profile"
CACHE_PRICE_KEY="prices"
CACHE_COR_KEY="correlation"
CACHE_DIV_KEY="dividends"
CACHE_STAT_KEY="statistic"
CACHE_EQUITY_KEY="equity_statistic"

STATIC_DIR = os.path.join(APP_DIR, 'data', 'static')

STATIC_TICKERS_FILE = os.path.join(STATIC_DIR, f'tickers.{FILE_EXT}')
STATIC_ECON_FILE = os.path.join(STATIC_DIR, f'economics.{FILE_EXT}')
STATIC_CRYPTO_FILE = os.path.join(STATIC_DIR, f'crypto.{FILE_EXT}')

COMMON_DIR=os.path.join(APP_DIR, 'data', 'common')
COMMON_WATCHLIST_FILE=os.path.join(COMMON_DIR, f'watchlist.{FILE_EXT}')

ACCURACY=5

BACKOFF_PERIOD=30

# See .sample.env for more information.
LOCAL_CACHE = os.environ.setdefault('LOCAL_CACHE_ENABLED', 'true').strip().lower() == 'true'

## GUI CONFIGURATION

POPUP_WIDTH, POPUP_HEIGHT = 150, 150

try:
    GUI_WIDTH = int(os.getenv('GUI_WIDTH'))
except (ValueError, TypeError) as ParseError: 
    logger.debug('Failed to parse GUI_WIDTH from environment. Setting to default value of 800.')
    GUI_WIDTH = 800

try:
    GUI_HEIGHT = int(os.getenv('GUI_HEIGHT'))
except (ValueError, TypeError) as ParseError:
    logger.debug('Failed to parse GUI_HEIGHT from enviroment. Setting to default value of 800.')
    GUI_HEIGHT = 800


## FINANCIAL ALGORITHM CONFIGURATION

OPTIMIZATION_METHOD="SLSQP"

try:
    FRONTIER_STEPS = int(os.getenv('FRONTIER_STEPS'))

except (ValueError, TypeError) as ParseError:
    logger.debug('Failed to parse FRONTIER_STEPS from enviroment. Setting to default value of 5.')
    FRONTIER_STEPS = 5

try:
    MA_1_PERIOD = int(os.getenv('MA_1'))
except (ValueError, TypeError) as ParseError: 
    logger.debug('Failed to parse MA_1 from environment. Setting to default value of 20.')
    MA_1_PERIOD = 20

try:
    MA_2_PERIOD = int(os.getenv('MA_2'))
except (ValueError, TypeError) as ParseError: 
    logger.debug('Failed to parse MA_2 from environment. Setting to default value of 60.')
    MA_2_PERIOD = 60

try:
    MA_3_PERIOD = int(os.getenv('MA_3'))
except (ValueError, TypeError) as ParseError: 
    logger.debug('Failed to parse MA_3 from environment. Setting to default value of 100.')
    MA_3_PERIOD = 100

try:
    ITO_STEPS = int(os.getenv('ITO_STEPS'))
except (ValueError, TypeError) as ParseError:
    logger.debug('Failed to parsed ITO_STEPS from environment. Setting to default of 10000.')
    ITO_STEPS = 10000

ONE_TRADING_DAY=(1/252)

# Number of days
DEFAULT_ANALYSIS_PERIOD=100

PRICE_YEAR_CUTOFF=1950

DENOMINATION = "USD"

NPV_DELTA_TOLERANCE = 0.0000001

# SEE: ARG_Q_YIELD_CURVE for allowabled values
RISK_FREE_RATE=os.environ.setdefault("RISK_FREE", "10-Year").strip("\"")

MARKET_PROXY=os.environ.setdefault('MARKET_PROXY', 'SPY')

ASSET_EQUITY="equity"
ASSET_CRYPTO="crypto"
STAT_ECON="statistic"

## SERVICE CONFIGURATION
### PRICE_MANAGER CONFIGRUATION
PRICE_MANAGER = os.environ.setdefault('PRICE_MANAGER', 'alpha_vantage')

#### ALPHAVANTAGE CONFIGURATION
if PRICE_MANAGER == 'alpha_vantage':
    AV_URL = os.environ.setdefault('ALPHA_VANTAGE_URL', 'https://www.alphavantage.co/query').strip("\"").strip("'")
    
    AV_KEY = os.environ.setdefault('ALPHA_VANTAGE_KEY', '')
    if AV_KEY is None:
        keystore = os.path.join(COMMON_DIR, f'ALPHA_VANTAGE_KEY.{FILE_EXT}')
        if os.path.isfile(keystore):
            with open(keystore, 'r') as infile:
                if FILE_EXT == "json":
                    AV_KEY = json.load(infile)['ALPHA_VANTAGE_KEY']
                    
    # Metadata Endpoints
    AV_CRYPTO_LIST=os.environ.setdefault('ALPHA_VANTAGE_CRYPTO_META_URL', 'https://www.alphavantage.co/digital_currency_list/')
    
    # Response Keys
    AV_RES_EQUITY_FIRST_LAYER='Time Series (Daily)'
    AV_RES_EQUITY_CLOSE_PRICE="4. close"
    AV_RES_EQUITY_OPEN_PRICE="1. open"
    AV_RES_EQUITY_KEY="symbol"
    AV_RES_CRYPTO_FIRST_LAYER='Time Series (Digital Currency Daily)'
    AV_RES_CRYPTO_KEY="currency code"
    AV_RES_CRYPTO_CLOSE_PRICE=f'4a. close ({DENOMINATION})'
    AV_RES_CRYPTO_OPEN_PRICE=f'1a. open ({DENOMINATION})'
    AV_RES_ERROR='Error Message'
    AV_RES_LIMIT='Note'
    AV_RES_DAY_LIMIT='Information'
    
    # Query Parameters
    PARAM_AV_TICKER="symbol"
    PARAM_AV_FUNC="function"
    PARAM_AV_DENOM="market"
    PARAM_AV_KEY="apikey"
    PARAM_AV_SIZE="outputsize"
    
    # Query Arguments
    ARG_AV_FUNC_EQUITY_DAILY="TIME_SERIES_DAILY"
    ARG_AV_FUNC_EQUITY_LISTINGS="LISTING_STATUS"
    ARG_AV_FUNC_CRYPTO_DAILY="DIGITAL_CURRENCY_DAILY"
    ARG_AV_SIZE_FULL="full"

### STAT_MANAGER CONFIGURATION
STAT_MANAGER = os.environ.setdefault('STAT_MANAGER', 'quandl')

#### QUANDL CONFIGURAITON
if STAT_MANAGER == "quandl":
    Q_URL = os.environ.setdefault('QUANDL_URL', 'https://www.quandl.com/api/v3/datasets').strip("\"").strip("'")
    
    Q_KEY = os.environ.setdefault('QUANDL_KEY', '')
    if Q_KEY is None:
        keystore = os.path.join(COMMON_DIR, f'QUANDL_KEY.{FILE_EXT}')
        if os.path.isfile(keystore):
            with open(keystore, 'r') as infile:
                if FILE_EXT == "json":
                    Q_KEY = json.load(infile)['QUANDL_KEY']

    # Metadata Endpoints
    Q_META_URL = os.environ.setdefault('QUANDL_META_URL' ,'https://www.quandl.com/api/v3/databases')

    # Response Keys
    Q_FIRST_LAYER="dataset"
    Q_SECOND_LAYER="data"
    Q_RES_STAT_KEY="code"
    Q_RES_STAT_ZIP_KEY="FRED_metadata.csv"

    # Path Paramaters
    PATH_Q_FRED ="FRED"

    # Special Endpoints
    ARG_Q_YIELD_CURVE = {
        'Overnight': 'DFF',
        '3-Month': 'DTB3',
        '5-Year': 'DGS5',
        '10-Year': 'DGS10',
        '30-Year': 'DGS30'
    }
    RISK_FREE_RATE=ARG_Q_YIELD_CURVE[RISK_FREE_RATE]
        
    # Query Parameters
    PARAM_Q_KEY="api_key"
    PARAM_Q_METADATA="metadata.json"
    PARAM_Q_START="start_date"
    PARAM_Q_END="end_date"

### DIVIDEND_MANAGER CONFIGURATION
DIV_MANAGER=os.environ.setdefault("DIV_MANAGER", 'iex')

if DIV_MANAGER == "iex":
    IEX_URL = os.environ.setdefault("IEX_URL", 'https://cloud.iexapis.com/stable/stock')
    
    IEX_KEY = os.environ.setdefault("IEX_KEY", '')
    if IEX_KEY is None:
        keystore = os.path.join(COMMON_DIR, f'IEX_KEY.{FILE_EXT}')
        if os.path.isfile(keystore):
            with open(keystore, 'r') as infile:
                if FILE_EXT == "json":
                    IEX_KEY = json.load(infile)['IEX_KEY']

    IEX_RES_DATE_KEY="paymentDate"
    IEX_RES_DIV_KEY="amount"

    PATH_IEX_DIV ="dividends"

    PARAM_IEX_RANGE_5YR="5y"
    PARAM_IEX_RANGE_2YR="2y"
    PARAM_IEX_RANGE_1YR="1y"
    PARAM_IEX_KEY="token"

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
    if asset_type == ASSET_CRYPTO:
        return (1/365)
    return ONE_TRADING_DAY
