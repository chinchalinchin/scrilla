APP_NAME="scrilla"

SIG_FIGS=5

SEPARATER = "-"

LINE_LENGTH = 100

BAR_WIDTH = 0.10

INDENT = 10

RISK_FREE_TITLE = "10-Year US Treasury"

HELP_MSG = "A financial application written in python to determine optimal portfolio allocations subject to various constraints and to calculate fundamental statistics concerning a given portfolio allocation. Note: all calculations are based on an equity's closing price for the past 100 trading days. "

SYNTAX = "command -OPTIONS [tickers]"

TAB = "      "

FUNC_ARG_DICT = {
    "asset_type": "-asset",
    "capm_equity_cost": "-capm-equity",
    "capm_beta": "-capm-beta",
    "clear_cache": "-clear-cache",
    "clear_static": "-clear-static",
    "clear_watchlist": "-clear-watch",
    "close": "-close",
    "correlation":"-cor",
    "correlation_time_series": "-cors",
    "discount_dividend": "-ddm",
    "dividends": "-div",
    "efficient_frontier": "-ef",
    "examples": "-ex",
    "gui": "-gui",
    "help": "-help",
    "initialize": "-init-static",
    "list_watchlist": "-ls-watch",
    "maximize_return": "-max",
    "moving_averages": "-mov",
    "optimize_portfolio": "-opt",
    "plot_correlation": "-plot-cors",
    "plot_dividends": "-plot-div",
    "plot_frontier": "-plot-ef",
    "plot_moving_averages": "-plot-mov",
    "plot_risk_profile": "-plot-rr",
    "plot_yield_curve":"-plot-yield",
    "price_history": "-prices",
    "purge": "-purge",
    "risk_free_rate": "-rf",
    "risk_return" : "-rr",
    "screener": "-screen",
    "sharpe_ratio": "-sharpe",
    "statistic": "-stat",
    "statistic_history": "-stats",
    "watchlist": "-watch",
    "yield_curve": "-yield"
}

FUNC_XTRA_VALUED_ARGS_DICT = {
    'target': '-target',
    'save': '-save',
    'start_date': '-start',
    'end_date': '-end',
    'discount': '-discount',
    'model': '-model',
    'investment': '-invest',
    'steps': '-steps'
}

FUNC_XTRA_SINGLE_ARGS_DICT = {
    'optimize_sharpe': "-sh",
}

