import os
from scrilla import static
from scrilla.util import helper

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(SCRIPT_DIR))))
ENV_DIR = os.path.join(PROJECT_DIR, 'env')

APP_NAME="scrilla"

SIG_FIGS=5

SEPARATER = "-"

LINE_LENGTH = 100

BAR_WIDTH = 0.10

INDENT = 10

RISK_FREE_TITLE = "{} US Treasury"

HELP_MSG = [
    "A financial application for optimizing portfolio allocations and calculating financial statistics. This library requires API keys from Alpha Vantage (https://www.alphavantage.co), Quandl (https://www.quandl.com/) and IEX (https://iexcloud.io/) to hydrate with data. These keys should be stored in environment variables named \x1b[1mALPHA_VANTAGE_KEY\x1b[0m, \x1b[1mQUANDL_KEY\x1b[0m and \x1b[1mIEX_KEY\x1b[0m.",

    "NOTE: The asset price model used for probability calculations can be changed by modifying the value of the \x1b[1mANALYSIS_MODE\x1b[0m environment variable. Currently, scrilla supports a Geometric Brownian Motion mode, 'geometric', and a Mean Reversion motion mode, 'reversion'. The parameters of these distributions are estimated using the method set by the environment variable \x1b[1mESTIMATION_METHOD\x1b[0m. Currently supported values for \x1b[1mESTIMATION_METHOD\x1b[0m are: 'moments', 'percents' and 'likely'. Any function that returns a statistical calculation can have the default method overridden with the '-moments', '-percents' or 'likely' flag.",

    "See documentation for more information on configuration and usage: https://github.com/chinchalinchin/scrilla."
]

SYNTAX = "command -FUNCTION -OPTIONS [tickers/symbols]"

TAB = "      "

FUNC_ARG_DICT = {
    "asset_type": "-asset",
    "cvar": "-cvar",
    "var": "-var",
    "capm_equity_cost": "-capm-equity",
    "capm_beta": "-capm-beta",
    "clear_cache": "-clear-cache",
    "clear_static": "-clear-static",
    "clear_common": "-clear-watch",
    "close": "-close",
    "correlation":"-cor",
    "correlation_time_series": "-cors",
    "discount_dividend": "-ddm",
    "dividends": "-div",
    "efficient_frontier": "-ef",
    "examples": "-ex",
    "gui": "-gui",
    "help": "-help",
    "interest_history": "-int",
    "list_watchlist": "-ls-watch",
    "maximize_return": "-max",
    "moving_averages": "-mov",
    "optimize_portfolio_variance": "-opt",
    "optimize_portfolio_conditional_var": "-opt-cvar",
    "plot_correlation": "-plot-cors",
    "plot_dividends": "-plot-div",
    "plot_frontier": "-plot-ef",
    "plot_moving_averages": "-plot-mov",
    "plot_returns": "-plot-rets",
    "plot_risk_profile": "-plot-profile",
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
    "version": "-version",
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
    'json': '-json',
    'suppress_output': '-quiet',
    'moments': '-moments',
    'percentiles': '-percents',
    'likelihood': '-likely'
}

