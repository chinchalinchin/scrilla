APP_NAME="scrilla"

SIG_FIGS=5

SEPARATER = "-"

LINE_LENGTH = 100

BAR_WIDTH = 0.10

INDENT = 10

RISK_FREE_TITLE = "{} US Treasury"

HELP_MSG = "A financial application written in python to determine optimal portfolio allocations subject to various constraints and to calculate fundamental statistics concerning a given portfolio allocation. Note: all calculations are based on an equity's closing price for the past 100 trading days. "

SYNTAX = "command -FUNCTION -OPTIONS [tickers]"

TAB = "      "

FUNC_ARG_DICT = {
    "asset_type": "-asset",
    "bs_cvar": "-bs-cvar",
    "bs_var": "-bs-var",
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
    "optimize_portfolio_variance": "-opt",
    "optimize_portfolio_conditional_var": "-opt-cvar",
    "plot_correlation": "-plot-cors",
    "plot_dividends": "-plot-div",
    "plot_frontier": "-plot-ef",
    "plot_moving_averages": "-plot-mov",
    "plot_risk_profile": "-plot-rr",
    "plot_yield_curve":"-plot-yield",
    "price_history": "-prices",
    "purge": "-purge",
    "risk_free_rate": "-rf",
    "risk_profile" : "-profile",
    "screener": "-screen",
    "sharpe_ratio": "-sharpe",
    "statistic": "-stat",
    "statistic_history": "-stats",
    "store": "-store",
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
    'steps': '-steps',
    'expiry': '-expiry',
    'probability': '-prob',
    'allocate': '-allocate'
}

FUNC_XTRA_SINGLE_ARGS_DICT = {
    'optimize_sharpe': "-sh",
}

