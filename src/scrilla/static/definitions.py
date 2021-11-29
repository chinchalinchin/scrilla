import datetime
from scrilla.static import keys

HELP_MSG = [
    "A financial application for optimizing portfolio allocations, calculating financial statistics and generating graphical plots. This library requires API keys from Alpha Vantage (https://www.alphavantage.co), Quandl (https://www.quandl.com/) and IEX (https://iexcloud.io/) to hydrate with data. These keys should be stored in environment variables named ALPHA_VANTAGE_KEY, QUANDL_KEY and IEX_KEY.",

    "See documentation for more information on configuration and usage: https://chinchalinchin.github.io/scrilla/."
]

SYNTAX = "scrilla <command> <tickers/symbols> <options>"

FUNC_DICT = {
    "asset_type": {
        'name': 'Asset Type',
        'values': ["asset", "a"],
        'args': None,
        'description': "Outputs the asset type for the supplied symbol.",
        'tickers': True,
    },
    "cvar": {
        'name': 'Conditional Value At Risk',
        'values': ["cvar", "cv"],
        'args': ['probability', 'expiry', 'start_date', 'end_date', 'save_file', 'suppress_output', 'json', keys.keys['ESTIMATION']['MOMENT'], keys.keys['ESTIMATION']['PERCENT'], keys.keys['ESTIMATION']['LIKE']],
        'description': "Calculates the conditional value at risk, i.e. E(St | St < Sv) where Sv -> Prob(St<Sv) = `prob` , for the list of inputted ticker symbols. 'expiry' and 'prob' are required arguments for this function. Note: 'expiry' is measured in years and is different from the `start` and `end` dates. `start` and `end` are used to calibrate the model to a historical sample and `expiry` is used as the time horizon over which the value at risk is calculated into the future.",
        'tickers': True,
    },
    "var": {
        'name': 'Value At Risk',
        'values': ["var", "v"],
        'args': ['probability', 'expiry', 'start_date', 'end_date', 'save_file', 'suppress_output', 'json', keys.keys['ESTIMATION']['MOMENT'], keys.keys['ESTIMATION']['PERCENT'], keys.keys['ESTIMATION']['LIKE']],
        'description': "Calculates the value at risk, i.e. for a given p, the Sv such that Prob(St<Sv) = p. 'expiry' and 'prob' are required arguments for this function. Note: 'expiry' is measured in years and is different from the `start` and `end` dates. `start` and `end` are used to calibrate the model to a historical sample and `expiry` is used as the time horizon over which the value at risk is calculated into the future.",
        'tickers': True,
    },
    "capm_equity_cost": {
        'name': 'Capital Asset Pricing Model Cost of Equity',
        'values': ["capm-equity", "capm-e"],
        'args': ['start_date', 'end_date', 'save_file', 'suppress_output', 'json', keys.keys['ESTIMATION']['MOMENT'], keys.keys['ESTIMATION']['PERCENT'], keys.keys['ESTIMATION']['LIKE']],
        'description': "Computes the cost of equity according to CAPM for the supplied list of tickers. If no start or end dates are specified, calculations default to the last 100 days of prices. The environment variable MARKET_PROXY defines which ticker serves as a proxy for the market as whole.",
        'tickers': True,
    },
    "capm_beta": {
        'name': 'Capital Asset Pricing Model Beta',
        'values': ["capm-beta", "capm-b"],
        'args': ['start_date', 'end_date', 'save_file', 'suppress_output', 'json', keys.keys['ESTIMATION']['MOMENT'], keys.keys['ESTIMATION']['PERCENT'], keys.keys['ESTIMATION']['LIKE']],
        'description': "Computes the market beta according to CAPM for the supplied list of tickers. If no start or end dates are specified, calculations default to the last 100 days of prices. The environment variable MARKET_PROXY defines which ticker serves as a proxy for the market as whole.",
        'tickers': True,
    },
    "clear_cache": {
        'name': 'Clear Cache',
        'values': ["clear-cache", "cc"],
        'args': None,
        'description': "Clears the _installation_directiory_/data/cache/ directory of all data.",
        'tickers': False,
    },
    "clear_static": {
        'name': 'Clear Static',
        'values': ["clear-static", "cs"],
        'args': None,
        'description': "Clears the _installation_directory_/data/static/ directory of all data. Not recommended unless necessary; Static data takes a long time to reload.",
        'tickers': False,
    },
    "clear_common": {
        'name': 'Clear Common',
        'values': ["clear-common", "cc"],
        'args': None,
        'description': "Clears the _installation_directory_/data/common/, which includes API keys stored through the command line and ticker saved to the user watchlist.",
        'tickers': False,
    },
    "close": {
        'name': 'Last Closing Price',
        'values': ["close", "cl"],
        'args': None,
        'description': "Return latest closing value for the supplied list of symbols (equity or crypto).",
        'tickers': True,
    },
    "correlation": {
        'name': 'Correlation Matrix',
        'values': ["correlation", "cor"],
        'args': ['start_date', 'end_date', 'save_file', 'suppress_output', 'json', keys.keys['ESTIMATION']['MOMENT'], keys.keys['ESTIMATION']['PERCENT'], keys.keys['ESTIMATION']['LIKE']],
        'description': "Calculate pair-wise correlation for the supplied list of ticker symbols. If no start or end dates are specified, calculations default to the last 100 days of prices.",
        'tickers': True,
    },
    "correlation_time_series": {
        'name': 'Correlation Time Series',
        'values': ["correlations", "cors"],
        'args': ['start_date', 'end_date', 'save_file', 'suppress_output', 'json', keys.keys['ESTIMATION']['MOMENT'], keys.keys['ESTIMATION']['PERCENT'], keys.keys['ESTIMATION']['LIKE']],
        'description': "Calculate correlation time series for a pair of tickers over a specified date range. If no start or end dates are specified, the default analysis period of 100 days is applied.",
        'tickers': True,
    },
    "discount_dividend": {
        'name': 'Discount Dividend Model',
        'values': ["discount-dividend-model", "ddm"],
        'args': ['discount', 'save_file', 'suppress_output', 'json'],
        'description': "Extrapolates future dividend cashflows from historical dividend payments with linear regression and then uses that model to calculate the net present value of all future dividends. If no discount rate is specified, the calculations default to the asset's cost of equity as determined the by the CAPM model.",
        'tickers': True,
    },
    "dividends": {
        'name': 'Dividend History',
        'values': ["dividends", "divs"],
        'args': ['start_date', 'end_date', 'save_file', 'suppress_output', 'json'],
        'description': "Displays the price history over the specific date range. If no dates are provided, returns the entire dividend history.",
        'tickers': True,
    },
    "efficient_frontier": {
        'name': 'Portfolio Efficient Frontier',
        'values': ["efficient-frontier", "ef"],
        'args': ['start_date', 'end_date', 'investment', 'target', 'steps', 'save_file', 'suppress_output', 'json', keys.keys['ESTIMATION']['MOMENT'], keys.keys['ESTIMATION']['PERCENT'], keys.keys['ESTIMATION']['LIKE']],
        'description': "Generate a sample of the portfolio's efficient frontier for the supplied list of tickers. The efficient frontier algorithm will minimize a portfolio's volality for a given rate of return and then maximize its return, and then use these points to generate the rest of the frontier by taking increments along the line connecting the (risk,return) profile of the minimum volatility portfolio to the (risk, return) profile of the maximum return portfolio. The number of points calculated in the efficient frontier can be specifed as an integer with the -steps flag. If no -steps is provided, the value of the environment variable FRONTIER_STEPS will be used.",
        'tickers': True,
    },
    "help": {
        'name': 'Help Message',
        'values': ["help", "h"],
        'args': None,
        'description': "Print this help message.",
        'tickers': False,
    },
    "interest_history": {
        'name': 'Interest Rate History',
        'values': ["interest", "int"],
        'args': ['start_date', 'end_date', 'save_file', 'suppress_output', 'json'],
        'description': "Prints the interest histories for each inputted maturity over the specified date range. If no date range is given, price histories will default to the last 100 days. See `scrilla -yield` for list of maturities.",
        'tickers': True,
    },
    "list_watchlist": {
        'name': 'Display Watchlist',
        'values': ["watchlist", "w-ls"],
        'args': None,
        'description': "Lists the equity symbols currently saved to your watchlist.",
        'tickers': False,
    },
    "maximize_return": {
        'name': 'Maximize Portfolio Return',
        'values': ["max-return", "max"],
        'args': ['start_date', 'end_date', 'investment', 'target', 'save_file', 'suppress_output', 'json', keys.keys['ESTIMATION']['MOMENT'], keys.keys['ESTIMATION']['PERCENT'], keys.keys['ESTIMATION']['LIKE']],
        'description': "Maximize the return of the portfolio defined by the supplied list of ticker symbols. Returns an array representing the allocations to be made for each asset in a portfolio. If no start or end dates are specified, calculations default to the last 100 days of prices. You can specify an investment with the '-invest' flag, otherwise the result will be output in percentage terms. Note: This function will always allocate 100% to the asset with the highest return. It's a good way to check and see if there are bugs in the algorithm after changes.",
        'tickers': True,
    },
    "moving_averages": {
        'name': 'Moving Averages Series',
        'values': ["mov-averages", "mas"],
        'args': ['start_date', 'end_date', keys.keys['ESTIMATION']['MOMENT'], keys.keys['ESTIMATION']['PERCENT'], keys.keys['ESTIMATION']['LIKE']],
        'description': "Calculate the current moving averages. If no start or end dates are specified, calculations default to the last 100 days of prices.",
        'tickers': True,
    },
    "optimize_portfolio": {
        'name': 'Optimize Portfolio Variance',
        'values': ["optimize-portfolio", "opt"],
        'args': ['start_date', 'end_date', 'optimize_sharpe', 'investment', 'target', 'save_file', 'suppress_output', 'json', keys.keys['ESTIMATION']['MOMENT'], keys.keys['ESTIMATION']['PERCENT'], keys.keys['ESTIMATION']['LIKE']],
        'description': "Optimize a portfolio's risk return profile.  Returns an array representing the allocations to be made for each asset in a portfolio.",
        'tickers': True,
    },
    "optimize_portfolio_conditional_var": {
        'name': 'Optimize Portfolio Conditional Value At Risk',
        'values': ["optimize-cvar", "opt-cvar"],
        'args': ['start_date', 'end_date', 'investment', 'target', 'save_file', 'suppress_output', 'json', 'expiry', 'probability', keys.keys['ESTIMATION']['MOMENT'], keys.keys['ESTIMATION']['PERCENT'], keys.keys['ESTIMATION']['LIKE']],
        'description': "Optimizes the conditional value at risk, i.e. E(St | St < Sv) where Sv -> Prob(St<S0) = `prob` , for the portfolio defined by the list of inputted ticker symbols. Note: expiry is measured in years and is different from the start and end dates. Start and end dates are used to calibrate the model to a historical sample while expiry is used as the time horizon over which the value at risk is calculated into the future.",
        'tickers': True,
    },
    "plot_correlation": {
        'name': 'Plot Correlation Time Series',
        'values': ["plot-correlations", "plot-cors"],
        'args': ['start_date', 'end_date', 'save_file', keys.keys['ESTIMATION']['MOMENT'], keys.keys['ESTIMATION']['PERCENT'], keys.keys['ESTIMATION']['LIKE']],
        'description': "Generates a time series for the correlation of two ticker symbols over the specified date range.",
        'tickers': True,
    },
    "plot_dividends": {
        'name': 'Plot Discount Dividend Model',
        'values': ["plot-dividends", "plot-divs"],
        'args': ['save_file'],
        'description': "Generates a scatter plot graphic of the dividend history for the supplied ticker with a superimposed simple linear regression line. Note: this function only accepts one ticker at a time.",
        'tickers': True,
    },
    "plot_frontier": {
        'name': 'Plot Efficient Frontier',
        'values': ["plot-efficient-frontier", "plot-ef"],
        'args': ['start_date', 'end_date', 'save_file', 'steps', keys.keys['ESTIMATION']['MOMENT'], keys.keys['ESTIMATION']['PERCENT'], keys.keys['ESTIMATION']['LIKE']],
        'description': "Generates a scatter plot graphic of the portfolio\'s efficient frontier for the supplied list of tickers. The number of points calculated in the efficient frontier can be specifed as an integer with the -steps. If no -steps is provided, the value of the environment variable FRONTIER_STEPS will be used. If this value is not set, the function will default to a value of 5.",
        'tickers': True,
    },
    "plot_moving_averages": {
        'name': 'Plot Moving Averages Series',
        'values': ["plot-moving-averages", "plot-mas"],
        'args': ['start_date', 'end_date', 'save_file', keys.keys['ESTIMATION']['MOMENT'], keys.keys['ESTIMATION']['PERCENT'], keys.keys['ESTIMATION']['LIKE']],
        'description': "Generates a grouped bar chart of the moving averages for each equity in the supplied list of ticker symbols. If no start or end dates are specified, calculations default to the last 100 days of prices.",
        'tickers': True,
    },
    "plot_return_qq": {
        'name': 'Normality of Returns (QQ Plot)',
        'values': ["plot-return-qq", "plot-qq"],
        'args': ['start_date', 'end_date', 'save_file'],
        'description': "Generates a Q-Q Plot to graphically test the normality of returns for the inputted ticker symbol over the specified date range. If no start or date are specified, calculations default to the last 100 days of prices.",
        'tickers': True,
    },
    "plot_return_dist": {
        'name': 'Distribution of Returns',
        'values': ["plot-return-distribution", "plot-dist"],
        'args': ['start_date', 'end_date', 'save_file'],
        'description': 'Generates a histogram of the annualized daily return over the specified date range.',
        'tickers': True
    },
    "plot_risk_profile": {
        'name': 'Plot Risk Profile',
        'values': ["plot-risk-profile", "plot-rp"],
        'args': ['start_date', 'end_date', 'save_file', keys.keys['ESTIMATION']['MOMENT'], keys.keys['ESTIMATION']['PERCENT'], keys.keys['ESTIMATION']['LIKE']],
        'description': "Generates a scatter plot of the risk-return profile for symbol in the supplied list of ticker symbols. If no start or end dates are specified, calculations default to the last 100 days of prices.",
        'tickers': True,
    },
    "plot_yield_curve": {
        'name': 'Plot Yield Curve',
        'values': ["plot-yield-curve", "plot-yc"],
        'args': ['start_date', 'save_file'],
        'description': "Generates a plot of the latest United States Treasury Yield Curve. A yield curveo n a different date can be generated by specifying the date with an argument.",
        'tickers': False,
    },
    "price_history": {
        'name': 'Price History',
        'values': ["prices", "pr"],
        'args': ['start_date', 'end_date', 'save_file', 'suppress_output', 'json'],
        'description': "Prints the price histories for each inputted asset over the specified date range. If no date range is given, price histories will default to the last 100 days.",
        'tickers': True,
    },
    "purge": {
        'name': 'Purge All Data',
        'values': ["purge", "pu"],
        'args': None,
        'description': "Removes all files contained with the _installation_directory_/data/static/, _installation_directory_/data/cache/ and _installation_directory_/data/common/ directory, but retains the directories themselves.",
        'tickers': False,
    },
    "risk_free_rate": {
        'name': 'Risk Free Rate',
        'values': ["risk-free", "rf"],
        'args': None,
        'description': "Returns the current annualized US Treasury yield specified by the RISK_FREE environment variables. Allowable values for RISK_FREE environment variable: ONE_MONTH, TWO_MONTH, THREE_MONTH, SIX_MONTH, ONE_YEAR, TWO_YEAR, THREE_YEAR, FIVE_YEAR, SEVEN_YEAR, TEN_YEAR, TWENTY_YEAR, THIRTY_YEAR.",
        'tickers': False,
    },
    "risk_profile": {
        'name': 'Risk Profile',
        'values': ["risk-profile", "rp"],
        'args': ['start_date', 'end_date', 'save_file', 'suppress_output', 'json', keys.keys['ESTIMATION']['MOMENT'], keys.keys['ESTIMATION']['PERCENT'], keys.keys['ESTIMATION']['LIKE']],
        'description': "Calculate the risk-return profile for the supplied list of ticker symbols. If no start or end dates are specified, calculations default to the last 100 days of prices.",
        'tickers': True,
    },
    "screener": {
        'name': 'Watchlist Screener',
        'values': ["screen", "scr"],
        'args': ['discount', 'criteria'],
        'description': "Searchs equity spot prices that trade at a discount to the provided model. If no model is provided, the screener will default to the Discount Dividend Model. If no discount rate is provided, the screener will default to the cost of equity for a ticker calculated using the CAPM model.",
        'tickers': False,
    },
    "sharpe_ratio": {
        'name': 'Sharpe Ratio',
        'values': ["sharpe-ratio", "sr"],
        'args': ['start_date', 'end_date', 'save_file', 'json', keys.keys['ESTIMATION']['MOMENT'], keys.keys['ESTIMATION']['PERCENT'], keys.keys['ESTIMATION']['LIKE']],
        'description': "Computes the sharpe ratio for each tickers in the supplied list",
        'tickers': True,
    },
    "statistic": {
        'name': 'Last Reported Value of Financial Statistic',
        'values': ["stat", "s"],
        'args': ['save_file', 'suppress_output', 'json'],
        'description': "Retrieves the latest value for the supplied list of economic statistics. The available list of economic statistic can be found at https://www.quandl.com/data/FRED-Federal-Reserve-Economic-Data/documentation?anchor=growth; it is also stored in the minstallation_directory_/data/static/ directory of the application.",
        'tickers': True,
    },
    "statistic_history": {
        'name': 'Financial Statistic History',
        'values': ["stats", "ss"],
        'args': ['start_date', 'end_date', 'save_file', 'suppress_output', 'json'],
        'description': "Prints the statistic history for the supplied list of economic statistics.The available list of economic statistic can be found at https://www.quandl.com/data/FRED-Federal-Reserve-Economic-Data/documentation?anchor=growth; it is also stored in the _installation_directory_/data/static/ directory of the application.",
        'tickers': True,
    },
    "store": {
        'name': 'API Key Store',
        'values': ["store", "st"],
        'args': ['key', 'value'],
        'description': "Save API key to local _installation_directory_/data/common/ directory.",
        'tickers': False,
    },
    "version": {
        'name': 'Display Version',
        'values': ["version", "v"],
        'args': None,
        'description': "Display installed version of this library.",
        'tickers': False,
    },
    "watchlist": {
        'name': 'Stock Watchlist',
        'values': ["watch", "w"],
        'args': None,
        'description': "Saves the supplist list of tickers to your watchlist. These equity symbol are used by the screening algorithms when searching for stocks that trade at a discount.",
        'tickers': False,
    },
    "yield_curve": {
        'name': 'Latest Yield Curve',
        'values': ["yield-curve", "yc"],
        'args': ['start_date'],
        'description': "Displays the current United States Treasury Yield Curve.",
        'tickers': False,
    }
}
"""
A dictionary containing configuration information for function arguments. This dictionary is used at various points in the library, such as `scrilla.gui.widgets.functions` and `scrilla.util.helper.format_args`, to generate function interfaces. 
"""