FUNC_DICT = {
    "asset_type": "Outputs the asset type for the supplied symbol.",
    
    "capm_equity_cost": "Computes the cost of equity according to CAPM for the supplied list of tickers. If no start or end dates are specified, calculations default to the last 100 days of prices. The environment variable MARKET_PROXY defines which ticker serves as a proxy for the market as whole. ADDITIONAL OPTIONS:  -start (format: \"YYYY-MM-DD\"), -end  (format :\"YYYY-MM-DD\")",

    "capm_beta": "Computes the market beta according to CAPM for the supplied list of tickers. If no start or end dates are specified, calculations default to the last 100 days of prices. The environment variable MARKET_PROXY defines which ticker serves as a proxy for the market as whole. ADDITIONAL OPTIONS:  -start (format: \"YYYY-MM-DD\"), -end  (format :\"YYYY-MM-DD\")",

    "clear_cache": "Clears the /data/cache/ directory of all data, outdated or not.",
    
    "clear_static": "Clears the /data/static directory of all data. Not recommended unless necessary. Static data takes a long time to reload.",

    "clear_watchlist": "Clears the /data/common/watchlist.json of all saved ticker symbols.",
    
    "close": "Return latest closing value for the supplied list of symbols (equity or crypto).",
    
    "correlation": "Calculate pair-wise correlation for the supplied list of ticker symbols. If no start or end dates are specified, calculations default to the last 100 days of prices. ADDITIONAL OPTIONS:  -start (format: \"YYYY-MM-DD\"), -end  (format :\"YYYY-MM-DD\")",
    
    "correlation_time_series": "EXPERIMENTAL. PROBABLY WON'T WORK. Calculate correlation for a pair of tickers over a specified date range. If no start or end dates are specified, the default analysis period of 100 days is applied. ADDITIONAL OPTIONS:  -start (format: \"YYYY-MM-DD\"), -end  (format :\"YYYY-MM-DD\")",

    "discount_dividend": "Extrapolates future dividend cashflows from historical dividend payments with linear regression and then uses that model to calculate the net present value of all future dividends. If no discount rate is specified, the calculations default to the risk-free rate, i.e. the 10-Year US Treasury yield. ADDITIONAL OPTIONS: -discount (float)",
    
    "dividends": "Displays the price history over the specific date range. If no dates are provided, returns the entire dividend history. -start (format: \"YYYY-MM-DD\"), -end  (format :\"YYYY-MM-DD\")",

    "efficient_frontier": "Generate a sample of the portfolio's efficient frontier for the supplied list of tickers. By default, the efficient frontier will minimize a portfolio's volality for a given rate of return. The number of points calculated in the efficient frontier can be specifed as an integer with the -steps. If no -steps is provided, the value of the environment variable FRONTIER_STEPS will be used. ADDITIONAL OPTIONS: -steps (format: integer), -invest (format: float), -start (format: \"YYYY-MM-DD\"), -end  (format :\"YYYY-MM-DD\"), -save (format: /path/to/file/filename.json)",
    
    "examples": "Display examples of syntax.",
    
    "gui": "Brings up a Qt GUI for the application (work in progress!)",
    
    "help": "Print this help message.",
    
    "initialize": "Initializes the data in the /static/ directory. Local application automatically initializes this data. This option is used to initialize static data inside of a Docker container, where the application entrypoint doesn't invoke the CLI automatically.",
    
    "maximize_return": "Maximize the return of the portfolio defined by the supplied list of ticker symbols. Returns an array representing the allocations to be made for each asset in a portfolio. If no start or end dates are specified, calculations default to the last 100 days of prices. You can specify an investment with the '-invest' flag, otherwise the result will be output in percentage terms. Note: This function will always allocate 100% to the asset with the highest return. It's a good way to check and see if there are bugs in the algorithm after changes. ADDITIONAL OPTIONS:  -start (format: \"YYYY-MM-DD\"), -end  (format :\"YYYY-MM-DD\"), -invest (format: float)",
    
    "list_watchlist": "Lists the equity symbols currently saved to your watchlist.",
    
    "moving_averages": "Calculate the current moving averages. If no start or end dates are specified, calculations default to the last 100 days of prices. ADDITIONAL OPTIONS:  -start (format: \"YYYY-MM-DD\"), -end  (format :\"YYYY-MM-DD\")",
    
    "optimize_portfolio": "Optimize the volatility of the portfolio\'s variance subject to the supplied return target.  Returns an array representing the allocations to be made for each asset in a portfolio. The target return must be specified with the '-target' flag. If no target return is specified, the portfolio's volatility is minimized. If no start or end dates are specified with the '-start' and '-end' flags, calculations default to the last 100 days of prices. You can specify an investment with the '-invest' flag, otherwise the result will be output in percentage terms. If the -sh flag is specified, the function will maximize the portfolio's sharpe ratio instead of minimizing it's volatility. ADDITIONAL OPTIONS:  -start (format: \"YYYY-MM-DD\"), -end  (format :\"YYYY-MM-DD\"), -target (format: decimal), -invest (format: float), -save (format: /path/to/file/filename.json), -sh (binary flag; no format. include it or don't.)",
    
    "plot_correlation": "EXPERIMENTAL. PROBABLY WON'T WORK. Generates a time series for the correlation of two ticker symbols over the specified date range. ADDITIONAL OPTIONS:  -start (format: \"YYYY-MM-DD\"), -end  (format :\"YYYY-MM-DD\"), -save (format: /path/to/file/filename.jpeg)",

    "plot_dividends": "Generates a scatter plot graphic of the dividend history for the supplied list of tickers with a superimposed simple linear regression line. ADDITIONAL OPTIONS: -save (format: /path/to/file/filename.jpeg)",
    
    "plot_frontier": "Generates a scatter plot graphic of the portfolio\'s efficient frontier for the supplied list of tickers. Not available when running inside of a Docker container.The number of points calculated in the efficient frontier can be specifed as an integer with the -steps. If no -steps is provided, the value of the environment variable FRONTIER_STEPS will be used. ADDITIONAL OPTIONS: -start (format: \"YYYY-MM-DD\"), -end  (format :\"YYYY-MM-DD\"), -save (format: /path/to/file/filename.jpeg), -steps (format: integer)",
    
    "plot_moving_averages": "Generates a grouped bar chart of the moving averages for each equity in the supplied list of ticker symbols. Not available when running inside of a Docker container. If no start or end dates are specified, calculations default to the last 100 days of prices. ADDITIONAL OPTIONS:  -start (format: \"YYYY-MM-DD\"), -end  (format :\"YYYY-MM-DD\"), -save (format: /path/to/file/filename.jpeg)",
    
    "plot_risk_profile": "Generates a scatter plot of the risk-return profile for symbol in the supplied list of ticker symbols. If no start or end dates are specified, calculations default to the last 100 days of prices. ADDITIONAL OPTIONS:  -start (format: \"YYYY-MM-DD\"), -end  (format :\"YYYY-MM-DD\"), -save (format: /path/to/file/filename.jpeg",

    "plot_yield_curve": "Generates a plot of the United States Treasury Yield Curve using the Federal Funds Rate, the 3-Month Rate, the 3-Year Rate, the 5-Year Rate, the 10-Year Rate and the 30-Year Rate. ADDITIONAL OPTIONS:  -start (format: \"YYYY-MM-DD\"), -end  (format :\"YYYY-MM-DD\"), -save (format: /path/to/file/filename.jpeg",
    
    "price_history": "Prints the price histories for each inputted asset over the specified date range. If no date range is given, price histories will default to the last 100 days. -start (format: \"YYYY-MM-DD\"), -end  (format :\"YYYY-MM-DD\"), -save (format: /path/to/file/filename.json)",

    "purge": "Removes all files contained with the /static/ and /cache/ directory, but retains the directories themselves.",
    
    "risk_free_rate": "Returns current 10-year, annualized US Treasury yield.",
    
    "risk_return": "Calculate the risk-return profile for the supplied list of ticker symbols. If no start or end dates are specified, calculations default to the last 100 days of prices. ADDITIONAL OPTIONS:  -start (format: \"YYYY-MM-DD\"), -end  (format :\"YYYY-MM-DD\"), -save (format: /path/to/file/filename.json)",
    
    "screener": "Searchs equity spot prices that trade at a discount to the provided model. If no model is provided, the screener will default to the Discount Dividend Model. If no discount rate is provided, the screener will default to the cost of equity for a ticker calculated using the CAPM model and the ticker defined by environment variable MARKET_PROXY as a proxy for the market. ADDITION OPTIONS: -discount (format: decimal), -model (format: string, values: ddm)",
    
    "sharpe_ratio": "Computes the sharpe ratio for each of the supplied tickers. ADDITIONAL OPTIONS:  -start (format: \"YYYY-MM-DD\"), -end  (format :\"YYYY-MM-DD\")", 

    "statistic": "Retrieves the latest value for the supplied list of economic statistics. The available list of economic statistic can be found at https://www.quandl.com/data/FRED-Federal-Reserve-Economic-Data/documentation?anchor=growth; it is also stored in the /static/ directory of the application ",
    
    "statistic_history": "Prints the statistic history for the supplied list of economic statistics. -save (format: /path/to/file/filename.jpeg)",

    "watchlist": "Saves the supplist list of tickers to your watchlist. These equity symbol are used by the screening algorithms when searching for stocks that trade at a discount.", 

    "yield_curve": "Displays the current United States Treasury Yield Curve using the Federal Funds Rate, the 3-Month Rate, the 3-Year Rate, the 5-Year Rate, the 10-Year Rate and the 30-Year Rate."

}