FUNC_DICT = {
    "asset_type": "Outputs the asset type for the supplied symbol.",
    
    "cvar": "Calculates the conditional value at risk, i.e. E(St | St < Sv) where Sv -> Prob(St<S0) = `prob` , for the list of inputted ticker symbols. 'expiry' and 'prob' are required arguments for this function. Note: 'expiry' is measured in years and is different from the `start` and `end` dates. `start` and `end` are used to calibrate the model to a historical sample and `expiry` is used as the time horizon over which the value at risk is calculated into the future.__\n\t\t\tOPTIONS: \n\t\t\t\t-prob (format: decimal) REQUIRED\n\t\t\t\t-expiry (format: decimal) REQUIRED\n\t\t\t\t-start (format: \"YYYY-MM-DD\")\n\t\t\t\t-end  (format :\"YYYY-MM-DD\")\n\t\t\t\t-json (print results to screen as JSON)\n\t\t\t\t-save (format: /path/to/file/filename.json)\n\t\t\t\t-quiet (suppress console output\n\t\t\t\t-moments (estimation method flag)\n\t\t\t\t-percents (estimation method flag)\n\t\t\t\t-likely (estimation method flag)",

   "var": "Calculates the value at risk, i.e. for a given p, the Sv such that Prob(St<Sv) = p. 'expiry' and 'prob' are required arguments for this function. Note: 'expiry' is measured in years and is different from the `start` and `end` dates. `start` and `end` are used to calibrate the model to a historical sample and `expiry` is used as the time horizon over which the value at risk is calculated into the future.__\n\t\t\tOPTIONS: \n\t\t\t\t-prob (format: decimal) REQUIRED \n\t\t\t\t-expiry (format: decimal) REQUIRED \n\t\t\t\t-start (format: \"YYYY-MM-DD\")\n\t\t\t\t-end  (format :\"YYYY-MM-DD\")\n\t\t\t\t-save (format: /path/to/file/filename.json)\n\t\t\t\t-quiet (suppress console output)\n\t\t\t\t-moments (estimation method flag)\n\t\t\t\t-percents (estimation method flag)\n\t\t\t\t-likely (estimation method flag)",

    "capm_equity_cost": "Computes the cost of equity according to CAPM for the supplied list of tickers. If no start or end dates are specified, calculations default to the last 100 days of prices. The environment variable \x1b[1mMARKET_PROXY\x1b[0m defines which ticker serves as a proxy for the market as whole.__\n\t\t\tOPTIONS:\n\t\t\t\t-start (format: \"YYYY-MM-DD\")\n\t\t\t\t-end  (format :\"YYYY-MM-DD\")\n\t\t\t\t-save (format: /path/to/file/filename.json)\n\t\t\t\t-json (print results to screen as JSON)\n\t\t\t\t-quiet (suppress console output)\n\t\t\t\t-moments (estimation method flag)\n\t\t\t\t-percents (estimation method flag)\n\t\t\t\t-likely (estimation method flag)",

    "capm_beta": "Computes the market beta according to CAPM for the supplied list of tickers. If no start or end dates are specified, calculations default to the last 100 days of prices. The environment variable \x1b[1mMARKET_PROXY\x1b[0m defines which ticker serves as a proxy for the market as whole.__\n\t\t\tOPTIONS:\n\t\t\t\t-start (format: \"YYYY-MM-DD\")\n\t\t\t\t-end  (format :\"YYYY-MM-DD\")\n\t\t\t\t-save (format: /path/to/file/filename.json)\n\t\t\t\t-json (print results to screen as JSON)\n\t\t\t\t-quiet (suppress console output)\n\t\t\t\t-moments (estimation method flag)\n\t\t\t\t-percents (estimation method flag)\n\t\t\t\t-likely (estimation method flag)",

    "clear_cache": "Clears the _installation_directiory_/data/cache/ directory of all data.",
    
    "clear_static": "Clears the _installation_directory_/data/static/ directory of all data. Not recommended unless necessary. Static data takes a long time to reload.",

    "clear_common": "Clears the _installation_directory_/data/common/, which includes API keys stored through the command line and ticker saved to the user watchlist.",
    
    "close": "Return latest closing value for the supplied list of symbols (equity or crypto).",
    
    "correlation": "Calculate pair-wise correlation for the supplied list of ticker symbols. If no start or end dates are specified, calculations default to the last 100 days of prices.__\n\t\t\tOPTIONS:\n\t\t\t\t-start (format: \"YYYY-MM-DD\")\n\t\t\t\t-end  (format :\"YYYY-MM-DD\")\n\t\t\t\t-save (format: /path/to/file/filename.json)\n\t\t\t\t-json (print results to screen as JSON)\n\t\t\t\t-quiet (suppress console output)\n\t\t\t\t-moments (estimation method flag)\n\t\t\t\t-percents (estimation method flag) \x1b[1mEXPERIMENTAL! PROBABLY WON'T WORK!\x1b[0m\n\t\t\t\t-likely (estimation method flag) \x1b[1mEXPERIMENTAL! PROBABLY WONT' WORK!\x1b[0m",
    
    "correlation_time_series": "\x1b[1mEXPERIMENTAL. PROBABLY WON'T WORK.\x1b[0m Calculate correlation time series for a pair of tickers over a specified date range. If no start or end dates are specified, the default analysis period of 100 days is applied. __\n\t\t\tOPTIONS:\n\t\t\t\t-start (format: \"YYYY-MM-DD\")\n\t\t\t\t-end  (format :\"YYYY-MM-DD\")",

    "discount_dividend": "Extrapolates future dividend cashflows from historical dividend payments with linear regression and then uses that model to calculate the net present value of all future dividends. If no discount rate is specified, the calculations default to the asset's cost of equity as determined the by the CAPM model.__\n\t\t\tOPTIONS:\n\t\t\t\t-discount (format: decimal)\n\t\t\t\t-save (format: /path/to/file/filename.json)\n\t\t\t\t-json (print results to screen as JSON)\n\t\t\t\t-quiet (suppress console output)",
    
    "dividends": "Displays the price history over the specific date range. If no dates are provided, returns the entire dividend history.__\n\t\t\tOPTIONS:\n\t\t\t\t-start (format: \"YYYY-MM-DD\")\n\t\t\t\t-end  (format :\"YYYY-MM-DD\")\n\t\t\t\t-save (format: /path/to/file/filename.json)\n\t\t\t\t-json (print results to screen as JSON)\n\t\t\t\t-quiet (suppress console output)",

    "efficient_frontier": "Generate a sample of the portfolio's efficient frontier for the supplied list of tickers. The efficient frontier algorithm will minimize a portfolio's volality for a given rate of return and then maximize its return, and then use these points to generate the rest of the frontier by taking increments along the line connecting the (risk,return) profile of the minimum volatility portfolio to the (risk, return) profile of the maximum return portfolio. The number of points calculated in the efficient frontier can be specifed as an integer with the -steps flag. If no -steps is provided, the value of the environment variable FRONTIER_STEPS will be used.__\n\t\t\t OPTIONS:\n\t\t\t\t-steps (format: integer)\n\t\t\t\t-invest (format: decimal)\n\t\t\t\t-start (format: \"YYYY-MM-DD\")\n\t\t\t\t-end  (format :\"YYYY-MM-DD\")\n\t\t\t\t-save (format: /path/to/file/filename.json)\n\t\t\t\t-json (print results to screen as JSON)\n\t\t\t\t-quiet (suppress console output)\n\t\t\t\t-moments (estimation method flag)\n\t\t\t\t-percents (estimation method flag)\n\t\t\t\t-likely (estimation method flag)",
    
    "examples": "Display examples of syntax.",
    
    "gui": "Brings up a Qt GUI for the application (TODO: work in progress!)",
    
    "help": "Print this help message.",
        
    "interest_history": "Prints the interest histories for each inputted maturity over the specified date range. If no date range is given, price histories will default to the last 100 days. See `scrilla -yield` for list of maturities.__\n\t\t\tOPTIONS:\n\t\t\t\t-start (format: \"YYYY-MM-DD\")\n\t\t\t\t-end  (format :\"YYYY-MM-DD\")\n\t\t\t\t-save (format: /path/to/file/filename.json)\n\t\t\t\t-json (print results to screen as JSON)\n\t\t\t\t-quiet (suppress console output)",
    
    "list_watchlist": "Lists the equity symbols currently saved to your watchlist.",

    "maximize_return": "Maximize the return of the portfolio defined by the supplied list of ticker symbols. Returns an array representing the allocations to be made for each asset in a portfolio. If no start or end dates are specified, calculations default to the last 100 days of prices. You can specify an investment with the '-invest' flag, otherwise the result will be output in percentage terms. Note: This function will always allocate 100% to the asset with the highest return. It's a good way to check and see if there are bugs in the algorithm after changes.__\n\t\t\tOPTIONS:\n\t\t\t\t-start (format: \"YYYY-MM-DD\")\n\t\t\t\t-end (format :\"YYYY-MM-DD\")\n\t\t\t\t-invest (format: decimal)\n\t\t\t\t-save (format: /path/to/file/filename.json)\n\t\t\t\t-json (print results to screen as JSON)\n\t\t\t\t-quiet (suppress console output)\n\t\t\t\t-moments (estimation method flag)\n\t\t\t\t-percents (estimation method flag)\n\t\t\t\t-likely (estimation method flag)",
        
    "moving_averages": "Calculate the current moving averages. If no start or end dates are specified, calculations default to the last 100 days of prices.__\n\t\t\tOPTIONS:\n\t\t\t\t-start (format: \"YYYY-MM-DD\")\n\t\t\t\t-end  (format :\"YYYY-MM-DD\")",
    
    "optimize_portfolio_variance": "Optimize the volatility of the portfolio\'s variance subject to the supplied return target.  Returns an array representing the allocations to be made for each asset in a portfolio. The target return must be specified with the '-target' flag. If no target return is specified, the portfolio's volatility is minimized. If no start or end dates are specified with the '-start' and '-end' flags, calculations default to the last 100 days of prices. You can specify an investment with the '-invest' flag, otherwise the result will be output in percentage terms. If the -sh flag is specified, the function will maximize the portfolio's sharpe ratio instead of minimizing it's volatility.__\n\t\t\tOPTIONS:\n\t\t\t\t-start (format: \"YYYY-MM-DD\")\n\t\t\t\t-end (format :\"YYYY-MM-DD\")\n\t\t\t\t-target (format: decimal)\n\t\t\t\t-invest (format: decimal)\n\t\t\t\t-save (format: /path/to/file/filename.json)\n\t\t\t\t-sh (binary flag; no format. include it or don't.)\n\t\t\t\t-json (print results to screen as JSON)\n\t\t\t\t-quiet (suppress console output)\n\t\t\t\t-moments (estimation method flag)\n\t\t\t\t-percents (estimation method flag)\n\t\t\t\t-likely (estimation method flag)",
    
    "optimize_portfolio_conditional_var":"Optimizes the conditional value at risk, i.e. E(St | St < Sv) where Sv -> Prob(St<S0) = `prob` , for the portfolio defined by the list of inputted ticker symbols. 'expiry' and 'prob' are required arguments for this function. Note: 'expiry' is measured in years and is different from the `start` and `end` dates. `start` and `end` are used to calibrate the model to a historical sample and `expiry` is used as the time horizon over which the value at risk is calculated into the future.__\n\t\t\tOPTIONS:\n\t\t\t\t-prob (format: decimal) REQUIRED\n\t\t\t\t-expiry (format: decimal) REQUIRED\n\t\t\t\t-start (format: \"YYYY-MM-DD\")\n\t\t\t\t-end (format :\"YYYY-MM-DD\")\n\t\t\t\t-json (print results to screen as JSON)\n\t\t\t\t-save (format: /path/to/file/filename.json)\n\t\t\t\t-quiet (suppress console output)\n\t\t\t\t-moments (estimation method flag)\n\t\t\t\t-percents (estimation method flag)\n\t\t\t\t-likely (estimation method flag)",

    "plot_correlation": "\x1b[1mEXPERIMENTAL! PROBABLY WON'T WORK!\x1b[0m Generates a time series for the correlation of two ticker symbols over the specified date range.__\n\t\t\tOPTIONS:\n\t\t\t\t-start (format: \"YYYY-MM-DD\")\n\t\t\t\t-end (format :\"YYYY-MM-DD\")\n\t\t\t\t-save (format: /path/to/file/filename.jpeg)",

    "plot_dividends": "Generates a scatter plot graphic of the dividend history for the supplied ticker with a superimposed simple linear regression line. Note: this function only accepts one ticker at a time.__\n\t\t\tOPTIONS:\n\t\t\t\t-save (format: /path/to/file/filename.jpeg)",
    
    "plot_frontier": "Generates a scatter plot graphic of the portfolio\'s efficient frontier for the supplied list of tickers. The number of points calculated in the efficient frontier can be specifed as an integer with the -steps. If no -steps is provided, the value of the environment variable \x1b[1mFRONTIER_STEPS\x1b[0m will be used.__\n\t\t\tOPTIONS:\n\t\t\t\t-start (format: \"YYYY-MM-DD\")\n\t\t\t\t-end  (format :\"YYYY-MM-DD\")\n\t\t\t\t-save (format: /path/to/file/filename.jpeg)\n\t\t\t\t-steps (format: integer)\n\t\t\t\t-moments (estimation method flag)\n\t\t\t\t-percents (estimation method flag)\n\t\t\t\t-likely (estimation method flag)",
    
    "plot_moving_averages": "Generates a grouped bar chart of the moving averages for each equity in the supplied list of ticker symbols. Not available when running inside of a Docker container. If no start or end dates are specified, calculations default to the last 100 days of prices.__\n\t\t\tOPTIONS:\n\t\t\t\t-start (format: \"YYYY-MM-DD\")\n\t\t\t\t-end  (format :\"YYYY-MM-DD\")\n\t\t\t\t-save (format: /path/to/file/filename.jpeg)",
    
    "plot_returns": "Generates a Q-Q Plot to graphically test the normality of returns for the inputted ticker symbol over the specified date range. If no start or date are specified, calculations default to the last 100 days of prices.__\n\t\t\tOPTIONS:\n\t\t\t\t-start (format: \"YYYY-MM-DD\")\n\t\t\t\t-end  (format :\"YYYY-MM-DD\")\n\t\t\t\t-save (format: /path/to/file/filename.jpeg)",

    "plot_risk_profile": "Generates a scatter plot of the risk-return profile for symbol in the supplied list of ticker symbols. If no start or end dates are specified, calculations default to the last 100 days of prices.__\n\t\t\t OPTIONS:\n\t\t\t\t-start (format: \"YYYY-MM-DD\")\n\t\t\t\t-end  (format :\"YYYY-MM-DD\")\n\t\t\t\t-save (format: /path/to/file/filename.jpeg\n\t\t\t\t-moments (estimation method flag)\n\t\t\t\t-percents (estimation method flag)\n\t\t\t\t-likely (estimation method flag)",

    "plot_yield_curve": "Generates a plot of the latest United States Treasury Yield Curve. A yield curveo n a different date can be generated by specifying the date with an argument.__\n\t\t\tOPTIONS:\n\t\t\t\t-start (format: \"YYYY-MM-DD\")\n\t\t\t\t-save (format: /path/to/file/filename.jpeg",
    
    "price_history": "Prints the price histories for each inputted asset over the specified date range. If no date range is given, price histories will default to the last 100 days.__\n\t\t\tOPTIONS:\n\t\t\t\t-start (format: \"YYYY-MM-DD\")\n\t\t\t\t-end  (format :\"YYYY-MM-DD\")\n\t\t\t\t-save (format: /path/to/file/filename.json)\n\t\t\t\t-json (print results to screen as JSON)\n\t\t\t\t-quiet (suppress console output)",

    "purge": "Removes all files contained with the _installation_directory_/data/static/, _installation_directory_/data/cache/ and _installation_directory_/data/common/ directory, but retains the directories themselves.",
    
    "risk_free_rate": "Returns the current annualized US Treasury yield specified by the RISK_FREE environment variables. Allowable values for RISK_FREE environment variable: ONE_MONTH, TWO_MONTH, THREE_MONTH, SIX_MONTH, ONE_YEAR, TWO_YEAR, THREE_YEAR, FIVE_YEAR, SEVEN_YEAR, TEN_YEAR, TWENTY_YEAR, THIRTY_YEAR.",
    
    "risk_profile": "Calculate the risk-return profile for the supplied list of ticker symbols. If no start or end dates are specified, calculations default to the last 100 days of prices.__\n\t\t\tOPTIONS:\n\t\t\t\t-start (format: \"YYYY-MM-DD\")\n\t\t\t\t-end  (format :\"YYYY-MM-DD\")\n\t\t\t\t-save (format: /path/to/file/filename.json)\n\t\t\t\t-json (print results to screen as JSON)\n\t\t\t\t-quiet (suppress console output)\n\t\t\t\t-moments (estimation method flag)\n\t\t\t\t-percents (estimation method flag)\n\t\t\t\t-likely (estimation method flag)",
    
    "screener": "Searchs equity spot prices that trade at a discount to the provided model. If no model is provided, the screener will default to the Discount Dividend Model. If no discount rate is provided, the screener will default to the cost of equity for a ticker calculated using the CAPM model.__\n\t\t\tOPTIONS:\n\t\t\t\t-discount (format: decimal)\n\t\t\t\t-model (format: string, values: ddm)",
    
    "sharpe_ratio": "Computes the sharpe ratio for each of the supplied tickers.__\n\t\t\tOPTIONS:\n\t\t\t\t-start (format: \"YYYY-MM-DD\")\n\t\t\t\t-end  (format :\"YYYY-MM-DD\")\n\t\t\t\t-save (format: /path/to/file/filename.json)\n\t\t\t\t-json (print results to screen as JSON)\n\t\t\t\t-quiet (suppress console output)\n\t\t\t\t-moments (estimation method flag)\n\t\t\t\t-percents (estimation method flag)\n\t\t\t\t-likely (estimation method flag)", 

    "statistic": "Retrieves the latest value for the supplied list of economic statistics. The available list of economic statistic can be found at https://www.quandl.com/data/FRED-Federal-Reserve-Economic-Data/documentation?anchor=growth; it is also stored in the minstallation_directory_/data/static/ directory of the application.__\n\t\t\tOPTIONS:\n\t\t\t\t-json (print results to screen as JSON)\n\t\t\t\t-save (format: /path/to/file/filename.json)\n\t\t\t\t-quiet (suppress console output)",
    
    "statistic_history": "Prints the statistic history for the supplied list of economic statistics.The available list of economic statistic can be found at https://www.quandl.com/data/FRED-Federal-Reserve-Economic-Data/documentation?anchor=growth; it is also stored in the _installation_directory_/data/static/ directory of the application.__\n\t\t\tOPTIONS:\n\t\t\t\t-start (format: \"YYYY-MM-DD\")\n\t\t\t\t-end  (format :\"YYYY-MM-DD\")\n\t\t\t\t-save (format: /path/to/file/filename.json)\n\t\t\t\t-json (print results to screen as JSON)\n\t\t\t\t-quiet (suppress console output)",

    "store": "Save API key to local _installation_directory_/data/common/ directory. Keys must be input one at a time. Allowable keys: \x1b[1mALPHA_VANTAGE_KEY\x1b[0m, \x1b[1mQUANDL_KEY\x1b[0m, \x1b[1mIEX_KEY\x1b[0m. Case sensitive.__\n\t\t\tEXAMPLE:\n\t\t\t\tscrilla -store <key>=<value>",

    "watchlist": "Saves the supplist list of tickers to your watchlist. These equity symbol are used by the screening algorithms when searching for stocks that trade at a discount.", 

    "version": "Display version.", 
    
    "yield_curve": "Displays the current United States Treasury Yield Curve."

}

