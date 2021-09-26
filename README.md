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

See [module documentation](https://chinchalinchin.github.io/scrilla/) for more information.

# Setup

## Installation

Install the package with the <b>Python</b> package manager,

`pip install scrilla` 

This will install a command line interface on your path under the name `scrilla`. Confirm your installation with with the `-version` flag,

`scrilla -version`

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

- ANALYSIS_MODE

The asset price model assumed during the estimation of statistics. A value of`geometric` corresponds geometric brownian motion model where the return is proportional to the asset price. The constant of proportionality is a random variable with a constant mean and volatility. A value of `reversion` refers to a mean reverting model where the return is proportional to the difference between the asset price and a stationary mean. The unit of proportionality is a random variable with constant mean and volatility.

Note, it is highly recommended that if you change this value, you should clear the cache, as the cache stores frequent statistical calculations to speed up the program. The previous values of the statistics calculated under the prior model will be referenced and result in incorrect calculations.

- DEFAULT_ESTIMATION_METHOD

Determines the method used to calculate risk-return profiles. If set to `moments`, the return and volatility will be estimated by setting them equal to the first and second sample moments. If set to `percents`, the return and volatilty will be estimated by setting the 25th percentile and 75th percentile of the assumed distribution (see above <b>ANALYSIS_MODE</b>) equal to the 25th and 75th percentile from the sample of data. If set to `likely`, the likelihood function calculated from the assumed distribution (see <b>ANALYSIS_MODE</b> again) will be maximized with respect to the return and volatility; the values which maximize will be used as the estimates. 

- RISK_FREE

Determines which annualized US-Treasury yield is used as stand-in for the risk free rate. This variable will default to a value of `ONE_YEAR`, but can be modified to any of the following: `ONE_MONTH`, `THREE_MONTH`, `SIX_MONTH`, `ONE_YEAR`, `THREE_YEAR`, `FIVE_YEAR`, `TEN_YEAR`, `THIRTY_YEAR`.

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

The two new arguments are `prob` and `expiry`. `prob`, in essence, represents the percentile of the portfolio's distribution on which the value at risk will be conditioned. In other words, if the portfolio value is represented by a random variable **P**, for a given value of **P**=*p*, the `prob` is the probability such that, 

`Probability(P<p)=prob`

`expiry` represents the time horizon over which the value at risk will be calculated, i.e. the point in time in which the hypothetical loss occurs. 

With these two new arguments, a portfolio's conditional value at risk can be optimized using the following,

`scrilla -opt-cvar -prob 0.05 -expiry 0.5 ALLY BX SONY`

The command given above will optimize the portfolio's value at risk consisting of <b>ALLY</b>, <b>BX</b> and <b>SONY</b> over the next half year (`expiry` = 0.5) conditioned the value at risk being in the 5th percentile. 

### Other Notable Features

1. Distribution Modes

<b>scrilla</b> will assume an asset price process and therefore a probability distribution for the population of asset returns. The model <b>scrilla</b> assumes is determined by the environment variable <b>ANALYSIS_MODE</b>. Currently, only one model is available: `geometric`, which corresponds to an assume price process that follows (Geometric Brownian Motion)[https://en.wikipedia.org/wiki/Geometric_Brownian_motion] and thus a probability distribution for the asset returns that is log-normal. 

In the near future, a mean reversion model will implemented.

2. Estimation Modes

<b>scrilla</b> can estimate model parameters in a number of ways. The default estimation method is defined by the environment variable <b>DEFAULT_ESTIMATION_METHOD</b>, but all statistical functions can have their estimation overridden with a flag. <b>scrilla</b> supports three estimation modes: `moments`, `percents` and `likely`. 

`moments` will use the [method of moment matching](https://en.wikipedia.org/wiki/Method_of_moments_(statistics)), where the moments of a sample of data are equated to the moments of the assumed distribution in order to determine the distribution parameters. `percents` will use the method of percentile matching, where the first and third quartile of the sample are equated to the theoretical distribution percentiles to determine the distribution parameters. `likely` will use [maximum likelihood estimation](https://en.wikipedia.org/wiki/Maximum_likelihood_estimation), where the probability of each observation given the assumed distribution is calculated and then the intersection of the probabilities is minimized with respect to the distribution parameters. (Note: the underlying distribution can be configured through the <b>ANALYSIS_MODE</b> environment variable; see [Environment](#environment) for more information)

For example, the following command will return the risk profile of <b>ACI</b> using the method of moment matching,

`scrilla -profile -moments ACI`

Where as the following command will return the risk profile of <b>ACI</b> using maximum likelihood estimation,

`scrilla -profile -likely ACI`

And the following command will return the risk profile of <b>ACI</b> using the method of percentile matching,

`scrilla -profile -percents ACI`

Note, the following command,

`scrilla -profile ACI`

will return the risk profile of <b>ACI</b> using the method set in the <b>DEFAULT_ESTIMATION_METHOD</b> environment variable. If this variable is not set, it will default to a value of `moments`.

2. Discount Dividend Model

<b>scrilla</b> will pull an equity's dividend payment history, regress the payment amount against its date and infer a [simple linear regression model](https://en.wikipedia.org/wiki/Simple_linear_regression) from this time series. It will use this model to project future dividend payments and then calculate the current cost of equity and use that to discount the sum of dividend payments back to the present. The following command will perform this action,

`scrilla -ddm ALLY`

Alternatively, you can visualize the dividend payments against the regression model with a <b>matplotlib</b> graphic,

`scrilla -plot-div ALLY`

3. Financial Statistics
    - Beta: `scrilla -capm-beta [TICKERS]`
    - Correlation Matrix: `scrilla -cor [TICKERS]`
    - Conditional Value At Risk `scrilla -cvar -prob PROB -expiry EXP [TICKERS]`
    - Cost Of Equity: `scrilla -capm-equity [TICKERS]`
    - Risk-Return Profile: `scrilla -profile [TICKERS]`
    - Sharpe Ratio: `scrilla -sharpe [TICKERS]`
    - Value At Risk: `scrilla -var -prob PROB -expiry EXP [TICKERS]`

4. Stock Watchlist and Screening

Stocks can be added to your watchlist with,

`scrilla -watch [TICKERS]`

You can then screen stocks according to some criteria. For example, the following command will search your watchlist for stock prices that are less than their Discount Dividend Model (very rare this happens...),

`scrilla -screen -model DDM`

5. Visualizations
    - Discount Dividend Model: `scrilla -plot-div [TICKER]`
        - NOTE: THIS FUNCTION ONLY ACCEPTS ONE TICKER AT A TIME.
    - Efficient Fronter: `scrilla -plot-ef [TICKERS]`
    - Moving Averages: `scrilla -plot-mov [TICKERS]`
    - Risk Return Profile: `scrilla -plot-rr [TICKERS]`
    - Yield Curve: `scrilla -plot-yield` (not implemented yet)

# Notes

1. The following symbols have both equity and crypto assets trading on exchanges:

['ABT', 'AC', 'ADT', 'ADX', 'AE', 'AGI', 'AI', 'AIR', 'AMP', 'AVT', 'BCC', 'BCD', 'BCH', 'BCX', 'BDL', 'BFT', 'BIS', 'BLK', 'BQ', 'BRX', 'BTA', 'BTG', 'CAT', 'CMP', 'CMT', 'CNX', 'CTR', 'CURE', 'DAR', 'DASH', 'DBC', 'DCT', 'DDF', 'DFS', 'DTB', 'DYN', 'EBTC', 'ECC', 'EFL', 'ELA', 'ELF','EMB', 'ENG', 'ENJ', 'EOS', 'EOT', 'EQT', 'ERC', 'ETH', 'ETN', 'EVX', 'EXP', 'FCT', 'FLO', 'FLT', 'FTC', 'FUN', 'GAM', 'GBX', 'GEO', 'GLD', 'GNT', 'GRC', 'GTO', 'INF', 'INS', 'INT', 'IXC', 'KIN', 'LBC', 'LEND', 'LTC', 'MAX', 'MCO', 'MEC', 'MED', 'MGC', 'MINT', 'MLN', 'MNE', 'MOD', 'MSP', 'MTH', 'MTN', 'MUE', 'NAV', 'NEO', 'NEOS', 'NET', 'NMR', 'NOBL', 'NXC', 'OCN', 'OPT', 'PBT', 'PING', 'PPC', 'PPT', 'PRG', 'PRO', 'PST', 'PTC', 'QLC', 'QTUM','R', 'RDN', 'REC', 'RVT', 'SALT', 'SAN', 'SC', 'SKY', 'SLS', 'SPR', 'SNX', 'STK', 'STX', 'SUB', 'SWT', 'THC', 'TKR', 'TRC', 'TRST', 'TRUE', 'TRX', 'TX', 'UNB', 'VERI', 'VIVO', 'VOX', 'VPN', 'VRM', 'VRS', 'VSL', 'VTC', 'VTR', 'WDC', 'WGO', 'WTT', 'XEL', 'NEM', 'ZEN']

Since there is no way good way to distinguish whether or not the asset is an equity or a cryptocurrency based on the value of the ticker alone, the module functions `scrilla.files.get_asset_type` and `scrilla.errors.validate_asset_type` will always default to the equity ticker for the above symbols. 

This is not the greatest solution, as all the crypto symbols given above are inaccessible to analysis. In particular, `ETH` represents a popular crypto that cannot be analyzed, which represents a major failing of the current application.

The way the `service` module works, `PriceManager` can be forced to retrieve the crypto asset's prices instead of the equity asset's through the `services.PriceManager.get_prices` method by providing the method an argument of `asset_type='crypto'`; However, the `service` module function `services.get_daily_price_history`, which is the point of contact between the `PriceManager` and the rest of the application, wraps calls to the `PriceManager.get_prices` method in a cache persistence layer (meaning, `get_daily_price_history` checks if prices exist in the cache before passing the request off to an external service query). The cache doesn't distinguish asset types currently. The `PriceCache` stores prices based on the inputs (<i>ticker, date, open close, close price</i>). So, even if the `PriceManager` is forced to get crypto prices on the first call, subsequent calls to the same `get_daily_price_history` function will likely break the application, or at least lead to misleading results, since the cache will contain a set of prices that doesn't necessarily map one-to-one with its ticker symbol.

If the above problem is to be solved, the cache needs modified to separate prices based on asset type.

2. There is a slight discrepancy between the results of maximum likelihood estimation and moment matching when the underyling distribution of the price process is log-normal. The likelihood algorithm in this library relies on the generalized idea of likelihood estimation; it will compute the log-likelihood function for a given vector of parameters and then optimize that function by varying the vector until the input that produces the maximum output; the usual matter of course is to derive a formula using calculus that can then be analytically solved. Both operations should be equivalent. Moreover, theoretically, it can be shown the maximization operation should be equivalent to the results obtained by the moment matching operation, i.e the maximum likelihood estimator for the mean is the sample mean, etc. However, the results between maximum likelihood estimation and moment matching are off by a few decimal points. It may be due to some vagary of floating point arithmetic, but something else may be going on. See comments in `scrilla.analysis.models.geometric.statistics'


# Documentation
- [dateutil](https://dateutil.readthedocs.io/en/stable/index.html)
- [holidays](https://github.com/dr-prodigy/python-holidays)
- [matplotlib](https://matplotlib.org/)
- [numpy](https://numpy.org/doc/)
- [pyqt](https://doc.qt.io/qtforpython/)
- [requests](https://docs.python-requests.org/en/latest/)
- [scipy](https://www.scipy.org/docs.html)
- [sqlite3](https://docs.python.org/3/library/sqlite3.html)