GROUP_DICT = {
    'estimation_method': 'Estimation Method'
}
"""
"""

ARG_META_DICT = {
    'groups': ['estimation_method']
}

# Every argument has four ways of being inputted: short-dash-long, long-dash-long, short-dash-short, long-dash-short
ARG_DICT = {
    'start_date': {
        'name': 'Sample Start Date',
        'values': ['-start-date', '--start-date', '-start', '--start'],
        'description': 'Start date of historical sample',
        'default': '100 Trading Days Ago',
        'widget_type': 'date',
        'format': lambda s: datetime.datetime.strptime(s, '%Y-%m-%d').date(),
        'required': False,
        'syntax': '<YYYY-MM-DD>',
        'cli_only': False
    },
    'end_date': {
        'name': 'Sample End Date',
        'values': ['-end-date', '--end-date', '-end', '--end'],
        'description': 'End date of historical sample',
        'default': 'Last Trading Day',
        'widget_type': 'date',
        'format': lambda s: datetime.datetime.strptime(s, '%Y-%m-%d').date(),
        'required': False,
        'syntax': '<YYYY-MM-DD>',
        'cli_only': False
    },
    'target': {
        'name': 'Target Return',
        'values': ['-target-return', '--target-return', '-target', '--target'],
        'description': 'Constraint for target rate of return',
        'default': None,
        'widget_type': 'decimal',
        'format': float,
        'required': False,
        'syntax': '<value>',
        'cli_only': False
    },
    'discount': {
        'name': 'Discount Rate',
        'values': ['-discount-rate', '--discount-rate', '-discount', '--discount'],
        'description': 'Rate of return used to discount future cash flows to present',
        'default': 'Cost of equity',
        'widget_type': 'decimal',
        'format': float,
        'required': False,
        'syntax': '<value>',
        'cli_only': False
    },
    'investment': {
        'name': 'Total Investment',
        'values': ['-investment', '--investment', '-invest', '--invest'],
        'description': 'Total amount of money invested',
        'default': None,
        'widget_type': 'currency',
        'format': float,
        'required': False,
        'syntax': '<value>',
        'cli_only': False
    },
    'expiry': {
        'name': 'Expiration',
        'values': ['-expiry', '--expiry', '-exp', '--exp'],
        'description': 'Time until event expiration',
        'default': None,
        'widget_type': 'decimal',
        'format': float,
        'required': True,
        'syntax': '<value>',
        'cli_only': False
    },
    'probability': {
        'name': 'Loss Probability',
        'values': ['-probability', '--probability', '-prob', '--prob'],
        'description': 'Probability a loss will occur',
        'default': None,
        'widget_type': 'decimal',
        'format': float,
        'required': True,
        'syntax': '<value>',
        'cli_only': False
    },
    'steps': {
        'name': 'Efficient Frontier Data Points',
        'values': ['-frontier-steps', '--frontier-steps', '-steps', '--steps'],
        'description': 'Number of data points included in efficient frontier calculations',
        'default': 'FRONTIER_STEPS environment variable',
        'widget_type': 'integer',
        'format': int,
        'required': False,
        'syntax': '<value>',
        'cli_only': False
    },
    'criteria': {
        'name': 'Watchlist Screener Critia',
        'values': ['-criteria', '--criteria', '-crit', '--crit'],
        'description': 'Criteria used to sort saved watchlist',
        'default': None,
        'widget_type': 'select',
        'format': str,
        'required': False,
        'allowable': ['DDM', 'sharpe', 'volatility', 'return'],
        'syntax': '<value>',
        'cli_only': False
    },
    'save_file': {
        'name': 'Save File Location',
        'values': ['-save-file', '--save-file', '-save', '--save'],
        'description': 'Location where file will be saved',
        'default': None,
        'widget_type': None,
        'format': str,
        'required': False,
        'syntax': '<path>',
        'cli_only': True
    },
    'key': {
        'name': 'Key-Value Key',
        'values': ['-key', '--key', '-k', '--k'],
        'description': 'API Key that will be saved to __installation_dir__/data/common/',
        'default': None,
        'format': str,
        'widget_type': None,
        'required': True,
        'allowable': ["ALPHA_VANTAGE_KEY", "QUANDL_KEY", "IEX_KEY"],
        'syntax': '<value>',
        'cli_only': True
    },
    'value': {
        'name': 'Key-Value Value',
        'values': ['-value', '--value', '-v', '--v'],
        'description': 'API Key-Value that will be saved to __installation_dir__/data/common/',
        'default': None,
        'widget_type': None,
        'format': str,
        'required': True,
        'syntax': '<value>',
        'cli_only': True
    },
    'optimize_sharpe': {
        'name': 'Optimize Portfolio Sharpe',
        'values': ['-sharpe', '--sharpe', '-sh', '--sh'],
        'description': 'Flag to optimize portfolio Sharpe Ratio',
        'default': None,
        'widget_type': 'flag',
        'format': bool,
        'required': False,
        'syntax': None,
        'cli_only': False
    },
    'json': {
        'name': 'JSON Display',
        'values': ['-json', '--json', '-js', '--js'],
        'description': 'Print output to screen as JSON',
        'default': None,
        'widget_type': 'flag',
        'format': bool,
        'required': False,
        'syntax': None,
        'cli_only': True
    },
    'suppress_output': {
        'name': 'No Display',
        'values': ['-quiet', '--quiet', "-q", "--q"],
        'description': 'Suppress all console output',
        'default': None,
        'widget_type': 'flag',
        'format': bool,
        'required': False,
        'syntax': None,
        'cli_only': True
    },
    'moments': {
        'name': 'Moment Matching',
        'values': ['-moments', '--moments', '-mom', '--mom'],
        'description': 'Statistics are calculated using method of moment matching',
        'default': None,
        'widget_type': 'group',
        'format': 'group',
        'group': 'estimation_method',
        'required': False,
        'syntax': None,
        'cli_only': False
    },
    'percentiles': {
        'name': 'Percentile Matching',
        'values': ['-percentiles', '--percentiles', '-per', '--per'],
        'description': 'Statistics are calculated using method of percentile matching',
        'default': None,
        'widget_type': 'group',
        'format': 'group',
        'group': 'estimation_method',
        'required': False,
        'syntax': None,
        'cli_only': False
    },
    'likelihood': {
        'name': 'Maximum Likelihood',
        'values': ['-likelihood', '--likelihood', '-like', '--like'],
        'description': 'Statistics are calculated using maximum likelihood estimation',
        'default': None,
        'widget_type': 'group',
        'format': 'group',
        'group': 'estimation_method',
        'required': False,
        'syntax': None,
        'cli_only': False
    }
}
"""
A dictionary containing configuration information for application arguments. This dictionary is used at various points in the library, such as `scrilla.gui.widgets.functions` and `scrilla.util.helper`, to parse construct and parse input elements.

.. notes::
    * Every argument has four ways of being inputted: short-dash-long, long-dash-long, short-dash-short, long-dash-short, e.g. the following commands are all equivalent,
    ```
    scrilla risk-profile LMT GD LNT -json
    ```
    ```
    scrilla risk-profile LMT GD LNT --json
    ```
    ```
    scrilla risk-profile LMT GD LNT -js
    ```
    ```
    scrilla risk-profile LMT GD LNT --js
    ```
    * arguments with a format of `group` are mutually exclusively modes, similar to a radio button.
"""