EXAMPLES = { 
    'scrilla -store ALPHA_VANTAGE_KEY=mykeygoeshere': 'Store your API credentials in the _installation_directory_/data/common subdirectory. Note: credentials are stored unencrypted. It is recommended you store your API credentials in environment variables. See documentation for more information: https://pypi.org/project/scrilla/',

    'scrilla -ls-watch': 'Lists the stocks in your watchlist.',

    'scrilla  -profile GOOG AMZN XOM AAPL': 'Calculate the risk-return profile for each equity in the portfolio composed of (GOOG, AMZN, XOM, APPL)',

    'scrilla  -cor GLD SPY SLV UUP TLT EWA': 'Calculate the correlation matrix for the portfolio composed of (GLD, SPY, SLV, UUP, TLT, EWA',

    'scrilla -opt U TSLA SPCE': 'Finds the portfolio allocation that minimizes the overall variance of the portfolio composed of (U, TSLA, SPCE). ',

    'scrilla -opt -target 0.83 ALLY FB PFE SNE BX': 'Optimize the portfolio consisting of (ALLY, FB, PFE, SNE, BX) subject to the constraint their mean annual return equal 83%. Note the constrained return must reside within the feasible region of returns, i.e. the constrained return must be less than the maximum possible return and greater than the minimum possible return.',  

    'scrilla -opt -sh -save /home/Desktop/max_sharpe_ratio.json LMT GD UPS MMM': 'Maximize the sharpe ratio of the portfolio consisting of (LMT, GD, UPS, MM) and ouput the portfolio allocation along with its risk-return profile to a json located at /home/Desktop/max_sharpe_ratio.json.',

    'scrilla -ef QS DIS RUN': 'Calculate a five point sample of the efficient (risk, return) frontier for the portfolio composed of (QS, DIS, RUN). The number of points generated in the sample can be altered through the FRONTIER_STEPS environment variable.',

    'scrilla -plot-ef QQQ SPY DIA': "Generate a graphical display of the (QQQ, SPY, DIA) portolio\'s efficient (risk, return) frontier. The number of points generated in the sample can be altered through the FRONTIER_STEPS environment variable. Note, if the graphical display does not show up, you may need to configure matplotlib\'s backend to be compatible with your OS.",

    'scrilla -plot-profile -save /home/Desktop/profile.jpeg QS ACI': "Generate a graphical display of the current risk profile of the (QS, ACI) portolio and saves it to the file named 'profile.jpeg' located in the /home/Desktop/ directory.",

    'scrilla -stat GDP BASE MI': "Display the latest values for the supplied list of economic indicators.",

    'scrilla -close MSFT IBM FSLR NFLX BTC XRP': "Displays the last closing price for the supplied list of asset types",

    'scrilla -gui': "Launches a PyQt GUI into which the application functions have been wired. Note this does not work in containers.",

    'scrilla -screen -model DDM': 'Screens the equities in your watchlist for spot prices that trade at a discount to the specified moel',
    
    'scrilla -watch ATVI TTWO EA': 'Adds the portfolio (ATVI, TTWO, EA) to the existing ticker symbols in your equity watchlist'  
}

