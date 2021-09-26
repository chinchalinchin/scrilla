"""
.. Static Code Analysis::

    * [![DeepSource](https://deepsource.io/gh/chinchalinchin/scrilla.svg/?label=active+issues&show_trend=true&token=tD25pyXAL4uIvrccqjlwzXIU)](https://deepsource.io/gh/chinchalinchin/scrilla/?ref=repository-badge)
    * [![DeepSource](https://deepsource.io/gh/chinchalinchin/scrilla.svg/?label=resolved+issues&show_trend=true&token=tD25pyXAL4uIvrccqjlwzXIU)](https://deepsource.io/gh/chinchalinchin/scrilla/?ref=repository-badge)

.. Author:: Grant Moore
.. Contact:: chinchalinchin@gmail.com

This is a financial application that calculates asset correlations, statistics and produces various graphical summaries of data. It was originally designed to optimize portfolio allocations using data it retrieves from external services (currently: [AlphaVantage](https://www.alphavantage.co), [IEX](https://iexcloud.io/) and [Quandl](https://www.quandl.com/)). Its scope has since expanded as way for the author to test the limits of his knowledge, as it were. 

Statistics are calculated using the results of [Ito Calculus](https://en.wikipedia.org/wiki/It%C3%B4_calculus) and should be consistent with the results of [Modern Portfolio Theory](https://en.wikipedia.org/wiki/Modern_portfolio_theory) and [Financial Engineering](https://en.wikipedia.org/wiki/Black%E2%80%93Scholes_equation). 

*scrilla* can estimate financial statistics in a variety of ways; it can be configured to estimate using the [method of moment matching](https://en.wikipedia.org/wiki/Method_of_moments_(statistics)), [method of percentile matching](https://openacttexts.github.io/Loss-Data-Analytics/C-ModelSelection.html)(section 4.1.3.2) or [maximum likelihood estimation](https://en.wikipedia.org/wiki/Maximum_likelihood_estimation). The estimation method can be stored in an environment variable to configure a default, or explicitly passed into statistical functions. See the specific functions of interest for more information.

In terms of its original purpose, portfolios are optimized by minimizing the portfolio's variance/volatility, i.e. by finding the optimal spot on the portfolio's efficient frontier as defined by the [CAPM model](https://en.wikipedia.org/wiki/Capital_asset_pricing_model). Alternatively, portfolios can be optimized by maximizing the portfolio's [Sharpe ratio](https://en.wikipedia.org/wiki/Sharpe_ratio) or by minimizing the portfolio's [Conditional Value at Risk](https://en.wikipedia.org/wiki/Expected_shortfall#Optimization_of_expected_shortfall).

Note this application optimizes across asset classes, i.e. the theoretical portfolio being constructed can be composed of equities, cryptocurrencies or both. In a future release, I would like to include fixed income assets, volatility assets (<i>VIX</i> futures, options, etc.) and other derivatives, but for now, only those two asset types are supported. I am looking for a good API that provides historical data on the other types of financial instruments before I bring them into the optimization algorithm, so if you know of one, contact me. 

The program's functions are wrapped in [PyQt5](https://doc.qt.io/qtforpython/index.html) widgets which provide a user interface (this feature is still in development and may explode). In addition, visualizations are created by [matplotlib](https://matplotlib.org/3.3.3/contents.html).

.. notes::
    * The idea behind the structure of the modules in this library is as follows: each sub-module should only depend on the sub-modules above it in the hierarchy of modules. At the top level, the modules are: `cache`, `errors`, `files`, `graphics`, `services`, `settings` and `static`. All of this modules are relatively independent (except the `settings` module which configures aspects of all the other modules, but it is made up entirely of values parsed from the environment and shouldn't introduce any circular dependencies), and expose mutually exclusive functionality. As you drill down in the sub-modules, the functions therein contain dependencies on the modules above them; for instance, the `analysis.markets` has dependencies on `services`, but `services` does not have dependencies on `analysis.markets`. There are instances where this design principle has been violated out of necessity, but by and large, this is the motivating idea behind this project's organization. For instance, `scrilla.main` imports the entire application module hierarchy into its namespace, since it acts as the entrypoint for the CLI and has to have access to everything to delegate user input; no other module in the program imports `scrilla.main`; there are other examples where the design principle enumerated above is not strictly followed, but it always the exception, not the rule.
    * The links below will take you to the registration pages for each API service Key,
        - [AlphaVantage API Key Registration](https://www.alphavantage.co/support/#api-key)
        - [Quandl API Key Registration](https://www.quandl.com/account/api)
        - [IEX API Key Registration](https://iexcloud.io/)


"""