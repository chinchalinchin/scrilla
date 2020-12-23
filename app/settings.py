import os, dotenv

APP_NAME="PYNANCE"

APP_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

dotenv.load_dotenv(os.path.join(APP_DIR,'.env'))

BUFFER_DIR = os.path.join(APP_DIR, 'cache')

AV_QUERY_URL = os.getenv('AV_QUERY_URL')

PRICE_MANAGER = "alpha_vantage"

DEBUG= True if os.getenv('DEBUG') == 'True' else False

INVESTMENT_MODE = True if os.getenv('INVESTMENT_MODE') == 'True' else False

ONE_TRADING_DAY=(1/252)

SEPARATER="-"

LINE_LENGTH=100

INDENT=10

HELP_MSG="A financial application written in python to determine optimal portfolio allocations subject to various constraints and calculate various statistics concerning a given portfolio allocation."

SYNTAX="command -OPTION [tickers] (additional input)"

FUNC_ARG_DICT={
    "correlation":"-cor",
    "efficient_frontier": "-ef",
    "examples": "-ex",
    "help": "-help",
    "minimize_variance": "-min",
    "maximize_return": "-max",
    "optimize_portfolio": "-opt",
    "risk_return" : "-rr",
}

FUNC_DICT={
    "correlation": "Calculate pair-wise correlation for the supplied list of ticker symbols.",
    "efficient_frontier": "Generate a plot of the portfolio's efficient frontier for the supplied list of tickers. The number of points in the plot must be specified by the last argument.",
    "examples":"Display examples of syntax.",
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
    'python ./main.py -ef QS DIS RUN 5': 'Calculate a five point plot of the efficient portfolio (risk, return) frontier for the portfolio composed of (QS, DIS, RUN)'
}