# TODO: come up with better names for the functions here now that GUI and CLI are grouped together
# CLI FORMATTING
def format_profiles(profiles: dict):
    profiles_format = []
    for key, value in profiles.items():
        holding = value
        holding['ticker'] = key
        profiles_format.append(holding)
    return profiles_format

def format_allocation(allocation, portfolio, investment=None):
    allocation_format = []

    if investment is not None:
        shares = portfolio.calculate_approximate_shares(x=allocation, total=investment)
        total = portfolio.calculate_actual_total(x=allocation, total=investment)

    annual_volatility = portfolio.volatility_function(x=allocation) 
    annual_return = portfolio.return_function(x=allocation)

    for j, item in enumerate(portfolio.tickers):
        holding = {}
        holding['ticker'] = item
        holding['allocation'] = round(allocation[j], static.constants['ACCURACY'])
        if investment is not None:
            holding['shares'] = float(shares[j])
        holding['annual_return'] = round(portfolio.mean_return[j], static.constants['ACCURACY']) 
        holding['annual_volatility'] = round(portfolio.sample_vol[j], static.constants['ACCURACY'])
        allocation_format.append(holding)

    json_format = {}
    json_format['holdings'] = allocation_format

    if investment is not None:
        json_format['total'] = float(total)
        
    json_format['portfolio_return'] = annual_return
    json_format['portfolio_volatility'] = annual_volatility
    
    return json_format

