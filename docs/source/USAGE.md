# Usage

## Command Line

Most functions have been wired into command line arguments. For a full list of <b>scrilla</b>'s functionality,

```shell
scrilla help
```

The main usage of <b>scrilla</b> is detailed below.

## Syntax

```shell 
scrilla [COMMAND] [TICKERS] [OPTIONS]
```

**Commands**: asset,cvar,var,capm-equity,capm-beta,clear-cache,clear-static,clear-common,close,correlation,correlations,discount-dividend-model,dividends,efficient-frontier,help,interest,watchlist,max-return,mov-averages,optimize-portfolio,optimize-cvar,plot-correlations,plot-dividends,plot-efficient-frontier,plot-moving-averages,plot-returns,plot-risk-profile,plot-yield-curve,prices,purge,risk-free,risk-profile,screen,sharpe-ratio,stat,stats,store,version,watch,yield-curve

**Tickers**: space-separated list of asset tickers/statistic symbols/interest maturities (depending on the command)

**Options**: command-specific flags and configuration.

### Portfolio Optimization

1. Volatility Minimization & Sharpe-Ratio Maximization

A portfolio of consisting of the equities <i>ALLY</i>, <i>BX</i> and <i>SONY</i> can be optimized with the following command,

```shell
scrilla optimize-portfolio ALLY BX SONY
```

By default, <b>scrilla</b> will optimize over the last 100 trading days. If you wish to optimize over a different time period, you may use the `-start` and `-end` argument flags to provide starting and ending dates in the `YYYY-MM-DD` format. 

Also by default, the optimization function will minimize the portfolio variance. You can also specify the portfolio should be maximized with respect to the Sharpe ratio,

```shell
scrilla optimize-portfolio ALLY BX SONY -sh
```

There are several other arguments you may use to configure your optimization program. The full list of arguments is shown below,

```shell
scrilla optimize-portfolio [TICKERS] -sh \
                                     -start <YYYY-MM-DD> \
                                     -end <YYYY-MM-DD> \
                                     -save <absolute path to json file> \
                                     -target <float> \
                                     -invest <float>
```

`-target` will optimize the portfolio with the additional constraint that its rate of return must equal `target`. Note the target return must be between the minimum rate of return and maximum rate of return in a basket of equities. For example, if ALLY had a rate of return of 10%, BX 15%, SONY 20%, the frontier of possible rates of returns resides in the range [10%, 20%]. It is impossible to combine the equities in such a way to get a rate of return less than 10% or one greater than 20%. Note, this assumes shorting is not possible. A future release will relax this assumption and allow portfolio weights to be negative.

`-invest` represents the total amount of money invested in a portfolio. 

For example, the following command,

```shell
scrilla optimize-portfolio ALLY BX SONY -sh \
                                        -save <path-to-json-file> \
                                        -target 0.25 \
                                        -invest 10000 \
                                        -start 2020-01-03 \
                                        -end 2021-05-15
```

Will optimize a portfolio consisting of <i>ALLY</i>, <i>BX</i> and <i>SONY</i> using historical data between the dates of January 1st, 2020 and May 15th, 2021. The portfolio will be constrained to return a rate of 25%. A total $10,000 will be invested into this portfolio (to the nearest whole share). The output of this command will look like this,

> ---------------------------------------------- Results ----------------------------------------------<br>
> ----------------------------------- Optimal Percentage Allocation -----------------------------------<br>
>           ALLY = 22.83 %<br>
>           BX = 19.26 %<br>
>           SONY = 57.91 %<br>
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

The two new arguments are `prob` and `expiry`. `prob`, in essence, represents the percentile of the portfolio's distribution on which the value at risk will be conditioned. In other words, if the portfolio value is represented by a random variable **P**, for a given value of **P**=*p*, the `prob` is the probability such that `Probability(P<p)=prob`.

`expiry` represents the time horizon over which the value at risk will be calculated, i.e. the point in time in which the hypothetical loss occurs. 

With these two new arguments, a portfolio's conditional value at risk can be optimized using the following,

