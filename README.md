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

If you prefer, you can build from source. `git clone` the [repository](https://github.com/chinchalinchin/scrilla) and then from the root directory build the library,

`python3 -m build` 

`cd` into the generated <i>/dist/</i>  to manually install the packaged code,

`pip install scrilla-<major>.<minor>.<micro>-py3-none-any.whl`

## Dependencies

You will need Python3.8 or greater. This application depends on the following <b>Python</b> libraries: 

- [python-dotenv](https://pypi.org/project/python-dotenv/)>=0.17.0<br>
- [requests](https://pypi.org/project/requests/)>=2.25.0<br>
- [numpy](https://pypi.org/project/numpy/)>=1.19.3<br>
- [scipy](https://pypi.org/project/scipy/)>=1.5.4<br>
- [matplotlib](https://pypi.org/project/matplotlib/)>=3.3.3<br>
- [holidays](https://pypi.org/project/holidays/)>=0.10.4<br>
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
    - main<br>
    - files<br>
    - services<br>
    - settings<br>
    - analysis<br>
        - calculator<br>
        - markets<br>
        - optimizer<br>
        - statistics<br>
    - objects
        - cashflow<br>
        - portfolio<br>
    - util<br>
        - formatter<br>
        - helper<br>
        - outputter<br>
        - plotter<br>

In general, you should not need to interact with any of the top level modules. <b>main</b> is the entrypoint for the CLI application, <b>files</b> is used to format and parse files and manage the local cache, <b>settings</b> parses environment variables to configure the application; these modules function entirely under the hood. On occasion, however, you may need to access <b>services</b>, as this is where raw data from the external services is requested and parsed. 

### scrilla.services

The four functions of interest in this module are:

1. `scrilla.services.get_daily_price_history(ticker, start_date=None, end_date=None)`<br>
    <b>Description:</b><br>
        This function will retrieve the price history for the equity specified by the `ticker` argument. `ticker` must be the symbol associated with the equity on the stock exchange, e.g. MSFT = Microsft, TSLA = Tesla, etc. If no `start_date` or `end_date` are provided, the function returns the last 100 trading days worth of information.
    <br><br>
    <b>Arguments:</b><br>
    - `ticker : str` : Required. Ticker symbol of the equity.<br>
    - `start_date: datetime.date` : Optional. Start date of analysis range. Defaults to `None`<br> 
    - `end_date: datetime.date` : Optional. End date of analysis range. Defaults to `None`<br>

    <b>Returns:</b><br>
    a dictionary of prices with the `YYYY-MM-DD` formatted date as key. The dictionary is sorted latest price to earliest price.<br>
    
2. `scrilla.services.get_daily_stat_history(statistic, start_date=None, end_date=None)`<br>
    <b>Description:</b><br>
        This function will retrieve the price history for the financial statistic specifed by the `statistic` argument. 
    <br><br>
    <b>Arguments:</b><br>
    - `statistic : str`: Required. Statistic symbol for quantity of interest. A list of allowable values can be found [here](https://www.quandl.com/data/FRED-Federal-Reserve-Economic-Data/documentation)<br>
    - `start_date: datetime.date` : Optional. Start date of analysis range. Defaults to `None`<br> 
    - `end_date: datetime.date` : Optional. End date of analysis range. Defaults to `None`<br>

3. `scrilla.services.get_dividend_history(ticker)`<br>
    <b>Description:</b><br>
        This function will retrieve the dividend payment history (i.e. the date on which the payment was <i>made</i>, not the date the payment was declared) for the equity specified by the `ticker` arugment. `ticker` must be the symobl assoccaited with the equity on the stock exchange. 
    <br><br>
    <b>Arguments:</b><br>
    - `ticker : str` : Required. Ticker symbol of the equity.<br>

4. `scrilla.services.get_risk_free_rate()`<br>
    <b>Description: </b><br>
        This function will retrieve the current value of the risk free rate (annualized yield on a US Treasury). The risk free rate can be configured through the <b>RISK_FREE</b> environment variable. See [optional configuration](#optional-configuration) for more details.
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