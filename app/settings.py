import sys, os, json, dotenv

import util.helper as helper
import util.tester as tester
import util.logger as logger

## APPLICATION CONFIGURATION
"""
Application Configuration
-------------------------
Not to be confused with server.pynance_api.core.settings, which configures the server side of the 
application. The settings in this file only affect the optimization and statistical calculations 
performed by the application. 

Attributes
----------
1. APP_NAME: Name of the application. \n \n
2. VERSION: Version of the application. \n \n
3. APP_DIR: Folder containing this file. \n \n
4. APP_ENV: Application environment. \n \n
5. LOG_LEVEL: Debug output level. \n \n
6. CONFIG_FILE: Location of secondary credentials file. \n \n
7. CACHE_DIR: Folder where cached price histories reside. \n \n
8. CACHE_STAT_KEY: File name where calculations are saved. \n \n
9. FILE_EXT: File extension used in CACHE_DIR. \n \n
10. STATIC_DIR: Folder where static data reside. \n \n
11. FILE_EXT: File extension used in STATIC_DIR. \n \n
12. STATIC_TICKERS_FILE: File containing equity ticker symbols. \n \n
13. STATIC_ECON_FILE: File containg list of economic statistics. \n \n
14. STATIC_CRYPTO_FILE: File containing crypto ticker symbols. \n \n
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

APP_NAME="PYNANCE"

VERSION="0.0.1"

APP_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

PROJECT_DIR = os.path.dirname(APP_DIR)

APP_ENV = os.environ.setdefault('APP_ENV', 'local')

# NOTE: Load in local.env file if not running application container. Container should 
# already have the container.env file preloaded in its environment.
if APP_ENV != 'container':
    dotenv.load_dotenv(os.path.join(os.path.join(APP_DIR,'env'), 'local.env'))

LOG_LEVEL = str(os.environ.setdefault("LOG_LEVEL", "info")).lower()

output = logger.Logger('app.settings', LOG_LEVEL)

# TODO: CACHE only supports JSON currently. Future file extensions: csv and txt.
FILE_EXT = os.environ.setdefault("FILE_EXT", "json")

CACHE_DIR = os.path.join(APP_DIR, 'data', 'cache')
CACHE_STAT_KEY = "statistics"

STATIC_DIR = os.path.join(APP_DIR, 'data', 'static')

STATIC_TICKERS_FILE = os.path.join(STATIC_DIR, f'tickers.{FILE_EXT}')
STATIC_ECON_FILE = os.path.join(STATIC_DIR, f'economics.{FILE_EXT}')
STATIC_CRYPTO_FILE = os.path.join(STATIC_DIR, f'crypto.{FILE_EXT}')

COMMON_DIR=os.path.join(APP_DIR, 'data', 'common')
COMMON_WATCHLIST_FILE=os.path.join(COMMON_DIR, f'watchlist.{FILE_EXT}')

ACCURACY=5

## GUI CONFIGURATION

POPUP_WIDTH, POPUP_HEIGHT = 150, 150

try:
    GUI_WIDTH = int(os.environ.setdefault('GUI_WIDTH', 800))
except: 
    output.debug('Failed to parse GUI_WIDTH from .env File. Setting to default value of 800. Please Ensure GUI_WIDTH is set to an integer value.')
    GUI_WIDTH = 800

try:
    GUI_HEIGHT = int(os.environ.setdefault('GUI_HEIGHT', 800))
except:
    output.debug('Failed to parse GUI_HEIGHT from .env File. Setting to default value of 800. Please Ensure GUI_HEIGHT is set to an integer value.')
    GUI_HEIGHT = 800


## FINANCIAL CONFIGURATION

OPTIMIZATION_METHOD="SLSQP"

INVESTMENT_MODE = True if os.getenv('INVESTMENT_MODE').lower() == 'true' else False

try:
    FRONTIER_STEPS = int(os.getenv('FRONTIER_STEPS'))

except:
    output.debug('Failed to parse FRONTIER_STEPS from .env File. Setting to default value of 5. Please Ensure FRONTIER_STEPS is set to an integer value.')
    FRONTIER_STEPS = 5

try:
    MA_1_PERIOD = int(os.getenv('MA_1'))
except: 
    output.debug('Failed to parse MA_1 from .env File. Setting to default value of 20. Please Ensure MA_1 is set to an integer value.')
    MA_1_PERIOD = 20

try:
    MA_2_PERIOD = int(os.getenv('MA_2'))
except: 
    output.debug('Failed to parse MA_2 from .env File. Setting to default value of 60. Please Ensure MA_2 is set to an integer value.')
    MA_2_PERIOD = 60

try:
    MA_3_PERIOD = int(os.getenv('MA_3'))
except: 
    output.debug('Failed to parse MA_3 from .env File. Setting to default value of 100. Please Ensure MA_3 is set to an integer value.')
    MA_3_PERIOD = 100

ONE_TRADING_DAY=(1/252)

PRICE_YEAR_CUTOFF=1950

DENOMINATION = "USD"

NPV_DELTA_TOLERANCE = 0.0000001

# SEE: ARG_Q_YIELD_CURVE for allowabled values
RISK_FREE_RATE=os.environ.setdefault("RISK_FREE", "10-Year")

ASSET_EQUITY="equity"
ASSET_CRYPTO="crypto"
STAT_ECON="indicator"

## SERVICE CONFIGURATION

INIT= True if os.getenv('INIT').lower() == 'true' else False

new_alpha_creds = None
new_quandl_creds = None

### PRICE_MANAGER CONFIGRUATION
PRICE_MANAGER = os.getenv('PRICE_MANAGER')

#### ALPHAVANTAGE CONFIGURATION
if PRICE_MANAGER == 'alpha_vantage':
    AV_URL = os.getenv('ALPHA_VANTAGE_URL').strip("\"").strip("'")
    AV_KEY = os.getenv('ALPHA_VANTAGE_KEY')

    # Metadata Endpoints
    AV_CRYPTO_LIST=os.getenv('ALPHA_VANTAGE_CRYPTO_META_URL')
    
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
STAT_MANAGER = os.getenv('STAT_MANAGER')

#### QUANDL CONFIGURAITON
if STAT_MANAGER == "quandl":
    Q_URL = os.getenv('QUANDL_URL').strip("\"").strip("'")
    Q_KEY = os.getenv('QUANDL_KEY')

    # Metadata Endpoints
    Q_META_URL = os.getenv('QUANDL_META_URL')

    # Response Keys
    Q_FIRST_LAYER="dataset"
    Q_SECOND_LAYER="data"
    Q_RES_STAT_KEY="code"
    Q_RES_STAT_ZIP_KEY="FRED_metadata.csv"

    # Path Paramaters
    PATH_Q_FRED ="FRED"

    # Special Endpoints
    ARG_Q_YIELD_CURVE = {
        '3-Month': 'DTB3',
        '5-Year': 'DGS5',
        '10-Year': 'DGS10',
        '30-Year': 'DGS30'
    }
        
    # Query Parameters
    PARAM_Q_KEY="api_key"
    PARAM_Q_METADATA="metadata.json"
    PARAM_Q_START="start_date"
    PARAM_Q_END="end_date"

### DIVIDEND_MANAGER CONFIGURATION
DIV_MANAGER=os.getenv("DIV_MANAGER")

if DIV_MANAGER == "iex":
    IEX_URL = os.getenv("IEX_URL")
    IEX_KEY = os.getenv("IEX_KEY")

    IEX_RES_DATE_KEY="paymentDate"
    IEX_RES_DIV_KEY="amount"

    PATH_IEX_DIV ="dividends"

    PARAM_IEX_RANGE_5YR="5y"
    PARAM_IEX_RANGE_2YR="2y"
    PARAM_IEX_RANGE_1YR="1y"
    PARAM_IEX_KEY="token"
