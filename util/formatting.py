import os, dotenv

APP_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

dotenv.load_dotenv(os.path.join(os.path.join(APP_DIR, 'env'),'.env'))

APP_NAME="Pynance"

DEBUG= True if os.getenv('DEBUG').lower() == 'true' else False

VERBOSE= True if os.getenv('VERBOSE').lower() == 'true' else False

SIG_FIGS=5

SEPARATER = "-"

LINE_LENGTH = 100

BAR_WIDTH = 0.10

INDENT = 10

HELP_MSG = "A financial application written in python to determine optimal portfolio allocations subject to various constraints and to calculate fundamental statistics concerning a given portfolio allocation. Note: all calculations are based on an equity's closing price for the past 100 trading days. "

SYNTAX = "command -OPTIONS [tickers] (additional input)"

TAB = "      "
FUNC_ARG_DICT = {
    "asset_type": "-at",
    "clear_cache": "-clear",
    "close": "-close",
    "correlation":"-cor",
    "efficient_frontier": "-ef",
    "examples": "-ex",
    "gui": "-gui",
    "help": "-help",
    "indicator": "-ind",
    "initialize": "-init",
    "maximize_return": "-max",
    "minimize_variance": "-min",
    "moving_averages": "-mov",
    "optimize_portfolio": "-opt",
    "plot_frontier": "-plot-ef",
    "plot_moving_averages": "-plot-mov",
    "plot_risk_profile": "-plot-rr",
    "purge": "-pur",
    "risk_return" : "-rr",
    "server_local": "-local",
    "server_container": "-container"
}

FUNC_XTRA_ARGS_DICT = {
    'target': '-target',
    'save': '-save',
    'start_date': '-start',
    'end_date': '-end'
}

FUNC_DICT = {
    "asset_type": "Outputs the asset type for the supplied symbol.",
    "clear_cache": "Clears the /cache/ directory of all data, outdated or not.",
    "close": "Return latest closing value for the supplied list of symbols (equity or crypto).",
    "correlation": "Calculate pair-wise correlation for the supplied list of ticker symbols. ADDITIONAL OPTIONS:  -start (format: \"YYYY-MM-DD\"), -end  (format :\"YYYY-MM-DD\")",
    "efficient_frontier": "Generate a sample of the portfolio's efficient frontier for the supplied list of tickers.",
    "examples": "Display examples of syntax.",
    "gui": "Brings up a Qt GUI for the application (work in progress!)",
    "help": "Print this help message.",
    "indicator": "Retrieves the latest value for the supplied list of economic indicators. The available list of economic indicators can be found at https://www.quandl.com/data/FRED-Federal-Reserve-Economic-Data/documentation?anchor=growth; it is also stored in the /static/ directory of the application ",
    "initialize": "Initializes the data in the /static/ directory. Local application automatically initializes this data. This option is used to initialize static data inside of a Docker container, where the application entrypoint doesn't invoke the CLI automatically.",
    "maximize_return": "Maximize the return of the portfolio defined by the supplied list of ticker symbols.",
    "minimize_variance": "Minimize the variance of the portfolio defined by the supplied list of ticker symbols.",
    "moving_averages": "Calculate the current moving averages. ADDITIONAL OPTIONS:  -start (format: \"YYYY-MM-DD\"), -end  (format :\"YYYY-MM-DD\")",
    "optimize_portfolio":"Optimize the variance of the portfolio\'s variance subject to the supplied return target. The target return must be specified with the '-target' flag. ADDITIONAL OPTIONS:  -target (format: decimal)",
    "plot_frontier": "Generates a scatter plot graphic of the portfolio\'s efficient frontier for the supplied list of tickers. Not available when running inside of a Docker container. ADDITIONAL OPTIONS:  -save (format: /path/to/file/filename.jpeg)",
    "plot_moving_averages": "Generates a grouped bar chart of the moving averages for each equity in the supplied list of ticker symbols. Not available when running inside of a Docker container. ADDITIONAL OPTIONS:  -start (format: \"YYYY-MM-DD\"), -end  (format :\"YYYY-MM-DD\"), -save (format: /path/to/file/filename.jpeg)",
    "plot_risk_profile": "Generates a scatter plot of the risk-return profile for symbol in the supplied list of ticker symbols.ADDITIONAL OPTIONS:  -start (format: \"YYYY-MM-DD\"), -end  (format :\"YYYY-MM-DD\"), -save (format: /path/to/file/filename.jpeg",
    "purge": "Removes all files contained with the /static/ and /cache/ directory, but retains the directories themselves.",
    "risk_return": "Calculate the risk-return profile for the supplied list of ticker symbols. ADDITIONAL OPTIONS:  -start (format: \"YYYY-MM-DD\"), -end  (format :\"YYYY-MM-DD\")",
    "server_local": "Invokes 'python manage.py runserver' from /server/ directory. Configure .env file to change port.",
    "server_container": "Builds and runs a Docker image of the application on 'localhost'. Configure .env to change port."
}

EXAMPLES = { 
    'python ./main.py -rr GOOG AMZN XOM AAPL': 'Calculate the risk-return profile for each equity in the portfolio composed of (GOOG, AMZN, XOM, APPL)',
    'python ./main.py -cor GLD SPY SLV UUP TLT EWA': 'Calculate the correlation matrix for the portfolio composed of (GLD, SPY, SLV, UUP, TLT, EWA',
    'python ./main.py -min U TSLA SPCE': 'Find the portfolio allocation that minimizes the overall variance of the portfolio composed of (U, TSLA, SPCE). ',
    'python ./main.py -opt -target 0.83 ALLY FB PFE SNE BX': 'Optimize the portfolio consisting of (ALLY, FB, PFE, SNE, BX) subject to the constraint their mean annual return equal 83%. Note the constrained return must reside within the feasible region of returns, i.e. the constrained return must be less than the maximum possible return.',  
    'python ./main.py -ef QS DIS RUN': 'Calculate a five point sample of the efficient portfolio (risk, return) frontier for the portfolio composed of (QS, DIS, RUN). The number of points generated in the sample can be altered through the FRONTIER_STEPS environment variable.',
    'python ./main.py -plot-ef QQQ SPY DIA': "Generate a graphical display of the (QQQ, SPY, DIA) portolio\'s efficient (risk, return) frontier. The number of points generated in the sample can be altered through the FRONTIER_STEPS environment variable. Note, if the graphical display does not show up, you may need to configure matplotlib\'s backend to be compatible with your OS.",
    'python ./main.py -plot-mov -save /home/Desktop/moving_averages.jpeg QS ACI': "Generate a graphical display of the current moving averages of the (QS, ACI) portolio and saves it to the file named 'moving_averages.jpeg' located in the directory /home/Desktop/. The length of moving average periods can be adjusted by the MA_1_PERIOD, MA_2_PERIOD and MA_3_PERIOD environment variables. Note, if the graphical display does not show up, you may need to configure matplotlib\'s backend to be compatible with your OS.",
    'python ./main.py -ind GDP BASE MI': "Display the latest values for the supplied list of economic indicators.",
    'python ./main.py -close MSFT IBM FSLR NFLX BTC XRP': "Displays the last closing price for the supplied list of asset types",
    'python ./main.py -gui': "Launches a PyQt GUI into which the application functions have been wired."
}
