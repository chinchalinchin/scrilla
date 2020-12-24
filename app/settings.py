import os, dotenv
import util.logger as logger


output = logger.Logger('app.settings')

APP_NAME="PYNANCE"

APP_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

dotenv.load_dotenv(os.path.join(APP_DIR,'.env'))

CACHE_DIR = os.path.join(APP_DIR, 'cache')

AV_QUERY_URL = os.getenv('AV_QUERY_URL')

PRICE_MANAGER = os.getenv('PRICE_MANAGER')

DEBUG= True if os.getenv('DEBUG').lower() == 'true' else False

INVESTMENT_MODE = True if os.getenv('INVESTMENT_MODE').lower() == 'true' else False

try:
    FRONTIER_STEPS = int(os.getenv('FRONTIER_STEPS'))

except:
    output.debug('Failed to parse FRONTIER_STEPS from .env File. Please Ensure FRONTIER_STEPS is set to an integer value.')
    FRONTIER_STEPS = 5

try:
    MA_1 = int(os.getenv('MA_1'))
except: 
    output.debug('Failed to parse MA_1 from .env File. Please Ensure MA_1 is set to an integer value.')
    MA_1 = 20

try:
    MA_2 = int(os.getenv('MA_2'))
except: 
    output.debug('Failed to parse MA_2 from .env File. Please Ensure MA_2 is set to an integer value.')
    MA_2 = 60

try:
    MA_3 = int(os.getenv('MA_3'))
except: 
    output.debug('Failed to parse MA_3 from .env File. Please Ensure MA_3 is set to an integer value.')
    MA_1 = 100
      
ONE_TRADING_DAY=(1/252)

SEPARATER="-"

LINE_LENGTH=100

INDENT=10

HELP_MSG="A financial application written in python to determine optimal portfolio allocations subject to various constraints and calculate fundamental statistics concerning a given portfolio allocation. Note: all calculations are based on an equity's closing price for the past 100 trading days. "

SYNTAX="command -OPTION [tickers] (additional input)"

FUNC_ARG_DICT={
    "correlation":"-cor",
    "efficient_frontier": "-ef",
    "examples": "-ex",
    "frontier_plot": "-pef",
    "help": "-help",
    "minimize_variance": "-min",
    "maximize_return": "-max",
    "optimize_portfolio": "-opt",
    "risk_return" : "-rr",
}

FUNC_DICT={
    "correlation": "Calculate pair-wise correlation for the supplied list of ticker symbols.",
    "efficient_frontier": "Generate a sample of the portfolio's efficient frontier for the supplied list of tickers.",
    "examples": "Display examples of syntax.",
    "frontier_plot": "Generates a graphical plot of the portfolio's efficient frontier for the supplied list of tickers.",
    "help": "Print this help message.",
    "minimize_variance": 'Minimize the variance of the portfolio defined by the supplied list of ticker symbols.',
    "maximize_return": "Maximize the return of the portfolio defined by the supplied list of ticker symbols.",
    "optimize_portfolio":"Optimize the variance of the portfolio's variance subject to the supplied return target. The target return must be specified by the last argument",
    "risk_return": "Calculate the risk-return profile for the supplied list of ticker symbols.",
}

EXAMPLES = { 
    'python ./main.py -rr GOOG AMZN XOM AAPL': 'Calculate the risk-return profile for each equity in the portfolio composed of (GOOG, AMZN, XOM, APPL)',
    'python ./main.py -cor GLD SPY SLV UUP TLT EWA': 'Calculate the correlation matrix for the portfolio composed of (GLD, SPY, SLV, UUP, TLT, EWA',
    'python ./main.py -min U TSLA SPCE': 'Find the portfolio allocation that minimizes the overall variance of the portfolio composed of (U, TSLA, SPCE). ',
    'python ./main.py -opt ALLY FB PFE SNE BX 0.83': 'Optimize the portfolio consisting of (ALLY, FB, PFE, SNE, BX) subject to the constraint their mean annual return equal 83%. Note the constrained return must reside within the feasible region of returns, i.e. the constrained return must be less than the maximum possible return.',  
    'python ./main.py -ef QS DIS RUN': 'Calculate a five point sample of the efficient portfolio (risk, return) frontier for the portfolio composed of (QS, DIS, RUN). The number of points generated in the sample can be altered through the FRONTIER_STEPS environment variable.',
    'python ./main.py -pef QQQ SPY DIA': 'Generate a graphical display of the (QQQ, SPY, DIA) portolio\'s efficient (risk, return) frontier. The number of points generated in the sample can be altered through the FRONTIER_STEPS environment variable.'
}
