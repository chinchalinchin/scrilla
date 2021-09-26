"""
scrilla
-------

This is a financial application that calculates asset correlations, statistics and optimal portfolio allocations using data it retrieves from external services (currently: [AlphaVantage](https://www.alphavantage.co), [IEX](https://iexcloud.io/) and [Quandl](https://www.quandl.com/)). Statistics are calculated using [Ito Calculus](https://en.wikipedia.org/wiki/It%C3%B4_calculus) and should be consistent with the results demanded by [Modern Portfolio Theory](https://en.wikipedia.org/wiki/Modern_portfolio_theory) and [Financial Engineering](https://en.wikipedia.org/wiki/Black%E2%80%93Scholes_equation). The portfolios are optimized by minimizing the portfolio's variance/volatility, i.e. by finding the optimal spot on the portfolio's efficient frontier as defined by the [CAPM model](https://en.wikipedia.org/wiki/Capital_asset_pricing_model). Alternatively, portfolios can be optimized by maximizing the portfolio's [Sharpe ratio](https://en.wikipedia.org/wiki/Sharpe_ratio) or by minimizing the portfolio's [Conditional Value at Risk](https://en.wikipedia.org/wiki/Expected_shortfall#Optimization_of_expected_shortfall).

The program's functions are wrapped in [PyQt5](https://doc.qt.io/qtforpython/index.html) widgets which provide a user interface (this feature is still in development and may explode). In addition, visualizations are created by [matplotlib](https://matplotlib.org/3.3.3/contents.html) for easier presentation.

The links below will take you to the registration pages for each API service Key,

[AlphaVantage API Key Registration](https://www.alphavantage.co/support/#api-key)<br>
[Quandl API Key Registration](https://www.quandl.com/account/api)<br>
[IEX API Key Registration](https://iexcloud.io/)<br>

Note this application optimizes across asset classes, i.e. the theoretical portfolio being constructed can be composed of equities, cryptocurrencies or both. In a future release, I would like to include fixed income assets, volatility assets (<i>VIX</i> futures, options, etc.) and other derivatives, but for now, only those two asset types are supported. I am looking for a good API that provides historical data on the other types of financial instruments before I bring them into the optimization algorithm, so if you know of one, contact me. 
"""