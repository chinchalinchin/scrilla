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
"""
import os
import json

import scrilla.util.outputter as outputter


class APIKeyError(Exception):
    pass


APP_DIR = os.path.dirname(os.path.abspath(__file__))
"""Folder containing the root module of the project"""

PROJECT_DIR = os.path.dirname(APP_DIR)
"""Folder containing the project source"""

APP_NAME = "scrilla"
"""Name of the application"""

APP_ENV = os.environ.setdefault('APP_ENV', 'local')
"""Application execution environment; Configured by environment variable of the same name, **APP_ENV**."""

LOG_LEVEL = str(os.environ.setdefault("LOG_LEVEL", "info")).lower()
"""Application log level output; Configured by environment of the same name, **LOG_LEVEL**."""
logger = outputter.Logger('settings', LOG_LEVEL)

# TODO: save formatting only supports JSON currently. Future file extensions: csv and txt.
FILE_EXT = os.environ.setdefault("FILE_EXT", "json")
"""Extension used to save files; Configured by environment variable of the same name, **FILE_EXT**"""

IMG_EXT = os.environ.setdefault("IMG_EXT", "jpg")
"""Extension used to saved images; Configured by environment variable of the same name, **IMG_EXT**"""

METADATA_FILE = os.path.join(APP_DIR, 'data', 'meta', 'data.json')
"""File containing metadata information about the application"""

CACHE_DIR = os.path.join(APP_DIR, 'data', 'cache')
"""Directory containing cached prices, statistics and calculations"""
CACHE_SQLITE_FILE = os.environ.setdefault(
    'SQLITE_FILE', os.path.join(CACHE_DIR, 'scrilla.db'))
"""Location of the SQLite database flat file; Configured by environment variable **SQLITE_FILE***"""

TEMP_DIR = os.path.join(APP_DIR, 'data', 'tmp')
"""Buffer directory for graphics generated while using the GUI."""

ASSET_DIR = os.path.join(APP_DIR, 'data', 'assets')
"""Directory containing application assets such as icons, HTML templates, jpegs, etc."""

STATIC_DIR = os.path.join(APP_DIR, 'data', 'static')
"""Directory containg static data, such as ticker symbols, statistic symbols, etc."""

STATIC_TICKERS_FILE = os.path.join(STATIC_DIR, f'tickers.{FILE_EXT}')
"""Location of file used to store equity ticker symbols"""

STATIC_ECON_FILE = os.path.join(STATIC_DIR, f'economics.{FILE_EXT}')
"""Location of file used to store statistic symbols"""

STATIC_CRYPTO_FILE = os.path.join(STATIC_DIR, f'crypto.{FILE_EXT}')
"""Location of file used to store crypto ticker symbols"""

COMMON_DIR = os.path.join(APP_DIR, 'data', 'common')
"""Directory used to store common files, such as API keys, watchlist, etc.

.. notes::
    * It is recommended API keys are not stored in this directory, as they will be stored unencrypted. A better option is storing the keys as environment variables in your current session. See the documentation for more information. 
