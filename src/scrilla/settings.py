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
"""
Application-wide configuration settings. 

Attributes
----------
1. `scrilla.settings.APP_NAME`: Name of the application.
2. `scrilla.settings.APP_DIR`: Folder containing this file.
3. `scrilla.settings.PROJECT_DIR`: Folder containering the project source.
4. `scrilla.settings.ROOT_DIR`: Root folder of the repository.
5. `scrilla.settings.APP_ENV`: Application environment.
6. `scrilla.settings.LOG_LEVEL`: Debug output level.
7. `scrilla.settings.CACHE_DIR`: Folder where cached price histories reside.
8. `scrilla.settings.CACHE_SQLITE_FILE`: Location of the SQLite persistence store.
9. `scrilla.settings.FILE_EXT`: File extension used in CACHE_DIR.
10. `scrilla.settings.STATIC_DIR`: Folder where static data reside.
11. `scrilla.settings.FILE_EXT`: File extension used to store files across the program.
12. `scrilla.settings.STATIC_TICKERS_FILE`: File containing a list of all equity ticker symbols with price histories that can be retrieved from external services.
13. `scrilla.settings.STATIC_ECON_FILE`: File containg a list of all economic statistics with sample histories that can be retrieved from external services.
14. `scrilla.settings.STATIC_CRYPTO_FILE`: File containing a list of all crypto ticker symbols with price histories that can be retrieved from external services.
15. GUI_WIDTH: Width of root widget in GUI.
16. GUI_HEIGHT: Height of root widget in GUI.
17. FRONTIER_STEPS: Number of points in efficient frontier output.
18. MA_1_PERIOD: Number of days in first moving average period.
19. MA_2_PERIOD: Number of days in second moving average period.
20. MA_3_PERIOD: Number of days in first moving average period.
21. RISK_FREE_RATE: Interest rate used for cashflow valuations.
22. MARKET_PROXY: Ticker symbol used to calculate market rate of return
23. `scrilla.settings.PRICE_MANAGER`: Service in charge of price histories.
24. STAT_MANAGER: Service in charge of statistic histories.
25. DIVIDEND_MANAGER: Service in charge of dividend payment histories.
26. AV_URL: Base URL for AlphaVantage query.
27. AV_KEY: Credentials for AlphaVantage query.
28. AV_CRYPTO_LIST: URL for crypto metadata AlphaVantage query.
54. Q_URL: Base URL for Quandl query.
55. Q_KEY: Credentials for Quandl query.
56. Q_META_URL: URL for economic statistics data.
"""
import os, dotenv, json

import scrilla.util.outputter as outputter

class APIKeyError(Exception):
    pass

APP_DIR = os.path.dirname(os.path.abspath(__file__))
"""Folder containing the root module of the project"""

PROJECT_DIR = os.path.dirname(APP_DIR)
"""Folder containing the project source"""

ROOT_DIR = os.path.dirname(PROJECT_DIR)
"""Folder containing the entire project"""

APP_NAME="scrilla"
"""Name of the application"""

APP_ENV = os.environ.setdefault('APP_ENV', 'local')
"""Application execution environment; Configured by environment variable of the same name, **APP_ENV**."""

env_file = os.path.join(os.path.join(ROOT_DIR,'env'), '.env')
if APP_ENV != 'container' and os.path.isfile(env_file):
    dotenv.load_dotenv(os.path.join(os.path.join(ROOT_DIR,'env'), '.env'))

LOG_LEVEL = str(os.environ.setdefault("LOG_LEVEL", "info")).lower()
"""Application log level output; Configured by environment of the same name, **LOG_LEVEL**."""
logger = outputter.Logger('settings', LOG_LEVEL)

# TODO: save formatting only supports JSON currently. Future file extensions: csv and txt.
FILE_EXT = os.environ.setdefault("FILE_EXT", "json")
"""Extension used to save files; Configured by environment variable of the same name, **FILE_EXT**"""

CACHE_DIR = os.path.join(APP_DIR, 'data', 'cache')
"""Directory containing cached prices, statistics and calculations"""
CACHE_SQLITE_FILE = os.environ.setdefault('SQLITE_FILE', os.path.join(CACHE_DIR, 'scrilla.db'))
"""Location of the SQLite database flat file; Configured by environment variable **SQLITE_FILE***"""
CACHE_TEMP_FILE = os.path.join(CACHE_DIR, 'tmp')

STATIC_DIR = os.path.join(APP_DIR, 'data', 'static')
"""Directory containg static data, such as ticker symbols, statistic symbols, etc."""

