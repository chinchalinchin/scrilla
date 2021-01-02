import os, json, dotenv
import util.logger as logger

output = logger.Logger('app.settings')

#### APPLICATION CONFIGURATOIN

APP_NAME="PYNANCE"

VERSION="0.0.1"

APP_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

ENVIRONMENT = os.environ.setdefault('ENVIRONMENT', 'local')

dotenv.load_dotenv(os.path.join(APP_DIR,'.env'))

CONFIG_FILE = os.path.join(APP_DIR,'config.json')

if os.path.isfile(CONFIG_FILE):
    with open(CONFIG_FILE, 'r') as infile:
        credential_overrides = json.load(infile)
else:
    credential_overrides = None

DEBUG= True if os.getenv('DEBUG').lower() == 'true' else False
VERBOSE= True if os.getenv('VERBOSE').lower() == 'true' else False

CACHE_DIR = os.path.join(APP_DIR, 'cache')

STATIC_DIR = os.path.join(APP_DIR, 'static')

STATIC_TICKERS_FILE = os.path.join(STATIC_DIR, "tickers.json")
STATIC_ECON_FILE = os.path.join(STATIC_DIR, "economics.json")
STATIC_CRYPTO_FILE = os.path.join(STATIC_DIR, "crypto.json")

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

AV_URL = os.getenv('ALPHA_VANTAGE_URL').strip("\"").strip("'")

if credential_overrides:
    try:
        AV_KEY = credential_overrides['ALPHA_VANTAGE_KEY']
    except:
        AV_KEY = None
        output.debug('Unable to parse ALPHA_VANTAGE_KEY from config.json file')
else:
    try:
        AV_KEY = os.getenv('ALPHA_VANTAGE_KEY')
    except:
        AV_KEY = None
        output.debug('Unable to parse ALPHA_VANTAGE_KEY from .env file')
if AV_KEY is not None:
    # TODO: test URL
    # if fails, set to None
    pass
if AV_KEY is None:
    # TODO: Prompt user to register and enter key, save in config.json
    pass

Q_URL = os.getenv('QUANDL_URL').strip("\"").strip("'")
if credential_overrides:
    try:
        Q_KEY = credential_overrides['QUANDL_KEY']
    except:
        Q_KEY = None
        output.debug('Unable to parse QUANDL_KEY from config.json file')
else:
    try:
        Q_KEY = os.getenv('QUANDL_KEY')
    except:
        Q_KEY = None
        output.debug('Unable to parse QUANDL_KEY from .env file')
if Q_KEY is not None:
    # TODO: test URL
    # if fails, set to None
    pass
if Q_KEY is None:
    # TODO: Prompt user to register and enter key, save in config.json
    pass

PRICE_MANAGER = os.getenv('PRICE_MANAGER')
STAT_MANAGER = os.getenv('STAT_MANAGER')

INIT= True if os.getenv('INIT').lower() == 'true' else False

INVESTMENT_MODE = True if os.getenv('INVESTMENT_MODE').lower() == 'true' else False

#### FINANCIAL CONFIGURATION

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

#### SERVICE CONFIGURATION

if PRICE_MANAGER == "alpha_vantage":
    AV_CRYPTO_LIST=os.getenv('ALPHA_VANTAGE_CRYPTO_META_URL')
    # Response Keys
    AV_RES_EQUITY_FIRST_LAYER='Time Series (Daily)'
    AV_RES_EQUITY_CLOSE_PRICE="4. close"
    AV_RES_EQUITY_KEY="symbol"
    AV_RES_CRYPTO_FIRST_LAYER='Time Series (Digital Currency Daily)'
    AV_RES_CRYPTO_KEY="currency code"
    AV_RES_CRYPTO_CLOSE_PRICE=f'4a. close ({DENOMINATION})'
    # Query Parameters
    PARAM_AV_TICKER="symbol"
    PARAM_AV_FUNC="function"
    PARAM_AV_DENOM="market"
    PARAM_AV_KEY="apikey"
    # Query Arguments
    ARG_AV_FUNC_EQUITY_DAILY="TIME_SERIES_DAILY"
    ARG_AV_FUNC_EQUITY_LISTINGS="LISTING_STATUS"
    ARG_AV_FUNC_CRYPTO_DAILY="DIGITAL_CURRENCY_DAILY"

if STAT_MANAGER == "quandl":
    Q_META_URL = os.getenv('QUANDL_META_URL')
    # Response Keys
    Q_FIRST_LAYER="dataset"
    Q_SECOND_LAYER="data"
    Q_RES_STAT_KEY="code"
    Q_RES_STAT_ZIP_KEY="FRED_metadata.csv"
    # Path Paramaters
    PATH_Q_FRED ="FRED"
    # Query Parameters
    PARAM_Q_KEY="api_key"
    PARAM_Q_METADATA="metadata.json"

#### PLOTTING CONFIGURAITON

BAR_WIDTH = 0.10