```
scrilla optimize-cvar ALLY BX SONY -prob 0.05 -expiry 0.5
```

The command given above will optimize the portfolio's value at risk consisting of <b>ALLY</b>, <b>BX</b> and <b>SONY</b> over the next half year (`expiry` = 0.5) conditioned the value at risk being in the 5th percentile. 

### Other Notable Features

1. Distribution Modes

<b>scrilla</b> will assume an asset price process and therefore a probability distribution for the population of asset returns. The model <b>scrilla</b> assumes is determined by the environment variable <b>ANALYSIS_MODE</b>. Currently, only one model is available: `geometric`, which corresponds to an assume price process that follows [geometric brownian motion](https://en.wikipedia.org/wiki/Geometric_Brownian_motion) and thus a probability distribution for the asset returns that is log-normal. 

In the near future, a mean reversion model will implemented.

2. Estimation Modes

<b>scrilla</b> can estimate model parameters in a number of ways. The default estimation method is defined by the environment variable <b>DEFAULT_ESTIMATION_METHOD</b>, but all statistical functions can have their estimation overridden with a flag. <b>scrilla</b> supports three estimation modes: `moments`, `percents` and `likely`. 

`moments` will use the [method of moment matching](https://en.wikipedia.org/wiki/Method_of_moments_(statistics)), where the moments of a sample of data are equated to the moments of the assumed distribution in order to determine the distribution parameters. `percents` will use the method of percentile matching, where the first and third quartile of the sample are equated to the theoretical distribution percentiles to determine the distribution parameters. `likely` will use [maximum likelihood estimation](https://en.wikipedia.org/wiki/Maximum_likelihood_estimation), where the probability of each observation given the assumed distribution is calculated and then the intersection of the probabilities is minimized with respect to the distribution parameters. (Note: the underlying distribution can be configured through the <b>ANALYSIS_MODE</b> environment variable; see [Environment](#environment) for more information)

For example, the following command will return the risk profile of <b>ACI</b> using the method of moment matching,

```shell
scrilla risk-profile ACI -moments
```

Where as the following command will return the risk profile of <b>ACI</b> using maximum likelihood estimation,

```shell
scrilla risk-profile ACI -likelihood
```

And the following command will return the risk profile of <b>ACI</b> using the method of percentile matching,

```shell
scrilla risk-profile ACI -percentiles
```

Note, the following command,

```shell
scrilla risk-profile ACI
```

will return the risk profile of <b>ACI</b> using the method set in the <b>DEFAULT_ESTIMATION_METHOD</b> environment variable. If this variable is not set, it will default to a value of `moments`.

2. Discount Dividend Model

<b>scrilla</b> will pull an equity's dividend payment history, regress the payment amount against its date and infer a [simple linear regression model](https://en.wikipedia.org/wiki/Simple_linear_regression) from this time series. It will use this model to project future dividend payments and then calculate the current cost of equity and use that to discount the sum of dividend payments back to the present. The following command will perform this action,

```shell
scrilla ddm ALLY
```

Alternatively, you can visualize the dividend payments against the regression model with a <b>matplotlib</b> graphic,

```shell
scrilla plot-divs ALLY
```

3. Financial Statistics
    - Beta: `scrilla capm-beta [TICKERS] [OPTIONS]`
    - Correlation Matrix: `scrilla cor [TICKERS] [OPTIONS]`
    - Conditional Value At Risk `scrilla cvar [TICKERS] -prob PROB -expiry EXP [OPTIONS]`
    - Cost Of Equity: `scrilla capm-equity [TICKERS] [OPTIONS]`
    - Risk-Return Profile: `scrilla risk-profile [TICKERS] [OPTIONS]`
    - Sharpe Ratio: `scrilla sharpe-ratio [TICKERS] [OPTIONS]`
    - Value At Risk: `scrilla var [TICKERS] -prob PROB -expiry EXP [OPTIONS]`

4. Stock Watchlist and Screening

Stocks can be added to your watchlist with,

```shell
scrilla watch [TICKERS]
```

You can then screen stocks according to some criteria. For example, the following command will search your watchlist for stock prices that are less than their Discount Dividend Model (very rare this happens...),

```shell
scrilla screen -criteria DDM
```

5. Visualizations
    - Discount Dividend Model: `scrilla plot-divs [TICKER] [OPTIONS]`
        - NOTE: THIS FUNCTION ONLY ACCEPTS ONE TICKER AT A TIME.
    - Efficient Fronter: `scrilla plot-ef [TICKERS] [OPTIONS]`
    - Moving Averages: `scrilla plot-mas [TICKERS] [OPTIONS]`
    - Risk Return Profile: `scrilla plot-rp [TICKERS] [OPTIONS]`
    - Yield Curve: `scrilla plot-yield`
    - QQ Plot of Returns: `scrilla plot-rets [TICKER] [OPTIONS]`
        - NOTE: THIS FUNCTION ONLY ACCEPTS ONE TICKER AT A TIME
    - Correlation Time Series `scrilla plot-cors [TICKERS] [OPTIONS]`
        - NOTE: THIS FUNCTION ACCEPTS EXACTLY TWO TICKERS

## Programmatic

You can import and use **scrilla**'s function in a Python script. You must ensure the API keys have been set. See [Configuration](/CONFIGURATION.md) for more information. If the keys have not been configured through environment variables or set through the CLI, you must set the keys through Python's ``os`` library before importing any functions or modules from **scrilla**,

```python
import os
os.environ.setdefault('ALPHA_VANTAGE_KEY', 'key')
os.environ.setdefault('QUANDL_KEY', 'key')
os.environ.setdefault('IEX_KEY', 'key')
```

Replace `key` with the appropriate API key. Append this to the top of the script before **scrilla**'s modules are imported. 

### Retrieve Price Data

```python
import os
os.environ.setdefault('ALPHA_VANTAGE_KEY', 'key')
os.environ.setdefault('QUANDL_KEY', 'key')
os.environ.setdefault('IEX_KEY', 'key')

from scrilla.services import get_daily_price_history
from scrilla.util import dater

start = dater.parse_date_string('2021-01-01')
end = dater.parse_date_string('2021-04-05')
prices = get_daily_price_history(ticker='ALLY', start_date=start, end_date=end)
```

### Risk Return

```python
import os
os.environ.setdefault('ALPHA_VANTAGE_KEY', 'key')
os.environ.setdefault('QUANDL_KEY', 'key')
os.environ.setdefault('IEX_KEY', 'key')

from scrilla.analysis.models.geometric.statistics import calculate_risk_return
from scrilla.util import dater

start = dater.parse_date_string('2021-01-01')
end = dater.parse_date_string('2021-04-05')
prices = calulate_risk_return(ticker='BTC', start_date=start, end_date=end)
```

### Portfolio Optimization


```python
import os
os.environ.setdefault('ALPHA_VANTAGE_KEY', 'key')
os.environ.setdefault('QUANDL_KEY', 'key')
os.environ.setdefault('IEX_KEY', 'key')

from scrilla.analysis.objects.portfolio import Portfolio
from scrilla.analysis.optimizer import optimize_portfolio_variance, maximize_sharpe_ratio
from scrilla.util import dater

start = dater.parse_date_string('2021-01-01')
end = dater.parse_date_string('2021-04-05')
port = Portfolio(tickers=['BTC','ALLY','SPY','GLD'], start_date=start, end_date=end)

# calculate minimum variance portfolio & its risk profile
min_vol_allocation = optimize_portfolio_variance(port)
min_vol_port_ret = port.return_function(min_vol_allocation)
min_vol_port_vol = port.volatility_function(min_vol_allocation)

# calculate maximum sharpe ratio portfolio & its risk profile
max_sh_allocation = maximize_sharpe_ratio(port)
max_sh_port_ret = port.return_function(max_sh_allocation)
max_sh_port_vol = port.volatility_function(max_sh_allocation)
```