def format_frontier(portfolio, frontier, investment=None):
    json_format = []
    for i, item in enumerate(frontier):
        json_format.append(format_allocation(allocation=item, portfolio=portfolio, 
                                                            investment=investment))
    return json_format

def format_moving_averages(tickers, averages_output):
    these_moving_averages, dates = averages_output

    response = {}
    for i, item in enumerate(tickers):
        ticker_str=f'{item}'
        MA_1_str, MA_2_str, MA_3_str = f'{ticker_str}_MA_1', f'{ticker_str}_MA_2', f'{ticker_str}_MA_3'    

        subresponse = {}
        if dates is None:
            subresponse[MA_1_str] = these_moving_averages[i][0]
            subresponse[MA_2_str] = these_moving_averages[i][1]
            subresponse[MA_3_str] = these_moving_averages[i][2]

        else:
            subsubresponse_1, subsubresponse_2, subsubresponse_3 = {}, {}, {}
    
            for j, this_item in enumerate(dates):
                date_str=helper.date_to_string(this_item)
                subsubresponse_1[date_str] = these_moving_averages[i][0][j]
                subsubresponse_2[date_str] = these_moving_averages[i][1][j]
                subsubresponse_3[date_str] = these_moving_averages[i][2][j]

            subresponse[MA_1_str] = subsubresponse_1
            subresponse[MA_2_str] = subsubresponse_2
            subresponse[MA_3_str] = subsubresponse_3

        response[ticker_str] = subresponse
    
    return response

def format_correlation_matrix(tickers, correlation_matrix):
    response = []
    for i, item in enumerate(tickers):
        # correlation_matrix[i][i]
        for j in range(i+1, len(tickers)):
            subresponse = {}
            subresponse[f'{item}_{tickers[j]}_correlation'] = correlation_matrix[j][i]
            response.append(subresponse)
    return response

# GUI FORMATTING
def format_allocation_profile_title(allocation, portfolio) -> str:
    port_return, port_volatility = portfolio.return_function(allocation), portfolio.volatility_function(allocation)
    formatted_result = "("+str(100*port_return)[:5]+"%, " + str(100*port_volatility)[:5]+"%)"
    formatted_result_title = "("
    for symbol in portfolio.tickers:
        if portfolio.tickers.index(symbol) != (len(portfolio.tickers) - 1):
            formatted_result_title += symbol+", "
        else:
            formatted_result_title += symbol + ") Portfolio Return-Risk Profile"
    whole_thing = formatted_result_title +" = "+formatted_result
    return whole_thing
