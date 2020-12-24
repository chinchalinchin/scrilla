import os, dotenv
import util.logger as logger


output = logger.Logger('app.settings')

APP_NAME="PYNANCE"

APP_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

dotenv.load_dotenv(os.path.join(APP_DIR,'.env'))

CACHE_DIR = os.path.join(APP_DIR, 'cache')

AV_URL = os.getenv('ALPHA_VANTAGE_URL')
AV_KEY = os.getenv('ALPHA_VANTAGE_KEY')

Q_URL = os.getenv('QUANDL_URL')
Q_KEY = os.getenv('QUANDL_KEY')

PRICE_MANAGER = os.getenv('PRICE_MANAGER')
STAT_MANAGER = os.getenv('STAT_MANAGER')

if PRICE_MANAGER == "alpha_vantage":
    # Response Keys
    AV_FIRST_LAYER='Time Series (Daily)'
    CLOSE_PRICE="4. close"
    # Query Parameters
    PARAM_TICKER="symbol"
    PARAM_FUNC="function"
    PARAM_AV_KEY="apikey"
    # Query Arguments
    ARG_FUNC_DAILY="TIME_SERIES_DAILY"

if STAT_MANAGER == "quandl":
    # Response Keys
    Q_FIRST_LAYER="dataset"
    Q_SECOND_LAYER="data"
    # Query Parameters
    PARAM_Q_KEY="api_key"

DEBUG= True if os.getenv('DEBUG').lower() == 'true' else False

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

SEPARATER="-"

LINE_LENGTH=100

INDENT=10

BAR_WIDTH=0.10

HELP_MSG="A financial application written in python to determine optimal portfolio allocations subject to various constraints and calculate fundamental statistics concerning a given portfolio allocation. Note: all calculations are based on an equity's closing price for the past 100 trading days. "

SYNTAX="command -OPTION [tickers] (additional input)"

FUNC_ARG_DICT={
    "correlation":"-cor",
    "economic_statistics": "-ec",
    "efficient_frontier": "-ef",
    "examples": "-ex",
    "help": "-help",
    "maximize_return": "-max",
    "minimize_variance": "-min",
    "moving_averages": "-mov",
    "optimize_portfolio": "-opt",
    "plot_frontier": "-pef",
    "plot_moving_averages": "-pmv",
    "risk_return" : "-rr",
}

FUNC_DICT={
    "correlation": "Calculate pair-wise correlation for the supplied list of ticker symbols.",
    "economic_statistics": "Retrieve the latest value for the supplied list of economic indicators. The available list of economic indicators can be found at https://www.quandl.com/data/FRED-Federal-Reserve-Economic-Data/documentation?anchor=growth",
    "efficient_frontier": "Generate a sample of the portfolio's efficient frontier for the supplied list of tickers.",
    "examples": "Display examples of syntax.",
    "help": "Print this help message.",
    "maximize_return": "Maximize the return of the portfolio defined by the supplied list of ticker symbols.",
    "minimize_variance": "Minimize the variance of the portfolio defined by the supplied list of ticker symbols.",
    "moving_averages": "Calculate the current moving averages ",
    "optimize_portfolio":"Optimize the variance of the portfolio's variance subject to the supplied return target. The target return must be specified by the last argument",
    "plot_frontier": "Generates a scatter plot graphic of the portfolio's efficient frontier for the supplied list of tickers.",
    "plot_moving_averages": "Generates a grouped bar chart of the moving averages for each equity in the supplied list of tickers.",
    "risk_return": "Calculate the risk-return profile for the supplied list of ticker symbols.",
}

EXAMPLES = { 
    'python ./main.py -rr GOOG AMZN XOM AAPL': 'Calculate the risk-return profile for each equity in the portfolio composed of (GOOG, AMZN, XOM, APPL)',
    'python ./main.py -cor GLD SPY SLV UUP TLT EWA': 'Calculate the correlation matrix for the portfolio composed of (GLD, SPY, SLV, UUP, TLT, EWA',
    'python ./main.py -min U TSLA SPCE': 'Find the portfolio allocation that minimizes the overall variance of the portfolio composed of (U, TSLA, SPCE). ',
    'python ./main.py -opt ALLY FB PFE SNE BX 0.83': 'Optimize the portfolio consisting of (ALLY, FB, PFE, SNE, BX) subject to the constraint their mean annual return equal 83%. Note the constrained return must reside within the feasible region of returns, i.e. the constrained return must be less than the maximum possible return.',  
    'python ./main.py -ef QS DIS RUN': 'Calculate a five point sample of the efficient portfolio (risk, return) frontier for the portfolio composed of (QS, DIS, RUN). The number of points generated in the sample can be altered through the FRONTIER_STEPS environment variable.',
    'python ./main.py -pef QQQ SPY DIA': 'Generate a graphical display of the (QQQ, SPY, DIA) portolio\'s efficient (risk, return) frontier. The number of points generated in the sample can be altered through the FRONTIER_STEPS environment variable. Note, if the graphical display does not show up, you may need to configure matplotlib\'s backend to be compatible with your OS.',
    'python ./main.py -pmo QS ACI': 'Generate a graphical display of the current moving averages of the (QS, ACI) portolio. The length of moving average periods can be adjusted by the MA_1_PERIOD, MA_2_PERIOD and MA_3_PERIOD environment variables. Note, if the graphical display does not show up, you may need to configure matplotlib\'s backend to be compatible with your OS.'
}