EXAMPLES = { 
    'scrilla -ls-watch': 'Lists the stocks in your watchlist.',

    'scrilla  -rr GOOG AMZN XOM AAPL': 'Calculate the risk-return profile for each equity in the portfolio composed of (GOOG, AMZN, XOM, APPL)',

    'scrilla  -cor GLD SPY SLV UUP TLT EWA': 'Calculate the correlation matrix for the portfolio composed of (GLD, SPY, SLV, UUP, TLT, EWA',

    'scrilla -opt U TSLA SPCE': 'Finds the portfolio allocation that minimizes the overall variance of the portfolio composed of (U, TSLA, SPCE). ',

    'scrilla -opt -target 0.83 ALLY FB PFE SNE BX': 'Optimize the portfolio consisting of (ALLY, FB, PFE, SNE, BX) subject to the constraint their mean annual return equal 83%. Note the constrained return must reside within the feasible region of returns, i.e. the constrained return must be less than the maximum possible return and greater than the minimum possible return.',  

    'scrilla -opt -sh -save /home/Desktop/max_sharpe_ratio.json LMT GD UPS MMM': 'Maximize the sharpe ratio of the portfolio consisting of (LMT, GD, UPS, MM) and ouput the portfolio allocation along with its risk-return profile to a json on the user Desktop.',

    'scrilla -ef QS DIS RUN': 'Calculate a five point sample of the efficient portfolio (risk, return) frontier for the portfolio composed of (QS, DIS, RUN). The number of points generated in the sample can be altered through the FRONTIER_STEPS environment variable.',

    'scrilla -plot-ef QQQ SPY DIA': "Generate a graphical display of the (QQQ, SPY, DIA) portolio\'s efficient (risk, return) frontier. The number of points generated in the sample can be altered through the FRONTIER_STEPS environment variable. Note, if the graphical display does not show up, you may need to configure matplotlib\'s backend to be compatible with your OS.",

    'scrilla -plot-mov -save /home/Desktop/moving_averages.jpeg QS ACI': "Generate a graphical display of the current moving averages of the (QS, ACI) portolio and saves it to the file named 'moving_averages.jpeg' located in the directory /home/Desktop/. The length of moving average periods can be adjusted by the MA_1_PERIOD, MA_2_PERIOD and MA_3_PERIOD environment variables. Note, if the graphical display does not show up, you may need to configure matplotlib\'s backend to be compatible with your OS.",

    'scrilla -ind GDP BASE MI': "Display the latest values for the supplied list of economic indicators.",

    'scrilla -close MSFT IBM FSLR NFLX BTC XRP': "Displays the last closing price for the supplied list of asset types",

    'scrilla -gui': "Launches a PyQt GUI into which the application functions have been wired. Note this does not work in containers.",

    'scrilla -screen -model DDM': 'Screens the equities in your watchlist for spot prices that trade at a discount to the specified moel',
    
    'scrilla -watch ATVI TTWO EA': 'Adds the portfolio (ATVI, TTWO, EA) to the existing ticker symbols in your equity watchlist'  
}
