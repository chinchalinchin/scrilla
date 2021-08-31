# scrilla: A Financial Optimization Application

## Table of Contaners
- Setup 
- Environment
    - [Required Configuration](#required-configuration)
    - [Optional Configuration](#optional-configuration)
- Usage
    - [Command Line](#command-line)
    - [Programmatic](#programmatic)

This is a financial application that calculates asset correlations, statistics and optimal portfolio allocations using data it retrieves from external services (currently: [AlphaVantage](https://www.alphavantage.co), [IEX](https://iexcloud.io/) and [Quandl](https://www.quandl.com/)). Statistics are calculated using [Ito Calculus](https://en.wikipedia.org/wiki/It%C3%B4_calculus) and should be consistent with the results demanded by [Modern Portfolio Theory](https://en.wikipedia.org/wiki/Modern_portfolio_theory) and [Financial Engineering](https://en.wikipedia.org/wiki/Black%E2%80%93Scholes_equation). The portfolios are optimized by minimizing the portfolio's variance/volatility, i.e. by finding the optimal spot on the portfolio's efficient frontier as defined by the [CAPM model](https://en.wikipedia.org/wiki/Capital_asset_pricing_model), or alternatively, by maximizing the portfolio's [Sharpe ratio](https://en.wikipedia.org/wiki/Sharpe_ratio).

The program's functions are wrapped in [PyQt5](https://doc.qt.io/qtforpython/index.html) widgets which provide a user interface (this feature is still in development and may explode). In addition, visualizations are created by [matplotlib](https://matplotlib.org/3.3.3/contents.html) for easier presentation.

# Setup

## Installation

Simply execute,

`pip install scrilla` 

## Dependencies

You will need Python3.8 or greater. This application depends on the following <b>Python</b> libraries: 

- [python-dotenv](https://pypi.org/project/python-dotenv/)>=0.17.0<br>
- [requests](https://pypi.org/project/requests/)>=2.25.0<br>
- [numpy](https://pypi.org/project/numpy/)>=1.19.3<br>
- [scipy](https://pypi.org/project/scipy/)>=1.5.4<br>
- [matplotlib](https://pypi.org/project/matplotlib/)>=3.3.3<br>
- [holidays](https://pypi.org/project/holidays/)>=0.10.4<br>
- [PyQt5](https://pypi.org/project/PyQt5/)>=5.14<br>

This libraries will be installed during the `pip` command. If you wish to use the GUI, you will need to install [Qt](https://doc.qt.io/) separately,

`sudo apt-get install qt5-default`

The GUI will not function without a <b>Qt</b> library.

# Environment

A sample environment file is located [here](https://github.com/chinchalinchin/scrilla/blob/development/env/.sample.env), along with some comments regarding their purpose. The application sets defaults for more of these, but there are several required environment variables you will need to set up yourself. 

## Required Configuration

In order to use this application, you will need to register for API keys at <b>AlphaVantage</b>, <b>IEX</b> and <b>Quandl</b>. Store these in your session's environment. <b>scrilla</b> will search for environment variables named <b>ALPHA_VANTAGE_KEY</b>, <b>QUANDL_KEY</b> and <b>IEX_KEY</b>. You can add the following lines to your <i>.bashrc</i> profile,

`export ALPHA_VANTAGE_KEY=<key goes here>`<br>
`export QUANDL_KEY=<key goes here>`<br>
`export IEX_KEY=<key goes here>`<br>

If no API keys are found in these variables, the application will not function properly; be sure to load these variables into your shell session before using <b>scrilla</b>. The link below will take you to the registration pages for each service API Key,

[AlphaVantage API Key Registration](https://www.alphavantage.co/support/#api-key)<br>
[Quandl API Key Registration](https://www.quandl.com/account/api)<br>
[IEX API Key Registration](https://iexcloud.io/)<br>

## Optional Configuration 

<b>scrilla</b> can be configured with the following environment variables. Each variable in this list has a suitable default set and so does not need changed unless the user prefers a different setting.

- RISK_FREE

Determines which US-Treasury yield is used as the basis for the risk free rate. This variable will default to a value of `10-Year`, but can be modified to any of the following: `"3-Month"`, `"5-Year"`, `"10-Year"`, or `"30-Year"`.

- MARKET_PROXY

Determines which ticker symbol is used as a proxy for the market return. This variable will default to a value of `SPY`, but can be set to any ticker on the stock market.

- FRONTIER_STEPS

Determines the number of data points in a portfolio's efficient frontier. This variable will default to a value of `5`, but can be set equal to any integer.


- MA_1, MA_2, MA_3

Determines the period in days used to calculuate moving average series. These variables default to the values of `20`, `60` and `100`, but can be set equal to any integer, as long as <b>MA_3</b> > <b>MA_2</b> > <b>MA_1</b>.

- FILE_EXT 

Determines the type of files that are output by <b>scrilla</b>. This variable is ccurrently only defined for an argument of `json`. A future release will include `csv`. 

- LOG_LEVEL

Determines the amount of output. Defaults to `info`. Allowable values: `info`, `debug`, `verbose`. Be warned, `verbose` is <i>extremely</i> verbose.

# Usage

## Command Line 

Most functions have been wired into command line arguments. For a full list of <b>scrilla</b>'s functionality,

`scrilla -help`

The main usage of <b>scrilla</b> is detailed below.

### Optimization

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
    <b>Arguments:</b><br>
    - `ticker : str` : Required. Ticker symbol of the equity.<br>
    - `start_date: datetime.date` : Optional. Start date of analysis range. Defaults to `None`<br> 
    - `end_date: datetime.date` : Optional. End date of analysis range. Defaults to `None`<br>
    
2. `scrilla.services.get_daily_stat_history(statistic, start_date=None, end_date=None)`<br>
    <b>Description:</b><br>
        This function will retrieve the price history for the financial statistic specifed by the `statistic` argument. 
    <b>Arguments:</b><br>
    - `statistic : str`: Required. Statistic symbol for quantity of interest. A list of allowable values can be found [here](https://www.quandl.com/data/FRED-Federal-Reserve-Economic-Data/documentation)<br>
    - `start_date: datetime.date` : Optional. Start date of analysis range. Defaults to `None`<br> 
    - `end_date: datetime.date` : Optional. End date of analysis range. Defaults to `None`<br>

3. `scrilla.services.get_dividend_history(ticker)`<br>
    <b>Description:</b><br>
        This function will retrieve the dividend payment history (i.e. the date on which the payment was <i>made</i>, not the date the payment was declared) for the equity specified by the `ticker` arugment. `ticker` must be the symobl assoccaited with the equity on the stock exchange.
    <b>Arguments:</b><br>
    - `ticker : str` : Required. Ticker symbol of the equity.<br>

4. `scrilla.services.get_risk_free_rate()`
    <b>Description: </b><b>
        This function will retrieve the current value of the risk free rate (yield on a Treasury). The risk free rate can be configured through the <b>RISK_FREE</b> environment variable. See [optional configuration](#optional-configuration) for more details.

### scrilla.analysis.markets

1. `scrilla.analysis.markets.sharpe_ratio`

2. `scrilla.analysis.markets.market_premium`

3. `scrilla.analysis.markets.market_beta`

4. `scrilla.analysis.markets.cost_of_equity`

### scrilla.analysis.optimizer

1. `scrilla.analysis.optimizer.optimize_portfolio_variance`

2. `scrilla.analysis.optimizer.maximize_sharpe_ratio`

3. `scrilla.analysis.optimizer.maximize_portfolio_return`
    <b>Description:</b><br>
    <b>Note:</b><br>
    The rate of return of a portfolio of assets is a linear function with respect to the asset weights. IAs a result, this function should always allocate 100% of any given portfolio to the asset with the highest expected rate of return, i.e. if you have two assets where one asset has a 10% rate of return and a second asset has a 20% rate of return, the maximum rate of return for a portfolio composed of both assets is produced when 100% of the portfolio is invested in the asset with a 20% rate of return.<br>

### scrilla.analysis.statistics

1. `scrilla.analysis.statistics.sample_correlation`

2. `scrilla.analysis.statistics.recursive_rolling_correlation`

3. `scrilla.analysis.statistics.sample_mean`

4. `scrilla.anaylsis.statistics.recursive_rolling_mean`

5. `scrilla.anaylsis.statistics.sample_variance`

6. `scrilla.analysis.statistics.recursive_rolling_variance`

7. `scrilla.anaylsis.statistics.sample_covariance`

8. `scrilla.anaylsis.statistics.recursive_rolling_covariance`

9. `scrilla.analysis.statistics.regression_beta`

10. `scrilla.analysis.statistics.regression_alpha`

11. `scrilla.analysis.statistics.calculate_moving_averages`

12. `scrilla.analysis.statistics.calculate_risk_return`

13. `scrilla.analysis.statistics.calculate_return_covariance`

14. `scrilla.analysis.statistics.calculate_ito_correlation`

15. `scrilla.anaylsis.statistics.ito_correlation_matrix`

### scrilla.objects.cashflow.Cashflow

### scrilla.objects.portfolio.Portfolio