# scrilla: Financial Optimization

![](https://github.com/chinchalinchin/chinchalinchin/blob/main/assets/scrilla_gui_ii.png)

*scrilla* is a financial application that calculates asset correlations, statistics and produces various graphical summaries of data. It was originally designed to optimize portfolio allocations using data it retrieves from external services (currently: [AlphaVantage](https://www.alphavantage.co), [IEX](https://iexcloud.io/) and [Quandl](https://www.quandl.com/)), but has since taken on a life of its own as a way for me to explore different areas of Python, development, finance and mathematics. 

Statistical calculations are informed using the results of [Ito Calculus](https://en.wikipedia.org/wiki/It%C3%B4_calculus). In other words, the sampling distributions for returns on assets are modeled through stochastic differential equations. The parameters of these models are estimated with statistical techniques. *scrilla* can estimate financial statistics in a variety of ways; it can be configured to estimate using the [method of moment matching](https://en.wikipedia.org/wiki/Method_of_moments_(statistics)), [method of percentile matching](https://openacttexts.github.io/Loss-Data-Analytics/C-ModelSelection.html)(section 4.1.3.2) or [maximum likelihood estimation](https://en.wikipedia.org/wiki/Maximum_likelihood_estimation). The estimation method can be stored in an environment variable to set a default for calculations, or explicitly passed into statistical functions. See the [documentation](https://chinchalinchin.github.io/scrilla/) for more information. 

In terms of its original purpose, portfolios are optimized, using the procedures of [Modern Portfolio Theory](https://en.wikipedia.org/wiki/Modern_portfolio_theory), by minimizing the portfolio's variance/volatility, i.e. by finding the optimal spot on the portfolio's efficient frontier as defined by the [CAPM model](https://en.wikipedia.org/wiki/Capital_asset_pricing_model). Alternatively, portfolios can be optimized by maximizing the portfolio's [Sharpe ratio](https://en.wikipedia.org/wiki/Sharpe_ratio) or by minimizing the portfolio's [Conditional Value at Risk](https://en.wikipedia.org/wiki/Expected_shortfall#Optimization_of_expected_shortfall).

This application optimizes across asset classes, i.e. the theoretical portfolio being constructed can be composed of equities, cryptocurrencies or both. In a future release, I would like to include fixed income assets, volatility assets (<i>VIX</i> futures, options, etc.) and other derivatives, but for now, only those two asset types are supported. I am looking for a good API that provides historical data on the other types of financial instruments before I bring them into the optimization algorithm, so if you know of one, contact me. 

The program's functions are wrapped in [PyQt5](https://doc.qt.io/qtforpython/index.html) widgets which provide a user interface (this feature is still in development and may explode). In addition, visualizations are created by [matplotlib](https://matplotlib.org/3.3.3/contents.html).

# Links

## Documentation
- [Package Documentation](/scrilla/package/index.html)

## Test Coverage
- [Unit Test Report](scrilla/coverage/index.html)

## Static Code Analysis
[![DeepSource](https://deepsource.io/gh/chinchalinchin/scrilla.svg/?label=active+issues&show_trend=true&token=tD25pyXAL4uIvrccqjlwzXIU)](https://deepsource.io/gh/chinchalinchin/scrilla/?ref=repository-badge)<br/>
[![DeepSource](https://deepsource.io/gh/chinchalinchin/scrilla.svg/?label=resolved+issues&show_trend=true&token=tD25pyXAL4uIvrccqjlwzXIU)](https://deepsource.io/gh/chinchalinchin/scrilla/?ref=repository-badge)<br/>

## Branch Pipelines
| Branch | Status |
| ------ | ------ |
| pypi/micro-update | [![CircleCI](https://circleci.com/gh/chinchalinchin/scrilla/tree/pypi%2Fmicro-update.svg?style=svg)](https://circleci.com/gh/chinchalinchin/scrilla/tree/pypi%2Fmicro-update) |
| pypi/micro-update | [![CircleCI](https://circleci.com/gh/chinchalinchin/scrilla/tree/pypi%2Fminor-update.svg?style=svg)](https://circleci.com/gh/chinchalinchin/scrilla/tree/pypi%2Fminor-update) |
| develop/main | [![CircleCI](https://circleci.com/gh/chinchalinchin/scrilla/tree/develop%2Fmain.svg?style=svg)](https://circleci.com/gh/chinchalinchin/scrilla/tree/develop%2Fmain)| 