FUNC_DICT = {
    "asset_type": "Outputs the asset type for the supplied symbol.",
    
    "bs_cvar": "Calculates the Black Scholes conditional value at risk, i.e. E(St | St < K), for the list of inputted ticker symbols. 'expiry' and 'prob' are required arguments for this function. Note: 'expiry' is measured in years and is different from the `start` and `end` dates. `start` and `end` are used to calibrate the model to a historical sample and `expiry` is used as the time horizon over which the value at risk is calculated into the future.__\n\t\t\tOPTIONS: \n\t\t\t\t-prob (format: decimal) REQUIRED\n\t\t\t\t-expiry (format: decimal) REQUIRED\n\t\t\t\t-start (format: \"YYYY-MM-DD\")\n\t\t\t\t-end  (format :\"YYYY-MM-DD\")",

   "bs_var": "Calculates the Black Scholes value at risk, i.e. for a given p, the S0 such that Prob(St<S0) = p. 'expiry' and 'prob' are required arguments for this function. Note: 'expiry' is measured in years and is different from the `start` and `end` dates. `start` and `end` are used to calibrate the model to a historical sample and `expiry` is used as the time horizon over which the value at risk is calculated into the future.__\n\t \t\tOPTIONS: \n\t\t\t\t -prob (format: decimal) REQUIRED \n\t\t\t\t -expiry (format: decimal) REQUIRED \n\t\t\t\t -start (format: \"YYYY-MM-DD\")\n\t\t\t\t-end  (format :\"YYYY-MM-DD\")",


    "capm_equity_cost": "Computes the cost of equity according to CAPM for the supplied list of tickers. If no start or end dates are specified, calculations default to the last 100 days of prices. The environment variable MARKET_PROXY defines which ticker serves as a proxy for the market as whole.__\n\t\t\tOPTIONS:\n\t\t\t\t-start (format: \"YYYY-MM-DD\")\n\t\t\t\t-end  (format :\"YYYY-MM-DD\")",

    "capm_beta": "Computes the market beta according to CAPM for the supplied list of tickers. If no start or end dates are specified, calculations default to the last 100 days of prices. The environment variable MARKET_PROXY defines which ticker serves as a proxy for the market as whole.__\n\t\t\tOPTIONS:\n\t\t\t\t-start (format: \"YYYY-MM-DD\")\n\t\t\t\t-end  (format :\"YYYY-MM-DD\")",

    "clear_cache": "Clears the /data/cache/ directory of all data, outdated or not.",
    
    "clear_static": "Clears the /data/static directory of all data. Not recommended unless necessary. Static data takes a long time to reload.",

    "clear_watchlist": "Clears the /data/common/watchlist.json of all saved ticker symbols.",
    
    "close": "Return latest closing value for the supplied list of symbols (equity or crypto).",
    
    "correlation": "Calculate pair-wise correlation for the supplied list of ticker symbols. If no start or end dates are specified, calculations default to the last 100 days of prices.__\n\t\t\tOPTIONS:\n\t\t\t\t-start (format: \"YYYY-MM-DD\")\n\t\t\t\t-end  (format :\"YYYY-MM-DD\")",
    
    "correlation_time_series": "EXPERIMENTAL. PROBABLY WON'T WORK. Calculate correlation for a pair of tickers over a specified date range. If no start or end dates are specified, the default analysis period of 100 days is applied. __\n\t\t\tOPTIONS:\n\t\t\t\t-start (format: \"YYYY-MM-DD\")\n\t\t\t\t-end  (format :\"YYYY-MM-DD\")",

    "discount_dividend": "Extrapolates future dividend cashflows from historical dividend payments with linear regression and then uses that model to calculate the net present value of all future dividends. If no discount rate is specified, the calculations default to the risk-free rate, i.e. the 10-Year US Treasury yield.__\n\t\t\tOPTIONS:\n\t\t\t\t -discount (float)",
    
    "dividends": "Displays the price history over the specific date range. If no dates are provided, returns the entire dividend history.__\n\t\t\tOPTIONS:\n\t\t\t\t-start (format: \"YYYY-MM-DD\")\n\t\t\t\t-end  (format :\"YYYY-MM-DD\")",

    "efficient_frontier": "Generate a sample of the portfolio's efficient frontier for the supplied list of tickers. By default, the efficient frontier will minimize a portfolio's volality for a given rate of return. The number of points calculated in the efficient frontier can be specifed as an integer with the -steps. If no -steps is provided, the value of the environment variable FRONTIER_STEPS will be used.__\n\t\t\t OPTIONS:\n\t\t\t\t-steps (format: integer)\n\t\t\t\t-invest (format: float)\n\t\t\t\t-start (format: \"YYYY-MM-DD\")\n\t\t\t\t-end  (format :\"YYYY-MM-DD\")\n\t\t\t\t-save (format: /path/to/file/filename.json)",
    
    "examples": "Display examples of syntax.",
    
    "gui": "Brings up a Qt GUI for the application (work in progress!)",
    
    "help": "Print this help message.",
    
    "initialize": "Initializes the data in the /static/ directory. Local application automatically initializes this data. This option is used to initialize static data inside of a Docker container, where the application entrypoint doesn't invoke the CLI automatically.",
    
    "maximize_return": "Maximize the return of the portfolio defined by the supplied list of ticker symbols. Returns an array representing the allocations to be made for each asset in a portfolio. If no start or end dates are specified, calculations default to the last 100 days of prices. You can specify an investment with the '-invest' flag, otherwise the result will be output in percentage terms. Note: This function will always allocate 100% to the asset with the highest return. It's a good way to check and see if there are bugs in the algorithm after changes.__\n\t\t\tOPTIONS:\n\t\t\t\t-start (format: \"YYYY-MM-DD\")\n\t\t\t\t-end (format :\"YYYY-MM-DD\")\n\t\t\t\t-invest (format: float)",
    
    "list_watchlist": "Lists the equity symbols currently saved to your watchlist.",
    
    "moving_averages": "Calculate the current moving averages. If no start or end dates are specified, calculations default to the last 100 days of prices.__\n\t\t\tOPTIONS:\n\t\t\t\t-start (format: \"YYYY-MM-DD\")\n\t\t\t\t-end  (format :\"YYYY-MM-DD\")",
    
    "optimize_portfolio_variance": "Optimize the volatility of the portfolio\'s variance subject to the supplied return target.  Returns an array representing the allocations to be made for each asset in a portfolio. The target return must be specified with the '-target' flag. If no target return is specified, the portfolio's volatility is minimized. If no start or end dates are specified with the '-start' and '-end' flags, calculations default to the last 100 days of prices. You can specify an investment with the '-invest' flag, otherwise the result will be output in percentage terms. If the -sh flag is specified, the function will maximize the portfolio's sharpe ratio instead of minimizing it's volatility.__\n\t\t\tOPTIONS:  -start (format: \"YYYY-MM-DD\")\n\t\t\t\t-end (format :\"YYYY-MM-DD\")\n\t\t\t\t-target (format: decimal)\n\t\t\t\t-invest (format: float)\n\t\t\t\t-save (format: /path/to/file/filename.json)\n\t\t\t\t-sh (binary flag; no format. include it or don't.)",
    
    "optimize_portfolio_conditional_var":"Optimizes the Black Scholes conditional value at risk, i.e. E(St | St < K), for the portfolio defined by the list of inputted ticker symbols. 'expiry' and 'prob' are required arguments for this function. Note: 'expiry' is measured in years and is different from the `start` and `end` dates. `start` and `end` are used to calibrate the model to a historical sample and `expiry` is used as the time horizon over which the value at risk is calculated into the future.__\n\t\t\tOPTIONS:\n\t\t\t\t-prob (format: decimal) REQUIRED\n\t\t\t\t-expiry (format: decimal)\n\t\t\t\t-start (format: \"YYYY-MM-DD\")\n\t\t\t\t-end (format :\"YYYY-MM-DD\")",

    "plot_correlation": "EXPERIMENTAL. PROBABLY WON'T WORK. Generates a time series for the correlation of two ticker symbols over the specified date range.__\n\t\t\tOPTIONS:\n\t\t\t\t-start (format: \"YYYY-MM-DD\")\n\t\t\t\t-end (format :\"YYYY-MM-DD\")\n\t\t\t\t-save (format: /path/to/file/filename.jpeg)",

    "plot_dividends": "Generates a scatter plot graphic of the dividend history for the supplied list of tickers with a superimposed simple linear regression line.__\n\t\t\tOPTIONS:\n\t\t\t\t-save (format: /path/to/file/filename.jpeg)",
    
    "plot_frontier": "Generates a scatter plot graphic of the portfolio\'s efficient frontier for the supplied list of tickers. Not available when running inside of a Docker container.The number of points calculated in the efficient frontier can be specifed as an integer with the -steps. If no -steps is provided, the value of the environment variable FRONTIER_STEPS will be used.__\n\t\t\tOPTIONS:\n\t\t\t\t-start (format: \"YYYY-MM-DD\")\n\t\t\t\t-end  (format :\"YYYY-MM-DD\")\n\t\t\t\t-save (format: /path/to/file/filename.jpeg)\n\t\t\t\t-steps (format: integer)",
    
    "plot_moving_averages": "Generates a grouped bar chart of the moving averages for each equity in the supplied list of ticker symbols. Not available when running inside of a Docker container. If no start or end dates are specified, calculations default to the last 100 days of prices.__\n\t\t\tOPTIONS:\n\t\t\t\t-start (format: \"YYYY-MM-DD\")\n\t\t\t\t-end  (format :\"YYYY-MM-DD\")\n\t\t\t\t-save (format: /path/to/file/filename.jpeg)",
    
    "plot_risk_profile": "Generates a scatter plot of the risk-return profile for symbol in the supplied list of ticker symbols. If no start or end dates are specified, calculations default to the last 100 days of prices.__\n\t\t\t OPTIONS:\n\t\t\t\t-start (format: \"YYYY-MM-DD\")\n\t\t\t\t-end  (format :\"YYYY-MM-DD\")\n\t\t\t\t-save (format: /path/to/file/filename.jpeg",

    "plot_yield_curve": "Generates a plot of the United States Treasury Yield Curve using the Federal Funds Rate, the 3-Month Rate, the 3-Year Rate, the 5-Year Rate, the 10-Year Rate and the 30-Year Rate.__\n\t\t\tOPTIONS:\n\t\t\t\t-start (format: \"YYYY-MM-DD\")\n\t\t\t\t-end  (format :\"YYYY-MM-DD\")\n\t\t\t\t-save (format: /path/to/file/filename.jpeg",
    
    "price_history": "Prints the price histories for each inputted asset over the specified date range. If no date range is given, price histories will default to the last 100 days.__\n\t\t\tOPTIONS:\n\t\t\t\t-start (format: \"YYYY-MM-DD\")\n\t\t\t\t-end  (format :\"YYYY-MM-DD\")\n\t\t\t\t-save (format: /path/to/file/filename.json)",

    "purge": "Removes all files contained with the /static/ and /cache/ directory, but retains the directories themselves.",
    
    "risk_free_rate": "Returns current 10-year, annualized US Treasury yield.",
    
    "risk_profile": "Calculate the risk-return profile for the supplied list of ticker symbols. If no start or end dates are specified, calculations default to the last 100 days of prices.__\n\t\t\tOPTIONS:\n\t\t\t\t -start (format: \"YYYY-MM-DD\")\n\t\t\t\t-end  (format :\"YYYY-MM-DD\")\n\t\t\t\t-save (format: /path/to/file/filename.json)",
    
    "screener": "Searchs equity spot prices that trade at a discount to the provided model. If no model is provided, the screener will default to the Discount Dividend Model. If no discount rate is provided, the screener will default to the cost of equity for a ticker calculated using the CAPM model and the ticker defined by environment variable MARKET_PROXY as a proxy for the market.__\n\t\t\tADDITION OPTIONS:\n\t\t\t\t-discount (format: decimal)\n\t\t\t\t-model (format: string, values: ddm)",
    
    "sharpe_ratio": "Computes the sharpe ratio for each of the supplied tickers.__\n\t\t\tOPTIONS:\n\t\t\t\t-start (format: \"YYYY-MM-DD\")\n\t\t\t\t-end  (format :\"YYYY-MM-DD\")", 

    "statistic": "Retrieves the latest value for the supplied list of economic statistics. The available list of economic statistic can be found at https://www.quandl.com/data/FRED-Federal-Reserve-Economic-Data/documentation?anchor=growth; it is also stored in the /static/ directory of the application ",
    
    "statistic_history": "Prints the statistic history for the supplied list of economic statistics.__\n\t\t\tOPTIONS:\n\t\t\t\t-save (format: /path/to/file/filename.jpeg)",

    "store": "Save API key to local installation/data/common/ directory. Keys must be input one at a time. ALLOWABLE KEYS: ALPHA_VANTAGE_KEY, QUANDL_KEY, IEX_KEY. Case sensitive.",

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