"""

COMMON_WATCHLIST_FILE = os.path.join(COMMON_DIR, f'watchlist.{FILE_EXT}')
"""Location of file used to store watchlisted ticker symbols"""

GUI_STYLESHEET_FILE = os.path.join(APP_DIR, 'gui', 'styles', 'app.qss')
"""Location of the stylesheet applied to the GUI"""

GUI_THEME_FILE = os.path.join(APP_DIR, 'gui', 'styles', 'themes.json')
"""Location of the color schemes used to style components"""

GUI_ICON_FILE = os.path.join(APP_DIR, 'gui', 'styles', 'icons.json')
"""Location of the icon filenames used as icons for `PySide6.QtWidgets.QPushButtons`"""

GUI_TEMPLATE_DIR = os.path.join(APP_DIR, 'gui', 'templates')
"""Location where the HTML templates for certain ``PySide6.QtWidgets.QWidget`'s are stored."""

GUI_DARK_MODE = os.environ.setdefault('DARK_MODE', 'true').lower() == 'true'
"""Flag determining the theme of the GUI, i.e. light mode or dark mode."""

# OPTIONAL USER CONFIGURATION
DATE_FORMAT = None
"""datetime.strptime format for parsing date strings; Configured by environment of same name, **DATE_FORMAT**"""
GUI_WIDTH = None
"""Width of main Graphical User Interface window; Configured by environment variable of same name, **GUI_WIDTH**"""
GUI_HEIGHT = None
"""Height of main Graphical User Interface window; Configured by environment variable of same name, **GUI_HEIGHT**."""
FRONTIER_STEPS = None
"""Number of data points used to trace out the efficient frontier; Configured by environment variable of same name, **FRONTIER_STEPS** """
MA_1_PERIOD = None
"""Number of data points in first moving average period; Configured by environment variable, **MA_1**"""
MA_2_PERIOD = None
"""Number of data points in second moving average period; Configured by environment variable, **MA_2**"""
MA_3_PERIOD = None
"""Number of data points in third moving average period; Configured by environment variable, **MA_3***"""
ITO_STEPS = None
"""Number of iterations used to approximate an Ito integral; Configured by environment variable of same name, **ITO_STEPS**"""
DEFAULT_ANALYSIS_PERIOD = None
"""Number of days used in a historical sample, if no date range is specified; Configured by environment variable of same name, **DEFAULT_ANALYSIS_PERIOD**"""

try:
    DATE_FORMAT = str(os.environ.setdefault('DATE_FORMAT', '%Y-%m-%d'))
except (ValueError, TypeError) as ParseError:
    logger.debug(
        'Failed to parse DATE_FORMAT from environment. Setting to default value of 1024.')
    DATE_FORMAT = '%Y-%m-%d'
    os.environ['GUI_WIDTH'] = '%Y-%m-%d'

try:
    GUI_WIDTH = int(os.environ.setdefault('GUI_WIDTH', '1024'))
except (ValueError, TypeError) as ParseError:
    logger.debug(
        'Failed to parse GUI_WIDTH from environment. Setting to default value of 1024.')
    GUI_WIDTH = 1024
    os.environ['GUI_WIDTH'] = '1024'

try:
    GUI_HEIGHT = int(os.environ.setdefault('GUI_HEIGHT', '768'))
except (ValueError, TypeError) as ParseError:
    logger.debug(
        'Failed to parse GUI_HEIGHT from enviroment. Setting to default value of 768.')
    GUI_HEIGHT = 768
    os.environ['GUI_HEIGHT'] = '768'

# FINANCIAL ALGORITHM CONFIGURATION
try:
    FRONTIER_STEPS = int(os.environ.setdefault('FRONTIER_STEPS', '5'))
except (ValueError, TypeError) as ParseError:
    logger.debug(
        'Failed to parse FRONTIER_STEPS from enviroment. Setting to default value of 5.')
    FRONTIER_STEPS = 5
    os.environ['FRONTIER_STEPS'] = '5'

try:
    MA_1_PERIOD = int(os.environ.setdefault('MA_1', '20'))
except (ValueError, TypeError) as ParseError:
    logger.debug(
        'Failed to parse MA_1 from environment. Setting to default value of 20.')
    MA_1_PERIOD = 20
    os.environ['MA_1'] = '20'

try:
    MA_2_PERIOD = int(os.environ.setdefault('MA_2', '60'))
except (ValueError, TypeError) as ParseError:
    logger.debug(
        'Failed to parse MA_2 from environment. Setting to default value of 60.')
    MA_2_PERIOD = 60
    os.environ['MA_2'] = '60'

try:
    MA_3_PERIOD = int(os.environ.setdefault('MA_3', '100'))
except (ValueError, TypeError) as ParseError:
    logger.debug(
        'Failed to parse MA_3 from environment. Setting to default value of 100.')
    MA_3_PERIOD = 100
    os.environ['MA_3'] = '100'

try:
    ITO_STEPS = int(os.environ.setdefault('ITO_STEPS', '10000'))
except (ValueError, TypeError) as ParseError:
    logger.debug(
        'Failed to parse ITO_STEPS from environment. Setting to default of 10000.')
    ITO_STEPS = 10000
    os.environ['ITO_STEPS'] = '10000'

try:
    DEFAULT_ANALYSIS_PERIOD = int(
        os.environ.setdefault('DEFAULT_ANALYSIS_PERIOD', '100'))
except (ValueError, TypeError) as ParseError:
    logger.debug(
        'Failed to parse DEFAULT_ANALYSIS_PERIOD from environment. Setting to default of 100.')
    DEFAULT_ANALYSIS_PERIOD = 100
    os.environ['DEFAULT_ANALYSIS_PERIOD'] = 100

RISK_FREE_RATE = os.environ.setdefault("RISK_FREE", "TEN_YEAR").strip("\"")
"""Maturity of the US Treasury Yield Curve used as a proxy for the risk free rate"""

MARKET_PROXY = os.environ.setdefault('MARKET_PROXY', 'SPY')
"""Ticker symbol used as a proxy for the overall market rate of return"""

ANALYSIS_MODE = os.environ.setdefault('ANALYSIS_MODE', 'geometric')
"""Determines the asset price process and thus, the underlying probability distribution of an asset's return"""

ESTIMATION_METHOD = os.environ.setdefault(
    'DEFAULT_ESTIMATION_METHOD', 'moments')
"""Determines the default estimation method using in statistical estimations"""

# SERVICE CONFIGURATION
# PRICE_MANAGER CONFIGRUATION
PRICE_MANAGER = os.environ.setdefault('PRICE_MANAGER', 'alpha_vantage')
"""Determines the service used to retrieve price data"""

AV_KEY = None
"""API Key used to query *AlphaVantage* service."""

# ALPHAVANTAGE CONFIGURATION
if PRICE_MANAGER == 'alpha_vantage':
    AV_URL = os.environ.setdefault(
        'ALPHA_VANTAGE_URL', 'https://www.alphavantage.co/query').strip("\"").strip("'")
    AV_CRYPTO_LIST = os.environ.setdefault(
        'ALPHA_VANTAGE_CRYPTO_META_URL', 'https://www.alphavantage.co/digital_currency_list/')

    AV_KEY = os.environ.setdefault('ALPHA_VANTAGE_KEY', None)

    if AV_KEY is None:
        keystore = os.path.join(COMMON_DIR, f'ALPHA_VANTAGE_KEY.{FILE_EXT}')
        if os.path.isfile(keystore):
            with open(keystore, 'r') as infile:
                if FILE_EXT == "json":
                    AV_KEY = json.load(infile)['ALPHA_VANTAGE_KEY']
                    os.environ['ALPHA_VANTAGE_KEY'] = str(AV_KEY)

# STAT_MANAGER CONFIGURATION
STAT_MANAGER = os.environ.setdefault('STAT_MANAGER', 'quandl')
"""Determines the service used to retrieve statistics data"""

Q_KEY = None
"""API Key used to query *Quandl/Nasdaq* service"""

# QUANDL CONFIGURAITON
if STAT_MANAGER == "quandl":
    Q_URL = os.environ.setdefault(
        'QUANDL_URL', 'https://www.quandl.com/api/v3/datasets').strip("\"").strip("'")
    Q_META_URL = os.environ.setdefault(
        'QUANDL_META_URL', 'https://www.quandl.com/api/v3/databases')

    Q_KEY = os.environ.setdefault('QUANDL_KEY', None)

    if Q_KEY is None:
        keystore = os.path.join(COMMON_DIR, f'QUANDL_KEY.{FILE_EXT}')
        if os.path.isfile(keystore):
            with open(keystore, 'r') as infile:
                if FILE_EXT == "json":
                    Q_KEY = json.load(infile)['QUANDL_KEY']
                    os.environ['QUANDL_KEY'] = str(Q_KEY)

# DIVIDEND_MANAGER CONFIGURATION
DIV_MANAGER = os.environ.setdefault("DIV_MANAGER", 'iex')
"""Determines the service used to retrieve dividends data"""

IEX_KEY = None
"""API Key used to query IEX service"""

if DIV_MANAGER == "iex":
    IEX_URL = os.environ.setdefault(
        "IEX_URL", 'https://cloud.iexapis.com/stable/stock')

    IEX_KEY = os.environ.setdefault("IEX_KEY", None)

    if IEX_KEY is None:
        keystore = os.path.join(COMMON_DIR, f'IEX_KEY.{FILE_EXT}')
        if os.path.isfile(keystore):
            with open(keystore, 'r') as infile:
                if FILE_EXT == "json":
                    IEX_KEY = json.load(infile)['IEX_KEY']
                    os.environ['IEX_KEY'] = str(IEX_KEY)


def q_key() -> str:
    """Wraps access to the `scrilla.settings.Q_KEY` in an `scrilla.settings.APIKeyError`. Exception is thrown if `scrilla.settings.Q_KEY` cannot be parsed from the environment or the local data directory.

    Raises
    ------
    1. **scrilla.settings.APIKeyError**
    """
    if not Q_KEY:
        raise APIKeyError(
            'Quandl API Key not found. Either set QUANDL_KEY environment variable or use "-store" CLI function to save key.')
    return Q_KEY


def iex_key() -> str:
    """Wraps access to the `scrilla.settings.IEX_KEY` in an `scrilla.settings.APIKeyError`. Exception is thrown if `scrilla.settings.IEX_KEY` cannot be parsed from the environment or the local data directory

    Raises
    ------
    1. **scrilla.settings.APIKeyError**
    """
    if not IEX_KEY:
        raise APIKeyError(
            'IEX API Key cannot be found. Either set IEX_KEY environment variable or use "-store" CLI function to save key.')
    return IEX_KEY


def av_key() -> str:
    """Wraps access to the `scrilla.settings.AV_KEY` in an `scrilla.settings.APIKeyError`. Exception is thrown if `scrilla.settings.AV_KEY` cannot be parsed from the environment or the local data directory

    Raises
    ------
    1. **scrilla.settings.APIKeyError**
    """
    if not AV_KEY:
        raise APIKeyError(
            'Alpha Vantage API Key not found. Either set ALPHA_VANTAGE_KEY environment variable or use "-store" CLI function to save key.')
    return AV_KEY
