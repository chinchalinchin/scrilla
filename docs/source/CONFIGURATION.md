# Configuration

## API Key Links

[AlphaVantage API Key Registration](https://www.alphavantage.co/support/#api-key)<br>
[Quandl API Key Registration](https://www.quandl.com/account/api)<br>
[IEX API Key Registration](https://iexcloud.io/)<br>

In order to use this application, you will need to register for API keys for each of the above services. The program will need to be made aware of these keys somehow. The best option is storing these credentials in environment variables.
# Environment

**scrilla** scans the environment in its *settings.py* file for shell variables. Various properties of the application can be configured through these environment variables. A sample environment file is located [here](https://github.com/chinchalinchin/scrilla/blob/develop/main/env/.sample.env), along with comments describing the purpose of each variable. The application sets sensible defaults for most of these environment variables, but there are several required environment variables you will need to set yourself. 

## Required Configuration

*NOTE*: If no API keys are found through either of the following methods, the application will not function properly.

### Environment Variables
You will need to register for API keys at **AlphaVantage**, **IEX** and **Quandl** in order to retrieve financial data. One way of passing API keys to the program is by storing these in your session's environment. **scrilla** will search for environment variables named **ALPHA_VANTAGE_KEY**, **QUANDL_KEY** and **IEX_KEY**. You can add the following lines to your *.bashrc* profile or corresponding configuration file for whatever shell you are using, or simply execute these lines before invoking **scrilla**

```shell
export ALPHA_VANTAGE_KEY=<key goes here>
export QUANDL_KEY=<key goes here>
export IEX_KEY=<key goes here>
```

The next invocation of *scrilla* will detect these variables and automatically append the credentials to services calls. 

### Local Storage

You can also invoke the CLI function `store` to store the credentials in the local installation's <i>/data/common/</i> directory. To do so,

```shell
scrilla store -key <key> -value <value>
```

where `<key>` is one of the values: **ALPHA_VANTAGE_KEY**, **QUANDL_KEY** or **IEX_KEY**. `<value>` is the corresponding key itself given to you after registration. `<value>` is case-sensitive! Keep in mind if using this method to store the API keys, the keys will be stored unencrypted in the local */data/common/* directory. 

## Optional Configuration 

*scrilla* can be configured with the following optional environment variables. Each variable in this list has a suitable default set and so does not need changed unless the user prefers a different setting. Set these values in your shell profile or export them directly from your current session, i.e.

```shell
export RISK_FREE=ONE_YEAR
scrilla risk-free # returns one year risk free rate
export RISK_FREE=THREE_YEAR
scrilla risk-free # returns three year risk free rate
```

- ANALYSIS_MODE

The asset price model assumed during the estimation of statistics. A value of`geometric` corresponds geometric brownian motion model where the return is proportional to the asset price. The constant of proportionality is a random variable with a constant mean and volatility. A value of `reversion` refers to a mean reverting model where the return is proportional to the difference between the asset price and a stationary mean. The unit of proportionality is a random variable with constant mean and volatility.

Note, it is highly recommended that if you change this value, you should clear the cache, as the cache stores frequent statistical calculations to speed up the program. The previous values of the statistics calculated under the prior model will be referenced and result in incorrect calculations.

- DEFAULT_ESTIMATION_METHOD

Determines the method used to calculate risk-return profiles. If set to `moments`, the return and volatility will be estimated by setting them equal to the first and second sample moments. If set to `percents`, the return and volatilty will be estimated by setting the 25th percentile and 75th percentile of the assumed distribution (see above **ANALYSIS_MODE**) equal to the 25th and 75th percentile from the sample of data. If set to `likely`, the likelihood function calculated from the assumed distribution (see **ANALYSIS_MODE** again) will be maximized with respect to the return and volatility; the values which maximize will be used as the estimates. 

- RISK_FREE

Determines which annualized US-Treasury yield is used as stand-in for the risk free rate. This variable will default to a value of `ONE_YEAR`, but can be modified to any of the following: `ONE_MONTH`, `THREE_MONTH`, `SIX_MONTH`, `ONE_YEAR`, `THREE_YEAR`, `FIVE_YEAR`, `TEN_YEAR`, `THIRTY_YEAR`.

- MARKET_PROXY

Determines which ticker symbol is used as a proxy for the overall market return. This variable will default to a value of `SPY`, but can be set to any ticker on the stock market. Recommended values: `SPY`, `QQQ`, `DJI` or `VTI`.

- FRONTIER_STEPS

Determines the number of data points in a portfolio's efficient frontier. This variable will default to a value of `5`, but can be set equal to any integer.

- MA_1, MA_2, MA_3

Determines the number of days used in the sample for moving average series and plots. These variables default to the values of `20`, `60` and `100`. In other words, by default, moving average plots will display the 20-day moving average, the 60-day moving average and the 100-day moving average. These variables can be set equal to any integer, as long as **MA_1**, **MA_2**, **MA_3**. 

- FILE_EXT 

Determines the type of files that are output by **scrilla**. This variable is currently only defined for an argument of `json`. A future release will include `csv`. 

- LOG_LEVEL

Determines the amount of output. Defaults to `info`. Allowable values: `none`, `info`, `debug` or `verbose`. Be warned, `verbose` is *extremely* verbose.