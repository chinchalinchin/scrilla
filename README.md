# Pynance: A Financial Optimization Application

This is a financial application that calculates asset correlations, statistics and optimal portfolio allocations using data it retrieves from external services (currently: [AlphaVantage](https://www.alphavantage.co), [IEX](https://iexcloud.io/) and [Quandl](https://www.quandl.com/)). Statistics are calculated using [Ito Calculus](https://en.wikipedia.org/wiki/It%C3%B4_calculus) and should be consistent with the results demanded by [Modern Portfolio Theory](https://en.wikipedia.org/wiki/Modern_portfolio_theory) and [Financial Engineering](https://en.wikipedia.org/wiki/Black%E2%80%93Scholes_equation). The portfolios are optimized by minimizing the portfolio's variance/volatility, i.e. by finding the optimal spot on the portfolio's efficient frontier as defined by the [CAPM model](https://en.wikipedia.org/wiki/Capital_asset_pricing_model), or alternatively, by maximizing the portfolio's [Sharpe ratio](https://en.wikipedia.org/wiki/Sharpe_ratio).

The program's functions are wrapped in [PyQt5](https://doc.qt.io/qtforpython/index.html) widgets which provide a user interface. In addition, visualizations are created by [matplotlib](https://matplotlib.org/3.3.3/contents.html) for easier presentation.

## Required Configuration

In order to use this application, you will need to register for API keys at AlphaVantage, IEX and Quandl. Store these in your session's environment. <b>pynance</b> will search for environment variables named <b>ALPHA_VANTAGE_KEY</b>, <b>QUANDL_KEY</b> and <b>IEX_KEY</b>. If no API keys are found in these variables, the application will not function properly; be sure to load these variables into your shell session before using <b>pynance</b>. 

## Optional Configuration 

<b>Pynance</b> can be configured with the following environment variables. Each variable in this list has a suitable default set and so does not need changed unless the user prefers a different setting.

1. <b>RISK_FREE</b>: Determines which US-Treasury yield is used as the basis for the risk free rate. 

This variable will default to a value of `10-Year`, but can be modified to any of the following: `"3-Month"`, `"5-Year"`, `"10-Year"`, or `"30-Year"`.

2. <b>MARKET_PROXY</b>: Determines which ticker symbol is used as a proxy for the market return.

This variable will default to a value of `SPY`, but can be set to any ticker on the stock market.

3. <b>FRONTIER_STEPS</b>: Determines the number of data points in a portfolio's efficient frontier.

This variable will default to a value of `5`, but can be set equal to any integer.

4. <b>MA_1</b>, <b>MA_2</b>, <b>MA_3</b>: Determines the period in days used to calculuate moving average series.

These variables default to the values of `20`, `60` and `100`, but can be set equal to any integer, as long as <b>MA_3</b> > <b>MA_2</b> > <b>MA_1</b>.

5. <b>FILE_EXT</b>: Determines the type of files that are output by <b>pynance</b>. 

This variable is ccurrently only defined for an argument of `json`. A future release will include `csv`. 