STATIC_TICKERS_FILE = os.path.join(STATIC_DIR, f'tickers.{FILE_EXT}')
"""Location of file used to store equity ticker symbols"""
STATIC_ECON_FILE = os.path.join(STATIC_DIR, f'economics.{FILE_EXT}')
"""Location of file used to store statistic symbols"""
STATIC_CRYPTO_FILE = os.path.join(STATIC_DIR, f'crypto.{FILE_EXT}')
"""Location of file used to store crypto ticker symbols"""

COMMON_DIR=os.path.join(APP_DIR, 'data', 'common')
"""Directory used to store common files, such as API keys, watchlist, etc."""
COMMON_WATCHLIST_FILE=os.path.join(COMMON_DIR, f'watchlist.{FILE_EXT}')
"""Location of file used to store watchlisted ticker symbols"""

## GUI CONFIGURATION
try:
    GUI_WIDTH = int(os.environ.setdefault('GUI_WIDTH', '600'))
    """Width of main Graphical User Interface window; Configured by environment variable of same name, **GUI_WIDTH**"""
except (ValueError, TypeError) as ParseError: 
    logger.debug('Failed to parse GUI_WIDTH from environment. Setting to default value of 800.')
    GUI_WIDTH = 800
    os.environ['GUI_WIDTH'] = '800'

try:
    GUI_HEIGHT = int(os.environ.setdefault('GUI_HEIGHT', '600'))
    """Height of main Graphical User Interface window; Configured by environment variable of same name, **GUI_HEIGHT**."""
except (ValueError, TypeError) as ParseError:
    logger.debug('Failed to parse GUI_HEIGHT from enviroment. Setting to default value of 800.')
    GUI_HEIGHT = 800
    os.environ['GUI_HEIGHT'] = '800'

## FINANCIAL ALGORITHM CONFIGURATION
try:
    FRONTIER_STEPS = int(os.environ.setdefault('FRONTIER_STEPS', '5'))
    """Number of data points used to trace out the efficient frontier; Configured by environment variable of same name, **FRONTIER_STEPS** """
except (ValueError, TypeError) as ParseError:
    logger.debug('Failed to parse FRONTIER_STEPS from enviroment. Setting to default value of 5.')
    FRONTIER_STEPS = 5
    os.environ['FRONTIER_STEPS'] = '5'

try:
    MA_1_PERIOD = int(os.environ.setdefault('MA_1', '20'))
    """Number of data points in first moving average period; Configured by environment variable, **MA_1**"""
except (ValueError, TypeError) as ParseError: 
    logger.debug('Failed to parse MA_1 from environment. Setting to default value of 20.')
    MA_1_PERIOD = 20
    os.environ['MA_1'] = '20'

try:
    MA_2_PERIOD = int(os.environ.setdefault('MA_2', '60'))
    """Number of data points in second moving average period; Configured by environment variable, **MA_2**"""
except (ValueError, TypeError) as ParseError: 
    logger.debug('Failed to parse MA_2 from environment. Setting to default value of 60.')
    MA_2_PERIOD = 60
    os.environ['MA_2'] = '60'

try:
    MA_3_PERIOD = int(os.environ.setdefault('MA_3', '100'))
    """Number of data points in third moving average period; Configured by environment variable, **MA_3***"""
except (ValueError, TypeError) as ParseError: 
    logger.debug('Failed to parse MA_3 from environment. Setting to default value of 100.')
    MA_3_PERIOD = 100
    os.environ['MA_3'] = '100'

try:
    ITO_STEPS = int(os.environ.setdefault('ITO_STEPS', '10000'))
    """Number of iterations used to approximate an Ito integral; Configured by environment variable of same name, **ITO_STEPS**"""
except (ValueError, TypeError) as ParseError:
    logger.debug('Failed to parse ITO_STEPS from environment. Setting to default of 10000.')
    ITO_STEPS = 10000
    os.environ['ITO_STEPS'] = '10000'

try:
    DEFAULT_ANALYSIS_PERIOD=int(os.environ.setdefault('DEFAULT_ANALYSIS_PERIOD', '100'))
    """Number of days used in a historical sample, if no date range is specified; Configured by environment variable of same name, **DEFAULT_ANALYSIS_PERIOD**"""
except (ValueError, TypeError) as ParseError:
    logger.debug('Failed to parse DEFAULT_ANALYSIS_PERIOD from environment. Setting to default of 100.')
    DEFAULT_ANALYSIS_PERIOD=100
    os.environ['DEFAULT_ANALYSIS_PERIOD']=100

