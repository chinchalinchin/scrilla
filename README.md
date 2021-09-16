# scrilla: A Financial Optimization Application

## Table of Contents
- [Setup](#setup)
    - [Installation](#installation)
    - [Dependencies](#dependencies)
    - [Configuration](#configuration)
- [Environment](#environment)
    - [Required Configuration](#required-configuration)
    - [Optional Configuration](#optional-configuration)
- [Usage](#usage)
    - [Command Line](#command-line)
    - [Programmatic](#programmatic)

This is a financial application that calculates asset correlations, statistics and optimal portfolio allocations using data it retrieves from external services (currently: [AlphaVantage](https://www.alphavantage.co), [IEX](https://iexcloud.io/) and [Quandl](https://www.quandl.com/)). Statistics are calculated using [Ito Calculus](https://en.wikipedia.org/wiki/It%C3%B4_calculus) and should be consistent with the results demanded by [Modern Portfolio Theory](https://en.wikipedia.org/wiki/Modern_portfolio_theory) and [Financial Engineering](https://en.wikipedia.org/wiki/Black%E2%80%93Scholes_equation). The portfolios are optimized by minimizing the portfolio's variance/volatility, i.e. by finding the optimal spot on the portfolio's efficient frontier as defined by the [CAPM model](https://en.wikipedia.org/wiki/Capital_asset_pricing_model). Alternatively, portfolios can be optimized by maximizing the portfolio's [Sharpe ratio](https://en.wikipedia.org/wiki/Sharpe_ratio) or by minimizing the portfolio's [Conditional Value at Risk](https://en.wikipedia.org/wiki/Expected_shortfall#Optimization_of_expected_shortfall).

The program's functions are wrapped in [PyQt5](https://doc.qt.io/qtforpython/index.html) widgets which provide a user interface (this feature is still in development and may explode). In addition, visualizations are created by [matplotlib](https://matplotlib.org/3.3.3/contents.html) for easier presentation.

The links below will take you to the registration pages for each API service Key,

[AlphaVantage API Key Registration](https://www.alphavantage.co/support/#api-key)<br>
[Quandl API Key Registration](https://www.quandl.com/account/api)<br>
[IEX API Key Registration](https://iexcloud.io/)<br>

Note this application optimizes across asset classes, i.e. the theoretical portfolio being constructed can be composed of equities, cryptocurrencies or both. In a future release, I would like to include fixed income assets, volatility assets (<i>VIX</i> futures, options, etc.) and other derivatives, but for now, only those two asset types are supported. I am looking for a good API that provides historical data on the other types of financial instruments before I bring them into the optimization algorithm, so if you know of one, contact me. 

# Setup

## Installation

Install the package with the <b>Python</b> package manager,

`pip install scrilla` 

To keep the installation as minimal as possible, the base package does not include the GUI libraries. You can install the optional GUI dependency with,

`pip install scrilla[gui]`

Note, the GUI has a different CLI entrypoint, namely,

`scrilla-gui`

If you prefer, you can build from source. `git clone` the [repository](https://github.com/chinchalinchin/scrilla) and then from the root directory build the library,

`python3 -m build` 

`cd` into the generated <i>/dist/</i>  to manually install the packaged code,

`pip install scrilla-<major>.<minor>.<micro>-py3-none-any.whl`

## Dependencies

You will need Python3.8 or greater. This application depends on the following <b>Python</b> libraries: 

### Required
- [dateutil](https://dateutil.readthedocs.io/en/stable/index.html)>=2.8.2<br>
- [holidays](https://pypi.org/project/holidays/)>=0.10.4<br>
- [matplotlib](https://pypi.org/project/matplotlib/)>=3.3.3<br>
- [numpy](https://pypi.org/project/numpy/)>=1.19.3<br>
- [python-dotenv](https://pypi.org/project/python-dotenv/)>=0.17.0<br>
- [requests](https://pypi.org/project/requests/)>=2.25.0<br>
- [scipy](https://pypi.org/project/scipy/)>=1.5.4<br>

### Optional
- [PyQt5](https://pypi.org/project/PyQt5/)>=5.14<br>

This libraries will be installed during the `pip install` command. If you wish to use the GUI, you will also need to ensure your operating system has a [Qt5](https://doc.qt.io/) library,

`sudo apt-get install qt5-default`

The GUI will not function without a <b>Qt</b> library.

## Configuration

In order to use this application, you will need to register for API keys. The program will need to be made aware of these keys somehow. The best option is storing these credentials in environment variables. See [Required Configuration](#required-configuration) for more information. You can also invoke the CLI function `store` to store the credentials in the local installation <i>/data/common/</i> directory. To do so,

`scrilla -store <key>=<value>`

where `key` is one of the values: `ALPHA_VANTAGE_KEY`, `QUANDL_KEY` or `IEX_KEY`. `value` is the corresponding key itself given to you after registration. The `key` is case-sensitive and there should be no spaces in the expression `key=value`

# Environment

A sample environment file is located [here](https://github.com/chinchalinchin/scrilla/blob/development/env/.sample.env), along with comments describing the purpose of each variable. The application sets sensible defaults for most of the environment variable configurations, but there are several required environment variables you will need to set yourself. 

## Required Configuration

As mentioned, you will need to register for API keys at <b>AlphaVantage</b>, <b>IEX</b> and <b>Quandl</b>. One way of passing API keys to the program is by storing these in your session's environment. <b>scrilla</b> will search for environment variables named <b>ALPHA_VANTAGE_KEY</b>, <b>QUANDL_KEY</b> and <b>IEX_KEY</b>. You can add the following lines to your <i>.bashrc</i> profile or corresponding configuration file for whatever shell you are using,

`export ALPHA_VANTAGE_KEY=<key goes here>`<br>
`export QUANDL_KEY=<key goes here>`<br>
`export IEX_KEY=<key goes here>`<br>

If no API keys are found in these variables, the application will not function properly; be sure to load these variables into your shell session before using <b>scrilla</b>. 

## Optional Configuration 

<b>scrilla</b> can be configured with the following optional environment variables. Each variable in this list has a suitable default set and so does not need changed unless the user prefers a different setting.

- RISK_FREE

Determines which annualized US-Treasury yield is used as stand-in for the risk free rate. This variable will default to a value of `10-Year`, but can be modified to any of the following: `3-Month`, `5-Year`, `10-Year`, or `30-Year`.

- MARKET_PROXY

Determines which ticker symbol is used as a proxy for the overall market return. This variable will default to a value of `SPY`, but can be set to any ticker on the stock market. Recommended values: `SPY`, `QQQ`, `DJI` or `VTI`.

- FRONTIER_STEPS

Determines the number of data points in a portfolio's efficient frontier. This variable will default to a value of `5`, but can be set equal to any integer.

- MA_1, MA_2, MA_3

Determines the number of days used in the sample for moving average series and plots. These variables default to the values of `20`, `60` and `100`. In other words, by default, moving average plots will display the 20-day moving average, the 60-day moving average and the 100-day moving average. These variables can be set equal to any integer, as long as <b>MA_1</b> < <b>MA_2</b> < <b>MA_3</b>. 

- FILE_EXT 

Determines the type of files that are output by <b>scrilla</b>. This variable is currently only defined for an argument of `json`. A future release will include `csv`. 

- LOG_LEVEL

Determines the amount of output. Defaults to `info`. Allowable values: `none`, `info`, `debug` or `verbose`. Be warned, `verbose` is <i>extremely</i> verbose.

# Usage

## Command Line 

Most functions have been wired into command line arguments. For a full list of <b>scrilla</b>'s functionality,

`scrilla -help`

The main usage of <b>scrilla</b> is detailed below.

### Optimization

1. Volatility Minimization & Sharpe-Ratio Maximization

A portfolio of consisting of the equities <i>ALLY</i>, <i>BX</i> and <i>SONY</i> can be optimized with the following command,

`scrilla -opt ALLY BX SONY`

By default, <b>scrilla</b> will optimize over the last 100 trading days. If you wish to optimize over a different time period, you may use the `-start` and `-end` argument flags to provide starting and ending dates in the `YYYY-MM-DD` format. 

Also by default, the optimization function will minimize the portfolio variance. You can also specify the portfolio should be maximized with respect to the Sharpe ratio,

`scrilla -opt -sh ALLY BX SONY`

There are several other arguments you may use to configure your optimization program. The full list of arguments is shown below,

`scrilla -opt -sh -start <YYYY-MM-DD> -end <YYYY-MM-DD> -save <absolute path to json file> -target <double> -invest <double> [TICKERS]`

`-target` will optimize the portfolio with the additional constraint that its rate of return must equal `target`. Note the target return must be between the minimum rate of return and maximum rate of return in a basket of equities. For example, if ALLY had a rate of return of 10%, BX 15%, SONY 20%, the frontier of possible rates of returns resides in the range [10%, 20%]. It is impossible to combine the equities in such a way to get a rate of return less than 10% or one greater than 20%. Note, this assumes shorting is not possible. A future release will relax this assumption and allow portfolio weights to be negative.

`-invest` represents the total amount of money invested in a portfolio. 

For example, the following command,

`scrilla -opt -sh -save <path-to-json-file> -target 0.25 -invest 10000 -start 2020-01-03 -end 2021-05-15 ALLY BX SONY`

Will optimize a portfolio consisting of <i>ALLY</i>, <i>BX</i> and <i>SONY</i> using historical data between the dates of January 1st, 2020 and May 15th, 2021. The portfolio will be constrained to return a rate of 25%. A total $10,000 will be invested into this portfolio (to the nearest whole share). The output of this command will look like this,

> ---------------------------------------------- Results ----------------------------------------------<br>
> ----------------------------------------------------------------------------------------------------<br>
> ----------------------------------- Optimal Percentage Allocation -----------------------------------<br>
>           ALLY = 22.83 %<br>
>           BX = 19.26 %<br>
>           SONY = 57.91 %<br>
> ----------------------------------------------------------------------------------------------------<br>
> ----------------------------------------------------------------------------------------------------<br>
> -------------------------------------- Optimal Share Allocation --------------------------------------<br>
>           ALLY = 42<br>
>           BX = 15<br>
>           SONY = 56<br>
> -------------------------------------- Optimal Portfolio Value --------------------------------------<br>
>           >> Total  = $ 9893.98<br>
> ---------------------------------------- Risk-Return Profile ----------------------------------------<br>
>           >> Return  =  0.25<br>
>           >> Volatility  =  0.201<br>
> ----------------------------------------------------------------------------------------------------<br>

Note the optimal share allocation does not allow fractional shares. <b>scrilla</b> will attempt to get as close to the total investment inputted without going over using only whole shares. Also note the return of this portfolio is 25%, as this was inputted into the target return constraint. 

2. Conditional Value at Risk Minimization

The portfolio optimization can also be done by minimizing its conditional value at risk. Because the underlying calculations are a bit different, this function is accessed through a different command and requires different arguments. 

The two new arguments are `prob` and `expiry`. `prob`, in essence, represents the percentile of the portfolio's distribution on which the value at risk will be conditioned. In other words, if the portfolio value is represented by a random variable P, for a given value of P=*p*, the `prob` is the probability such that, 

`Probability(P<p)=prob`

`expiry` represents the time horizon over which the value at risk will be calculated, i.e. the point in time in which the hypothetical loss occurs. 

With these two new arguments, a portfolio's conditional value at risk can be optimized using the following,

`scrilla -opt-cvar -prob 0.05 -expiry 0.5 ALLY BX SONY`

The command given above will optimize the portfolio consisting of <b>ALLY</b>, <b>BX</b> and <b>SONY</b> over the next half year (`expiry` = 0.5) subject to the value at risk in the 5th percentile. 

### Other Notable Features

1. Discount Dividend Model

<b>scrilla</b> will pull an equity's dividend payment history, regress the payment amount against its date and infer a linear regression from this time series. It will use this model to project future dividend payments and then calculate the current cost of equity and use that to discount the sum of dividend payments back to the present,

`scrilla -ddm ALLY`

Alternatively, you can visualize the dividend payments against the regression model,

`scrilla -plot-div ALLY`

2. Financial Statistics
    - Beta: `scrilla -capm-beta [TICKERS]`
    - Correlation Matrix: `scrilla -cor [TICKERS]`
    - Cost Of Equity: `scrilla -capm-equity [TICKERS]`
    - Risk-Return Profile: `scrilla -rr [TICKERS]`
    - Sharpe Ratio: `scrilla -sharpe [TICKERS]`

3. Stock Watchlist and Screening

Stocks can be added to your watchlist with,

`scrilla -watch [TICKERS]`

You can then screen stocks according to some criteria. For example, the following command will search your watchlist for stock prices that are less than their Discount Dividend Model (very rare this happens...),

`scrilla -screen -model DDM`

4. Visualizations
    - Discount Dividend Model: `scrilla -plot-div [TICKER]`
        - NOTE: THIS FUNCTION ONLY ACCEPTS ONE TICKER AT A TIME.
    - Efficient Fronter: `scrilla -plot-ef [TICKERS]`
    - Moving Averages: `scrilla -plot-mov [TICKERS]`
    - Risk Return Profile: `scrilla -plot-rr [TICKERS]`
    - Yield Curve: `scrilla -plot-yield` (not implemented yet)

## Programmatic 

This package is made up of several top-level modules and various submodules, grouped according to the following name space:

- scrilla<br>
    - analysis<br>
        - calculator<br>
        - markets<br>
        - optimizer<br>
        - statistics<br>
    - cache<br>
    - errors<br>
    - files<br>
    - main<br>
    - objects<br>
        - cashflow<br>
        - portfolio<br>
    - services<br>
    - settings<br>
    - util<br>
        - formatter<br>
        - helper<br>
        - outputter<br>
        - plotter<br>

In general, you should not need to interact with any of the top level modules. <b>main</b> is the entrypoint for the CLI application, <b>files</b> is used to format and parse files, <b>cache</b> manages the local <b>sqlite</b> cache, <b>settings</b> parses environment variables to configure the application, <b>static</b> provides a dictionary of constants, <b>errors</b> provides the Exception classes for the application; these modules function entirely under the hood. On occasion, however, you may need to access <b>services</b>, as this is where raw data from the external services is requested and parsed. 

### scrilla.services

The four functions of interest in this module are:

1. `scrilla.services.get_daily_price_history(ticker, start_date=None, end_date=None, asset_type=None)`<br>
    <b>Description:</b><br>
    Wrapper around external service request for price data. Relies on an instance of `PriceManager` configured by `settings.PRICE_MANAGER` value, which in turn is configured by the `PRICE_MANAGER` environment variable, to hydrate with data. <br>
    
    Before deferring to the `PriceManager` and letting it call the external service, however, this function checks if response is in local cache. If the response is not in the cache, it will pass the request off to `PriceManager` and then save the resposne in the cache so subsequent calls to the function can bypass the service request. Used to prevent excessive external HTTP requests and improve the performance of the application. Other parts of the program should interface with the external price data services through this function to utilize the cache functionality.<br>

    <b>Arguments:</b><br>
    1. ticker :  `str`<br>
        Required. Ticker symbol corresponding to the price history to be retrieved. <br>
    2. start_date : `datetime.date`<br>
        Optional. Start date of price history. Defaults to None. If `start_date is None`, the calculation is made as if the `start_date` were set to 100 trading days ago. If `get_asset_type(ticker)=="crypto"`, this includes weekends and holidays. If `get_asset_type(ticker)=="equity"`, this excludes weekends and holidays. <br>
    3. end_date : `datetime.date`<br>
        Optional End date of price history. Defaults to None. If `end_date is None`, the calculation is made as if the `end_date` were set to today. If `get_asset_type(ticker)=="crypto"`, this means today regardless. If `get_asset_type(ticker)=="equity"`, this excludes weekends and holidays so that `end_date` is set to the previous business date. <br>
    4. asset_type : `str`<br>
        Optional. Asset type of the ticker whose history is to be retrieved. Used to prevent excessive calls to IO and list searching. `asset_type` is determined by comparing the ticker symbol `ticker` to a large static list of ticker symbols maintained in installation directory's <i>/data/static/</i> subdirectory, which can slow the program down if the file is constantly accessed and lots of comparison are made against it. Once an `asset_type` is calculated, it is best to preserve it in the process environment somehow, so this function allows the value to be passed in. If no value is detected, it will make a call to the aforementioned directory and parse the file to determine to the `asset_type`. Asset types are statically accessible through the `scrilla.static.keys['ASSETS']` dictionary.<br>

    <b>Returns:</b><br>
    `{ 'date' (str) : { 'open': value (str), 'close': value (str) }, 'date' (str): { 'open' : value (str), 'close' : value(str) }, ...}`<br>
    Dictionary with date strings formatted `YYYY-MM-DD` as keys and a nested dictionary containing the 'open' and 'close' price as values. Ordered from latest to earliest. <br>

    <b>Raises:</b><br>
    1. scrilla.errors.InputValidationError<br>
        If the arguments inputted into the function fail to exist within the domain the function, this error will be thrown.<br>
    2. scrilla.errors.APIResponseError<br>
        If the external service rejects the request for price data, whether because of rate limits or some other factor, the function will raise this exception.<br>
    3. KeyError<br>
        If the inputted or validated dates do not exist in the price history, a KeyError will be thrown. This could be due to the equity not having enough price history, i.e. it started trading a month ago and doesn't have 100 days worth of prices yet, or some other anomalous event in an equity's history.<br>
    4. errors.ConfigurationError<br>
        If one of the settings is improperly configured or one of the environment variables was unable to be parsed from the environment, this error will be thrown.<br>

    
2. `scrilla.services.get_daily_fred_history(symbol, start_date=None, end_date=None, asset_type=None)`<br>
    <b>Description:</b><br>
    Wrapper around external service request for financial statistics data constructed by the Federal Reserve Economic Data. Relies on an instance of `StatManager` configured by `settings.STAT_MANAGER` value, which in turn is configured by the `STAT_MANAGER` environment variable, to hydrate with data.<br>
    
    Before deferring to the `StatManager` and letting it call the external service, however, this function checks if response is in local cache. If the response is not in the cache, it will pass the request off to `StatManager` and then save the resposne in the cache so subsequent calls to the function can bypass the service request. Used to prevent excessive external HTTP requests and improve the performance of the application. Other parts of the program should interface with the external statistics data services through this function to utilize the cache functionality.<br>

    <b>Arguments:</b><br>
    1. symbol: `str`<br>
        Required. Symbol representing the statistic whose history is to be retrieved. List of allowable values can be found [here](https://www.quandl.com/data/FRED-Federal-Reserve-Economic-Data/documentation)<br>
    2. start_date : `datetime.date`<br>
        Optional. Start date of price history. Defaults to None. If `start_date is None`, the calculation is made as if the `start_date` were set to 100 trading days ago. This excludes weekends and holidays.<br>
    3. end_date :  `datetime.date`<br>
        Optional End date of price history. Defaults to None. If `end_date is None`, the calculation is made as if the `end_date` were set to today. This excludes weekends and holidays so that `end_date` is set to the last previous business date.<br>

    <b>Returns:</b><br>
    `{ 'date' (str) :  value (str),  'date' (str):  value (str), ... }`<br>
    Dictionary with date strings formatted `YYYY-MM-DD` as keys and the statistic on that date as the corresponding value.<br>

    <b>Raises</b><br>
    1. scrilla.errors.InputValidationError<br>
        If the arguments inputted into the function fail to exist within the domain the function, this error will be thrown<br>
    2. scrilla.errors.APIResponseError<br>
        If the external service rejects the request for price data, whether because of rate limits or some other factor, the function will raise this exception<br>
    3. KeyError<br>
        If the inputted or validated dates do not exist in the price history, a KeyError will be thrown. This could be due to the equity not having enough price history, i.e. it started trading a month ago and doesn't have 100 days worth of prices yet, or some other anomalous event in an equity's history.<br> 
    4. errors.ConfigurationError<br>
        If one of the settings is improperly configured or one of the environment variables was unable to be parsed from the environment, this error will be thrown.<br>

3. `scrilla.services.get_dividend_history(ticker)`<br>
    <b>Description:</b><br>
     Wrapper around external service request for dividend payment data. Relies on an instance of `DivManager` configured by `settings.DIV_MANAGER` value, which in turn is configured by the `DIV_MANAGER` environment variable, to hydrate with data.<br>
    
    Before deferring to the `DivManager` and letting it call the external service, however, this function checks if response is in local cache. If the response is not in the cache, it will pass the request off to `DivManager` and then save the response in the cache so subsequent calls to the function can bypass the service request. Used to prevent excessive external HTTP requests and improve the performance of the application. Other parts of the program should interface with the external statistics data services through this function to utilize the cache functionality.<br>

    <b>Arguments:</b><br>
    1. ticker : `str` : Required. Ticker symbol of the equity whose dividend history is to be retrieved.<br>

    <b>Returns:</b><br>
    `{ 'date' (str) :  amount (str),  'date' (str):  amount (str), ... }`<br>
    Dictionary with date strings formatted `YYYY-MM-DD` as keys and the dividend payment amount on that date as the corresponding value.<br>

    <b>Raises</b><br>
    1. scrilla.errors.InputValidationError<br>
        If the arguments inputted into the function fail to exist within the domain the function, this error will be thrown<br>
    2. scrilla.errors.APIResponseError<br>
        If the external service rejects the request for price data, whether because of rate limits or some other factor, the function will raise this exception<br>
    3. KeyError<br>
        If the inputted or validated dates do not exist in the price history, a KeyError will be thrown. This could be due to the equity not having enough price history, i.e. it started trading a month ago and doesn't have 100 days worth of prices yet, or some other anomalous event in an equity's history.<br> 
    4. errors.ConfigurationError<br>
        If one of the settings is improperly configured or one of the environment variables was unable to be parsed from the environment, this error will be thrown.<br>
        
4. `scrilla.services.get_risk_free_rate()`<br>
    <b>Description: </b><br>
        This function will retrieve the current value of the risk free rate (annualized yield on a US Treasury) as a decimal. The US Treasury yield used as a proxy for the risk free rate can be configured through the <b>RISK_FREE</b> environment variable. See [optional configuration](#optional-configuration) for more details.
    <br>

### scrilla.analysis.markets

1. `scrilla.analysis.markets.sharpe_ratio`<br>

2. `scrilla.analysis.markets.market_premium`<br>

3. `scrilla.analysis.markets.market_beta`<br>

4. `scrilla.analysis.markets.cost_of_equity`<br>

### scrilla.analysis.optimizer

1. `scrilla.analysis.optimizer.optimize_portfolio_variance`<br>

2. `scrilla.analysis.optimizer.maximize_sharpe_ratio`<br>

3. `scrilla.analysis.optimizer.maximize_portfolio_return`<br>
    <b>Description:</b><br>
        description goes here
    <br><br>
    <b>Note:</b><br>
        The rate of return of a portfolio of assets is a linear function with respect to the asset weights. IAs a result, this function should always allocate 100% of any given portfolio to the asset with the highest expected rate of return, i.e. if you have two assets where one asset has a 10% rate of return and a second asset has a 20% rate of return, the maximum rate of return for a portfolio composed of both assets is produced when 100% of the portfolio is invested in the asset with a 20% rate of return.<br>

### scrilla.analysis.statistics

1. `scrilla.analysis.statistics.sample_correlation`<br>

2. `scrilla.analysis.statistics.recursive_rolling_correlation`<br>

3. `scrilla.analysis.statistics.sample_mean`<br>

4. `scrilla.anaylsis.statistics.recursive_rolling_mean`<br>

5. `scrilla.anaylsis.statistics.sample_variance`<br>

6. `scrilla.analysis.statistics.recursive_rolling_variance`<br>

7. `scrilla.anaylsis.statistics.sample_covariance`<br>

8. `scrilla.anaylsis.statistics.recursive_rolling_covariance`<br>

9. `scrilla.analysis.statistics.regression_beta`<br>

10. `scrilla.analysis.statistics.regression_alpha`<br>

11. `scrilla.analysis.statistics.calculate_moving_averages`<br>

12. `scrilla.analysis.statistics.calculate_risk_return`<br>

13. `scrilla.analysis.statistics.calculate_return_covariance`<br>

14. `scrilla.analysis.statistics.calculate_ito_correlation`<br>

15. `scrilla.anaylsis.statistics.ito_correlation_matrix`<br>

### scrilla.objects.cashflow.Cashflow

### scrilla.objects.portfolio.Portfolio

# Notes

1. The following symbols have both equity and crypto assets trading on exchanges:

['ABT', 'AC', 'ADT', 'ADX', 'AE', 'AGI', 'AI', 'AIR', 'AMP', 'AVT', 'BCC', 'BCD', 'BCH', 'BCX', 'BDL', 'BFT', 'BIS', 'BLK', 'BQ', 'BRX', 'BTA', 'BTG', 'CAT', 'CMP', 'CMT', 'CNX', 'CTR', 'CURE', 'DAR', 'DASH', 'DBC', 'DCT', 'DDF', 'DFS', 'DTB', 'DYN', 'EBTC', 'ECC', 'EFL', 'ELA', 'ELF','EMB', 'ENG', 'ENJ', 'EOS', 'EOT', 'EQT', 'ERC', 'ETH', 'ETN', 'EVX', 'EXP', 'FCT', 'FLO', 'FLT', 'FTC', 'FUN', 'GAM', 'GBX', 'GEO', 'GLD', 'GNT', 'GRC', 'GTO', 'INF', 'INS', 'INT', 'IXC', 'KIN', 'LBC', 'LEND', 'LTC', 'MAX', 'MCO', 'MEC', 'MED', 'MGC', 'MINT', 'MLN', 'MNE', 'MOD', 'MSP', 'MTH', 'MTN', 'MUE', 'NAV', 'NEO', 'NEOS', 'NET', 'NMR', 'NOBL', 'NXC', 'OCN', 'OPT', 'PBT', 'PING', 'PPC', 'PPT', 'PRG', 'PRO', 'PST', 'PTC', 'QLC', 'QTUM','R', 'RDN', 'REC', 'RVT', 'SALT', 'SAN', 'SC', 'SKY', 'SLS', 'SPR', 'SNX', 'STK', 'STX', 'SUB', 'SWT', 'THC', 'TKR', 'TRC', 'TRST', 'TRUE', 'TRX', 'TX', 'UNB', 'VERI', 'VIVO', 'VOX', 'VPN', 'VRM', 'VRS', 'VSL', 'VTC', 'VTR', 'WDC', 'WGO', 'WTT', 'XEL', 'NEM', 'ZEN']

Since there is no way good way to distinguish whether or not the asset is an equity or a cryptocurrency based on the value of the ticker alone, the module functions `scrilla.files.get_asset_type` and `scrilla.errors.validate_asset_type` will always default to the equity ticker for the above symbols. 

This is not the greatest solution, as all the crypto symbols given above are inaccessible to analysis. In particular, `ETH` represents a popular crypto that cannot be analyzed, which represents a major failing of the current application.

The way the `service` module works, `PriceManager` can be forced to retrieve the crypto asset's prices instead of the equity asset's through the `services.PriceManager.get_prices` method by providing the method an argument of `asset_type='crypto'`; However, the `service` module function `services.get_daily_price_history`, which is the point of contact between the `PriceManager` and the rest of the application, wraps calls to the `PriceManager.get_prices` method in a cache persistence layer (meaning, `get_daily_price_history` checks if prices exist in the cache before passing the request off to an external service query). The cache doesn't distinguish asset types currently. The `PriceCache` stores prices based on the inputs (<i>ticker, date, open close, close price</i>). So, even if the `PriceManager` is forced to get crypto prices on the first call, subsequent calls to the same `get_daily_price_history` function will likely break the application, or at least lead to misleading results, since the cache will contain a set of prices that doesn't necessarily map one-to-one with its ticker symbol.

If the above problem is to be solved, the cache needs modified to separate prices based on asset type.


# Documentation
- [dateutil](https://dateutil.readthedocs.io/en/stable/index.html)
- [holidays](https://github.com/dr-prodigy/python-holidays)
- [matplotlib](https://matplotlib.org/)
- [numpy](https://numpy.org/doc/)
- [pyqt](https://doc.qt.io/qtforpython/)
- [requests](https://docs.python-requests.org/en/latest/)
- [scipy](https://www.scipy.org/docs.html)
- [sqlite3](https://docs.python.org/3/library/sqlite3.html)