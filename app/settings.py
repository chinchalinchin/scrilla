import sys, os, json, dotenv

from PyQt5.QtWidgets import QApplication, QWidget, QInputDialog, QLineEdit

import util.helper as helper
import util.tester as tester
import util.logger as logger


output = logger.Logger('app.settings')

# SETTINGS.PY

## APPLICATION CONFIGURATOIN

APP_NAME="PYNANCE"

VERSION="0.0.1"

APP_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

ENVIRONMENT = os.environ.setdefault('ENVIRONMENT', 'local')

dotenv.load_dotenv(os.path.join(APP_DIR,'.env'))

CONFIG_FILE = os.path.join(APP_DIR,'static', 'creds','config.json')

if helper.is_non_zero_file(CONFIG_FILE):
    with open(CONFIG_FILE, 'r') as infile:
        credential_overrides = json.load(infile)
else:
    credential_overrides = None

    # NOTE: CACHE only supports JSON currently. Future file extensions: csv and txt.
CACHE_DIR = os.path.join(APP_DIR, 'cache')
CACHE_STAT_KEY = "statistics"
CACHE_EXT = "json"

STATIC_DIR = os.path.join(APP_DIR, 'static')
STATIC_EXT = "json"

STATIC_TICKERS_FILE = os.path.join(STATIC_DIR, f'tickers.{STATIC_EXT}')
STATIC_ECON_FILE = os.path.join(STATIC_DIR, f'economics.{STATIC_EXT}')
STATIC_CRYPTO_FILE = os.path.join(STATIC_DIR, f'crypto.{STATIC_EXT}')

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

DENOMINATION = "USD"

ASSET_EQUITY="equity"
ASSET_CRYPTO="crypto"
STAT_ECON="indicator"

## SERVICE CONFIGURATION

INIT= True if os.getenv('INIT').lower() == 'true' else False

### PRICE_MANAGER CONFIGRUATION
PRICE_MANAGER = os.getenv('PRICE_MANAGER')

#### ALPHAVANTAGE CONFIGURATION
if PRICE_MANAGER == 'alpha_vantage':
    AV_URL = os.getenv('ALPHA_VANTAGE_URL').strip("\"").strip("'")

    # Grab AV API Key From config.json or .env if config.json doesn't exist
    if credential_overrides:
        try:
            AV_KEY = credential_overrides['ALPHA_VANTAGE_KEY']
        except:
            AV_KEY = None
            output.debug('Unable to parse ALPHA_VANTAGE_KEY from config.json file')
            try:
                AV_KEY = os.getenv('ALPHA_VANTAGE_KEY')
            except:
                AV_KEY = None
                output.debug('Unable to parse ALPHA_VANTAGE_KEY from .env file')
    else:
        try:
            AV_KEY = os.getenv('ALPHA_VANTAGE_KEY')
        except:
            AV_KEY = None
            output.debug('Unable to parse ALPHA_VANTAGE_KEY from .env file')

    # Verify API Key works
    if AV_KEY is not None:
        output.debug('Verifying ALPHA_VANTAGE API Key')
        unverified = not tester.test_av_key(AV_KEY)

    else:
        unverified = True

    new_creds = None
    while unverified:
        output.comment('Unable to verify ALPHA_VANTAGE API Key.')
        output.comment('Please register at https://www.alphavantage.co/ and place API Key in .env or config.json')
        
        app = QApplication([])
        widget, popup = QWidget(), QInputDialog()
        widget.resize(POPUP_WIDTH, POPUP_HEIGHT)

        text, okPressed = popup.getText(widget, "AlphaVantage API Key",
                                        "No AlphaVantage API Key found within application. \n Please register at https://www.alphavantage.co/ for an API Key and enter here:", QLineEdit.Normal, "")
        
        widget, popup = None, None
        app.exit()
        app = None

        unverified = not tester.test_av_key(text)

        if not unverified:
            new_creds = { 'ALPHA_VANTAGE_KEY' : text }

    if credential_overrides is not None and new_creds is not None and 'QUANDL_KEY' in credential_overrides:
        new_creds['QUANDL_KEY'] = credential_overrides['QUANDL_KEY']

        with open(CONFIG_FILE, 'w') as outfile:
            json.dump(new_creds, outfile)

    # Metadata Endpoints
    AV_CRYPTO_LIST=os.getenv('ALPHA_VANTAGE_CRYPTO_META_URL')
    
    # Response Keys
    AV_RES_EQUITY_FIRST_LAYER='Time Series (Daily)'
    AV_RES_EQUITY_CLOSE_PRICE="4. close"
    AV_RES_EQUITY_KEY="symbol"
    AV_RES_CRYPTO_FIRST_LAYER='Time Series (Digital Currency Daily)'
    AV_RES_CRYPTO_KEY="currency code"
    AV_RES_CRYPTO_CLOSE_PRICE=f'4a. close ({DENOMINATION})'
    AV_RES_ERROR='Error Message'
    AV_RES_LIMIT='Note'
    
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

    if credential_overrides:
        try:
            Q_KEY = credential_overrides['QUANDL_KEY']
        except:
            Q_KEY = None
            output.debug('Unable to parse QUANDL_KEY from config.json file')
            try:
                Q_KEY = os.getenv('QUANDL_KEY')
            except:
                Q_KEY = None
                output.debug('Unable to parse QUANDL_KEY from .env file')
    else:
        try:
            Q_KEY = os.getenv('QUANDL_KEY')
        except:
            Q_KEY = None
            output.debug('Unable to parse QUANDL_KEY from .env file')

    if Q_KEY is not None:
        output.debug('Verifying QUANDL API Key')
        unverified = not tester.test_q_key(Q_KEY)
    else:
        unverified = True

    new_creds = None
    while unverified:
        output.comment('Unable to verify QUANDL API Key.')
        output.comment('Please register at https://www.quandl.com/ and place API Key in .env or config.json')
        
        app = QApplication([])
        widget, popup = QWidget(), QInputDialog()
        widget.resize(POPUP_WIDTH, POPUP_HEIGHT)

        text, okPressed = popup.getText(widget, "Quandl API Key",
                                        "No Quandl API Key detectedin application. \n Please register at https://www.quandl.com/ for an API Key and enter here:", QLineEdit.Normal, "")
        
        widget, popup = None, None
        app.exit()
        app = None

        unverified = not tester.test_q_key(text)

        if not unverified:
            new_creds = { 'QUANDL_KEY' : text }

    if credential_overrides is not None and new_creds is not None and 'ALPHA_VANTAGE_KEY' in credential_overrides:
        new_creds['ALPHA_VANTAGE_KEY'] = credential_overrides['ALPHA_VANTAGE_KEY']

        with open(CONFIG_FILE, 'w') as outfile:
            json.dump(new_creds, outfile)

    # Metadata Endpoints
    Q_META_URL = os.getenv('QUANDL_META_URL')

    # Response Keys
    Q_FIRST_LAYER="dataset"
    Q_SECOND_LAYER="data"
    Q_RES_STAT_KEY="code"
    Q_RES_STAT_ZIP_KEY="FRED_metadata.csv"
    
    # Special Endpoints
    ENDPOINT_Q_YIELD_CURVE = {
        '3-Month': 'DTB3',
        '5-Year': 'DGS5',
        '10-Year': 'DGS10',
        '30-Year': 'DGS30'
    }
    
    # Path Paramaters
    PATH_Q_FRED ="FRED"
    
    # Query Parameters
    PARAM_Q_KEY="api_key"
    PARAM_Q_METADATA="metadata.json"
    PARAM_Q_START="start_date"
    PARAM_Q_END="end_date"