RISK_FREE_RATE=os.environ.setdefault("RISK_FREE", "TEN_YEAR").strip("\"")
"""Maturity of the US Treasury Yield Curve used as a proxy for the risk free rate"""

MARKET_PROXY=os.environ.setdefault('MARKET_PROXY', 'SPY')
"""Ticker symbol used as a proxy for the overall market rate of return"""

ANALYSIS_MODE=os.environ.setdefault('ANALYSIS_MODE', 'geometric')
"""Determines the asset price process and thus, the underlying probability distribution of an asset's return"""

ESTIMATION_METHOD=os.environ.setdefault('DEFAULT_ESTIMATION_METHOD', 'moments')
"""Determines the default estimation method using in statistical estimations"""

## SERVICE CONFIGURATION
### PRICE_MANAGER CONFIGRUATION
PRICE_MANAGER = os.environ.setdefault('PRICE_MANAGER', 'alpha_vantage')
"""Determines the service used to retrieve price data"""

#### ALPHAVANTAGE CONFIGURATION
if PRICE_MANAGER == 'alpha_vantage':
    AV_URL = os.environ.setdefault('ALPHA_VANTAGE_URL', 'https://www.alphavantage.co/query').strip("\"").strip("'")
    AV_CRYPTO_LIST=os.environ.setdefault('ALPHA_VANTAGE_CRYPTO_META_URL', 'https://www.alphavantage.co/digital_currency_list/')

    AV_KEY = os.environ.setdefault('ALPHA_VANTAGE_KEY', '')
    if not AV_KEY:
        keystore = os.path.join(COMMON_DIR, f'ALPHA_VANTAGE_KEY.{FILE_EXT}')
        if os.path.isfile(keystore):
            with open(keystore, 'r') as infile:
                if FILE_EXT == "json":
                    AV_KEY = json.load(infile)['ALPHA_VANTAGE_KEY']
                    os.environ['ALPHA_VANTAGE_KEY'] = str(AV_KEY)

    if not AV_KEY:
        raise APIKeyError('Alpha Vantage API Key not found. Either set ALPHA_VANTAGE_KEY environment variable or use "-store" CLI function to save key.')

### STAT_MANAGER CONFIGURATION
STAT_MANAGER = os.environ.setdefault('STAT_MANAGER', 'quandl')
"""Determines the service used to retrieve statistics data"""

#### QUANDL CONFIGURAITON
if STAT_MANAGER == "quandl":
    Q_URL = os.environ.setdefault('QUANDL_URL', 'https://www.quandl.com/api/v3/datasets').strip("\"").strip("'")
    Q_META_URL = os.environ.setdefault('QUANDL_META_URL' ,'https://www.quandl.com/api/v3/databases')
    Q_KEY = os.environ.setdefault('QUANDL_KEY', '')

    if not Q_KEY:
        keystore = os.path.join(COMMON_DIR, f'QUANDL_KEY.{FILE_EXT}')
        if os.path.isfile(keystore):
            with open(keystore, 'r') as infile:
                if FILE_EXT == "json":
                    Q_KEY = json.load(infile)['QUANDL_KEY']
                    os.environ['QUANDL_KEY'] = str(Q_KEY)

    if not Q_KEY:
        raise APIKeyError('Quandl API Key not found. Either set QUANDL_KEY environment variable or use "-store" CLI function to save key.')

### DIVIDEND_MANAGER CONFIGURATION
DIV_MANAGER=os.environ.setdefault("DIV_MANAGER", 'iex')
"""Determines the service used to retrieve dividends data"""

if DIV_MANAGER == "iex":
    IEX_URL = os.environ.setdefault("IEX_URL", 'https://cloud.iexapis.com/stable/stock')
    
    IEX_KEY = os.environ.setdefault("IEX_KEY", '')
    if not IEX_KEY:
        keystore = os.path.join(COMMON_DIR, f'IEX_KEY.{FILE_EXT}')
        if os.path.isfile(keystore):
            with open(keystore, 'r') as infile:
                if FILE_EXT == "json":
                    IEX_KEY = json.load(infile)['IEX_KEY']
                    os.environ['IEX_KEY'] = str(IEX_KEY)

    if not IEX_KEY:
        raise APIKeyError('IEX API Key cannot be found. Either set IEX_KEY environment variable or use "-store" CLI function to save key.')
