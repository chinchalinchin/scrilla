# Pynance: A Financial Optimization Application

This is a financial application that calculates asset correlations, statistics and optimal portfolio allocations using data it retrieves from external services (currently: [AlphaVantage](https://www.alphavantage.co), [IEX](https://iexcloud.io/) and [Quandl](https://www.quandl.com/)). Statistics are calculated using [Ito Calculus](https://en.wikipedia.org/wiki/It%C3%B4_calculus) and should be consistent with the results demanded by [Modern Portfolio Theory](https://en.wikipedia.org/wiki/Modern_portfolio_theory) and [Financial Engineering](https://en.wikipedia.org/wiki/Black%E2%80%93Scholes_equation). The portfolios are optimized by minimizing the portfolio's variance/volatility, i.e. by finding the optimal spot on the portfolio's efficient frontier as defined by the [CAPM model](https://en.wikipedia.org/wiki/Capital_asset_pricing_model).

The program's functions are wrapped in [PyQt5](https://doc.qt.io/qtforpython/index.html) widgets which provide a user interface. In addition, visualizations are created by [matplotlib](https://matplotlib.org/3.3.3/contents.html) for easier presentation.

The program's functions can also be wired into a WSGI Application using the [Django framework](https://docs.djangoproject.com/en/3.1/) provided in the <i>/server/</i> directory. See <b>[WSGI Application](#WSGI-Application)</b> for more information. The WSGI application can be containerized using the <i>Dockerfile</i> in the project root and deployed as a microservice. 

# Set Up

## Prerequisites
- [Python 3.8 +](https://www.python.org/downloads/) <br>
- [Docker](https://www.docker.com/products/docker-desktop) (Not required, but recommended for deploying application as a microservice.)<br>

## Environment 

You will want to export the environment variables defined in the <i>/env/</i><b>ENVIRONMENT</b><i>.env</i> file into your current terminal session while using and developing the application. You can `source` the <i>scripts/util/env-vars.sh</i> shell script to load these variables,

> source ./scripts/util/env-vars.sh

If this script is provided an argument, it will search for an <i>.env</i> file within the <i>/env/</i> with the name supplied, i.e.,

> source ./scripts/util/env-vars.sh container

will attempt to export the <i>/env/container.env</i> variables into your session. If it does not find this file, it will copy the <i>/env/.sample.env</i> into a new file with that name and ask you configure it before executing the script again. If no argument is provided, it will search for <i>/env/.env</i> and perform the same checks.

## Package

The application module can also be installed through <b>pip</b> by installing its <i>Pypi</i> package,

`pip install pynance`

Before using the package, make sure to register for API keys at [AlphaVantage](https://www.alphavantage.co), [IEX](https://iexcloud.io/) and [Quandl](https://www.quandl.com/). Store your keys in environment keys named <b>ALPHA_VANTAGE_KEY</b>, <b>QUANDL_KEY</b> and <b>IEX_KEY</b> respectively. 


# CLI Application

## Building From Source Code 

- Note : the first time the CLI application is invoked, it loads a huge amount of data into the <i>/static/</i> directory. This may take a few moments to complete. Subsequent invocations of the CLI application will not take anywhere near as long.

First, from the project root directory, (activate your virtual environment, if using one, and) install all of the requirements,

> pip install -r requirements.txt

For the application to retrieve data, it must be able to connect to <b>AlphaVantage</b>, <b>IEX</b> and <b>Quandl</b>. Register for API keys at [AlphaVantage](https://www.alphavantage.co), [IEX](https://iexcloud.io/) and [Quandl](https://www.quandl.com/). The application searches for environment variables called <b>ALPHA_VANTAGE_KEY</b>, <b>IEX_KEY</b> and <b>QUANDL_KEY</b> that contain the respective API keys. These variables are loaded in through the <i>/env/local.env</i> environment file. There are several other environment variables that configure various aspects of the application. A <i>.sample.env</i> file has been included to demonstrate the appropriate format for all variables, in addition to providing explanations for the other variables that can be changed. Besides the API keys, none of the other environment variables need to be changed from their defaults for the application to function properly. The easiest way to set up is to simply 

> cp .sample.env local.env

And then change the <b>ALPHA_VANTAGE_KEY</b>, <b>IEX_KEY</b> and <b>QUANDL_KEY</b> variables to the values you received when you registered on their respective site. Once the API keys have been set, execute the `python main.py` script. Supply this script an argument preceded by a dash that specifies the function you wish to execute and the ticker symbols to which you wish to apply the function. 

You can add the <i>/scripts/</i> directory to your path to provide access to a BASH script for invoking the application with a python wrapper, i.e. if <i>/scripts/</i> is on your path, then

> pynance -help

will execute the same function as 

> python $PATH_TO_PROJECT/main.py -help

from any directory on your computer.

### Examples 

If I wanted to calculate the risk-return profile for the Facebook (FB), Amazon (AMZN) and Exxon (XOM), I would execute the following command from the project's root directory,

> python main.py -rr FB AMZN XOM

To list the functions available for pynance, use the <i>-help</i> flag to print a help message, i.e.

> python main.py -help

Or use the <i>-ex</i> flag to display a list of examples of syntax,

> python main.py -ex

If you prefer a GUI, most of pynance's functionality has been wired into a PyQt widget GUI that can be launched with,

> python main.py -gui

The GUI is still in development and so may have a few bugs lurking within it. If you discover one, contact the owner of this repo.

Note, if you put the <i>/scripts/</i> directory on your PATH, it provides a light wrapper around the python invocation so you can dispense with the `python main.py` part of each command. In other words, if <i>/scripts/</i> is on your PATH, you can execute the following command from any directory,

> pynance -min SPY GLD EWA

to perform the same operation as the following command performed in the project root directory,

> python main.py -min SPY GLD EWA

In addition, some of the functions have extra arguments that can be provided to filter the output. For example, moving averages can be calculated for a range of dates by using the `-start` and `-end` flags, i.e.

> python main.py -mov -start 2020-03-05 -end 2021-02-01 ALLY BX

will output the (date, average)-tuple series of moving averages defined by the environment variables <b>MA_1</b>, <b>MA_2</b> and <b>MA_3</b> between the dates of 2020-03-05 and 2021-02-01. Note dates must be provided in the <i>YYYY-MM-DD</i> format. See

> python main.py -ex

or

> pynance -ex

for more examples of additional arguments that can be provided to functions.









# PyPi Module

## Setup

TODO: Explain how to install package from PyPi.

TODO: Explain how to set API Key environment variables before using pynance.

### Using Pynance Objects In Your Own Program

TODO: Explain how to use Portfolio objects, Cashflow objects, statistics.py module, markets.py module, services.py module, optimizer.py module, calculator.py module and files.py module. 









# WSGI Application

## Local Setup

The application's functions can also be exposed through an API (a work in progress). To launch the API on your <i>localhost</i>, first configure the <b>APP_PORT</b> in the <i>/env/local.env</i> file. Then, from the <i>/server/pynance_api</i> directory execute,

> python manage.py runserver $APP_PORT

Alternatively, you can run the <i>/scripts/server/launch-server.sh</i> script with an argument of <i>-local</i>,

>./scripts/server/launch-server.sh -local

This will launch the Django app and expose it on your <i>localhost</i>.

## Container Setup

First create a new environment file,

> cp .sample.env container.env

and make sure the <b>APP_ENV</b> variable is set to <i>container</i>. Initialize your environment in your current shell session by executing from the project root directory,

> source ./scripts/util/env-vars.sh container

After you have your environment file initialized, note the <b>IMG_NAME</b>, <b>TAG_NAME</b> and <b>APP_CONTAINER_NAME</b> environment variables will set the image, tag and container name respectively (if that wasn't obvious). 

To start up the server in a container, execute the <i>launch-server</i> script, but provide it an argument of `-container`,

>./scripts/server/pynance-server.sh -container

Or, if you want to build the image without spinning up the container,

>./scripts/docker/pynance-container.sh

Once the image has been built, you can spin up the container using (assuming your environment file has been initialized and loaded into your shell session),

> docker run 
> --publish $APP_PORT:$APP_PORT \\ <br>
> --env-file /path/to/env/file $IMG_NAME:$IMG_TAG

Note, the image will need an environment file to function properly. The application container also supports the CLI functionality, which can be accessed by providing the `docker run` command with the function you wish to execute (you do not need to publish the container on port in this case),

> docker run --env-file /path/to/env/file \\ <br>
> $IMG_NAME:$IMG_TAG -rr BX AMC BB

The <i>Dockerfile</i> defines the container <i>/cache/</i> and <i>/static/</i> directories as volumes, so that you can mount your local directories onto the container. The first time the CLI is ever run, it loads in a substantial amount of static data. Because of this, it is recommended that you mount atleast the <i>/static/</i> directory onto its containerized counterpart,

> docker run --env-file /path/to/env/file \\ <br>
> --mount type=bind,source=/path/to/project/static/,target=/home/static/ \\ <br>
> $IMG_NAME:$IMG_TAG -min SPY QQQ 

The same applies for publishing the application over a <i>localhost</i> port. To run the container in as efficient as manner as possible, execute the following,

> docker run --publish $APP_PORT:$APP_PORT \\ <br>
> --env-file /path/to/env/file \\ <br>
> --mount type=bind,source=/path/to/project/static/,target=/home/static/ --mount type=bind,source=/path/to/project/cache/,target=/home/cache/ \\ <br>
> $IMG_NAME:$IMG_TAG

NOTE: if the <b>APP_ENV</b> in the environment file is set to <i>container</i>, then the application will search for a <b>postgres</b> database on the connection defined by <b>POSTGRES_\*</b> environment variables. If <b>APP_ENV</b> is set to <i>local</i> or not set at all, then the Django app will default to a <b>SQLite</b> database. If running the application as a container, it is recommended you spin up the container with the <i>docker-compose.yml</i> to launch a postgres container (unless you have a postgres service running on your <i>localhost</i>; configure the <b>POSTGRES_*</b> environment variables accordingly). After building the application image, execute from the project root directory,

> docker-compose up

to orchestrate the application with a <b>postgres</b> container. Verify the environment variable <b>POSTGRES_HOST</b> is set to the name of the database service defined in the <i>docker-compose.yml</i>, i.e. <b>POSTGRES_HOST</b> = <i>datasource</i>, if you are running the application as a container through <i>docker-compose</i>.

### API

Some endpoints have unique query parameters, but all endpoints accept the following list of query parameters. See below for more information. 

### Query Parameters
- <i>tickers</i>: an array of the stock/crypto tickers (specified by repeated instances of the <i>tickers</i> parameters).<br>
- <i>start</i>: start date of calculation's time period. If not provided, defaults to 100 days ago. Format: YYYY-MM-DD<br>
- <i>end</i>: end date of calculation's time period. If not provided, defaults to today. Format: YYYY-MM-DD<br>
- <i>jpeg</i>: will visualize and return the result as a JPEG. If not provided, defaults to <i>False</i>. Format: true, false. Case insensitive.<br>

1. <h2>/api/risk-return</h2>
    <b>Description</b><br>
    Returns the annualized mean return and the annualized volatility over the specified date range for the supplied list of ticker symbols.<br><br>
    
    <b>Examples</b><br>
    - /api/risk-return?tickers=ALLY&tickers=SNE&tickers=GME<br>
    - /api/risk-return?tickers=TSLA&start=2020-03-22<br><br>
    
    <b>Response JSON</b><br>
    > { <br>
    >    'annual_return': double, <br>
    >    'annual_volatility': double, <br>
    >    'sharpe_ratio': double
    > }<br><br>

2. <h2>/api/optimize</h2>
    <b>Description</b><br>
    Returns the optimal portfolio allocation (i.e. the portfolio with the minimal volatility) for the supplied list of ticker subject to the target return. If no target return is specified, the portfolio's volatility is minimized without constraints.<br><br>
    
    <b>Additional Query Parameters</b><br>
    - <i>target</i>: Optional. The target return subject to which the portfolio will be optimized. If nothing is provided, function will minimize portfolio variance.<br>
    - <i>sharpe</i>: Optional. Defaults to <i>false.</i> If a value of <i>true</i> is provided, the optimization function will <b>maximize</b> the portfolio's Sharpe ratio instead of minimizing the portfolio's volatility.<br><br>
    <b>Examples</b><br>
    - /api/optimize?tickers=SRAC&tickers=SPCE&tickers=AMZN<br>
    - /api/optimize?tickers=FB&tickers=GOOG&tickers=AMZN&tickers=NFLX&target=0.68<br><br>
    
    <b>Response JSON</b><br>
    > {<br>
    >    'portfolio_return': double, <br>
    >    'portfolio_volatility': double,<br>
    >    'allocations': {<br>
    >        &nbsp;&nbsp;&nbsp;&nbsp;'ticker_allocation': double,<br>
    >        &nbsp;&nbsp;&nbsp;&nbsp;'ticker_allocation': double,<br>
    >        &nbsp;&nbsp;&nbsp;&nbsp;...<br>
    >    }<br>
    >}<br>

3. <h2>/api/efficient-frontier</h2>
    <b>Description</b><br>
    Returns the efficient-frontier of a portfolio defined by the supplied list of tickers. Each point on the frontier tier consists of a mean annualized return, an annualized volatility and the portfolio allocations necessary to generate those two statistics.<br><br>

    - <i>sharpe</i>: Optional. Defaults to <i>false.</i> If a value of <i>true</i> is provided, the optimization function will <b>maximize</b> the portfolio's Sharpe ratio instead of minimizing the portfolio's volatility.<br><br>

    <b>Examples</b><br>
    -/api/efficient-frontier?tickers=ENPH&tickers=TTWO&tickers=ATVI&tickers=DE<br><br>

    <b>Response JSON</b><br>
    > {<br>
    >   'portfolio_1': { <br>
    >   &nbsp;&nbsp;&nbsp;&nbsp;'portfolio_return': double, <br>
    >   &nbsp;&nbsp;&nbsp;&nbsp;'portfolio_volatility': double,<br>
    >   &nbsp;&nbsp;&nbsp;&nbsp;'allocations': {<br>
    >   &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;'ticker_allocation': double,<br>
    >   &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;'ticker_allocation': double,<br>
    >   &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;...<br>
    >   &nbsp;&nbsp;&nbsp;&nbsp;}<br>
    >   },<br>
    >   'portfolio_2': { <br>
    >   &nbsp;&nbsp;&nbsp;&nbsp;'portfolio_return': double,<br>
    >   &nbsp;&nbsp;&nbsp;&nbsp;'portfolio_volatility': double,<br>
    >   &nbsp;&nbsp;&nbsp;&nbsp;'allocations': {<br>
    >   &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;'ticker_allocation': double,<br>
    >   &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;'ticker_allocation': double,<br>
    >   &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;...<br>
    >   &nbsp;&nbsp;&nbsp;&nbsp;}<br>
    >   },<br>
    >   ...<br>
    > }

4. <h2>/api/moving-averages</h2>
    <b>Description</b><br>
    Returns the moving average of the return over the specified dates. The response will include three moving averages series with periods defined by the <b>MA_1</b>, <b>MA_2</b> and <b>MA_3</b> environment variables. In the future, this endpoint will accept user defined periods through request parameters. Note: if no start-date and end-date are supplied, this endpoint will return a snapshot of the current moving averages, not a time series.<br><br>
    
    <b>Examples</b><br><br>

    <b>Response JSON</b><br>
    > { <br>
    >   'ticker':{ <br>
    >   &nbsp;&nbsp;&nbsp;&nbsp;'ticker_MA_1':{ <br>
    >   &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;'date': double, <br>
    >   &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;'date': double, <br>
    >   &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;... <br>
    >   &nbsp;&nbsp;&nbsp;&nbsp;}, <br>
    >   &nbsp;&nbsp;&nbsp;&nbsp;'ticker_MA_2:{ <br>
    >   &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;'date': double, <br>
    >   &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;... <br>
    >   &nbsp;&nbsp;&nbsp;&nbsp;}, <br>
    >   &nbsp;&nbsp;&nbsp;&nbsp;'ticker_MA_3': { <br>
    >   &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;'date': double, <br>
    >   &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;... <br>
    >   &nbsp;&nbsp;&nbsp;&nbsp;}<br>
    > }<br>

5. <h2>/api/discount-dividend-model</h2>
    <b>Description</b><br>
    
    <b>Additional Query Parameters</b><br>
    - <i>discount</i>: Optional. The rate of return used to discount future dividend payments. If nothing is provided, the function will default to the cost of equity capital as estimated by the CAPM model.<br><br>
    
    <b>Examples</b><br>

    <b>Response JSON</b><br>

    <b>Note</b><br>
    If the <i>jpeg</i> parameter is specified for this endpoint, the resulting graph will only contain the plot of the first ticker's dividend history and its accompanying linear regression model; only one equity's dividend graphic can be computed and returned at once. The DDM model price will be output onto the graph's legend. 






# Environment Variables

See the comments in the <i>/env/.sample.env</i> for more information on each variable. Most of the defaults shouldn't need changed except for <b>ALPHA_VANTAGE_KEY</b>, <b>IEX_KEY</b> and <b>QUANDL_KEY</b>.

## Service Configuration

1. <b>PRICE_MANAGER</b>: defines the service manager in charge of retrieving asset price historical data.
2. <b>STAT_MANAGER</b>: defines the service manager in charge of retrieving economic statistics historical data.
3. <b>DIV_MANAGER</b>: defines the service manager in charge of retrieving dividend historical data.
4. <b>ALPHA_VANTAGE_URL</b>: URL used to query <b>AlphaVantage</b> for asset price histories.
5. <b>ALPHA_VANTAGE_CRYPTO_META_URL</b>: URL used to query to <b>AlphaVantage</b> for metadata on crypto market.
6. <b>ALPHA_VANTAGE_KEY</b>: API key required to authenticate <b>AlphaVantage</b> queries.
7. <b>QUANDL_URL</b>: URL used to query <b>Quandl</b> for economic statistics histories.
8. <b>QUANDL_META_URL</b>: URL used to query <b>Quandl</b> for metadata on economic statistics.
9. <b>QUANDL_KEY</b>: API key required to authenticate <b>Quandl</b> queries.
10. <b>IEX_URL</b>: URL used to query <b>IEX</b> for dividend histories.
11. <b>IEX_KEY</b>: API key required to authenticate <b>IEX</b> queries. 

## Algorithm Configuration

12. <b>ITO_STEPS</b>: The number of segments into which the integration domain is divided during the calculation of Ito Integrals.
13. <b>FRONTIER_STEPS</b>: Number of data points calculated in a portfolio's efficient frontier. Each data point consists of a (return, volatility)-tuple for a specific allocation of assets. 
14. <b>MA_1</b>: Number of days in the first Moving Average period. Defaults to 20 if not provided.
15. <b>MA_2</b>: Number of days in the second Moving Average period. Defaults to 60 if not provided.
16. <b>MA_3</b>: Number of days in the third Moving Average period. Defaulst to 100 if not provided.
17. <b>RISK_FREE</b>: values = ("3-Month", "5-Year", "10-Year", "30-Year"). The US Treasury yield used as a proxy for the risk free rate when valuing securities and equities.
18. <b>MARKET_PROXY</b>: Recommend values: ("SPY", "DIA", "QQQ"). Defines the equity ticker symbol used by the application as a proxy for market return. While the recommended values are preferred, there is nothing preventing more obscure ticker symbols from being used the MARKET. GME, for instance. ;)

## CLI Configuration

19. <b>LOG_LEVEL</b>: values = ("info", "debug", "verbose"). Verbose is <i>extremely</i> verbose. The result of every single calculation within the application will be outputted. 
20. <b>FILE_EXT</b>: values = ("json"). Determines in what format cached price, statistic and dividend histories are saved. Currently only supports JSON. In the future, will support XML and CSV.

## GUI Configuration

21. <b>GUI_WIDTH</b>: Defines the width in pixels of the application's root <b>PyQt</b> widget. Defaults to 800 if not provided.
22. <b>GUI_HEIGHT</b>: Defines the height in pixels of the application's root <b>PyQt</b> widget. Defaults to 800 if not provided.

## Application Server Configuration

23. <b>SECRET_KEY</b>: The secret used by Django to sign requests.
24. <b>APP_ENV</b>: Informs the application which environment is it running in, i.e. either <i>local</i> or <i>container</i>
25. <b>APP_PORT</b>: Configures the port on which the WSGI application runs.
26. <b>DEBUG</b>: Configures Django's debug mode. 
27. <b>DJANGO_SUPERUSER_EMAIL</b>:
28. <b>DJANGO_SUPERUSER_USERNAME</b>:
29. <b>DJANGO_SUPERUSER_PASSWORD</b>:

## Database Configuration

- Note: If `APP_ENV == local`, then the server will default to a SQLite database and the following environment variables will 
not affect the application. 

25. <b>POSTGRES_HOST</b>: should be set equal to the name of the <b>postgres</b> service defined in the <i>docker-compose.yml</i>; the default is <i>datasource</i>
26. <b>POSTGRES_PORT</b>:
27. <b>POSTGRES_DB</b>:
28. <b>POSTGRES_USER</b>:
29. <b>POSTGRES_PASSWORD</b>:
30. <b>PGDATA</b>:

### Container Configuration
22. <b>APP_IMG_NAME</b>: Image name of the application created during the Docker build.
23. <b>APP_TAG_NAME</b>: Tag applied to the application image created during the Docker build.
24. <b>APP_CONTAINER_NAME</b>: Container name applied to the running application image when it is spun up.
25. <b>SCRAPPER_ENABLED</b>: If set to True, the container will scrap price histories from the external services for storage in the <b>postgres</b> instance orchestrated with the application. 









# TODOS

1. Rejigger GUI to have DateWidgets to select dates in GUI and take advantage of the new date filtering functionality.

2. Hook up 'Optimize' widget to optimize subject to constraint.

3. Create functions for calculation and plotting of yield curve. Relevant FRED symbols: 
    - DFF = Effective Federal Funds Rate<br>
    - DTB3 = 3 Month Treasury<br>
    - DGS5 = 5 Year Treasury Constant Maturity<br>
    - DGS10 = 10 Year Treasury Constant Maturity<br>
    - DGS30 = 30 Year Treausry Constant Maturity<br>
    - T5YIE = 5 Year Breakeven Inflation Rate<br>
    - T10YIE = 10 Year Breakeven Inflation Rate<br>

4. Create tabs in GUI for: Markets, Fundamentals, Options, Economy. Markets will feature the portfolio optimization and financial price statistics such as moving averages and efficient frontiers. Fundamentals will feature graphs and calculations of accounting statistics like EBITDA, Enterprise Value, etc. Options will feature functions for calculating IV of options, displaying the volatility skew, historical vs. implied volatility, and option greeks. Economy will feature graphs of the yield curve, GDP, etc. 

5. Copy IV algorithm and option greek algorithms from old python cli program. 

6. TEST MOVING AVERAGE ALGORITHM FOR MIX OF ASSET TYPES. I think there may be some mismatch of types in date comparisons.

7. Correlation algorithm needs tested for mix of asset types as well, i.e. equities and crypto.

8. Create automated tests and integrate repo with a CircleCi pipeline that builds the image. Will need to find a cloud provider to deploy onto. Perhaps [Heroku](https://www.heroku.com/)

15. Angular frontend! Separate container. Serve through nginx and queries backend <b>pynance</b> server. 

16. If an option prices API is found, then IV can be calculated for a specific equity. The optimization algorithm can be expanded to optimize over IV of a portfolio, instead of the Historical Volatility. Allow user to specify what type of volatility the portfolio will use in its optimization, historical or implied. Will need to account for skew, somehow. 

17. Test moving averages plot generation.

18. Pretty sure the reason the len(moving_averages) != len(dates_between) in moving average algorithm is because dates_between doesn't include the dates themselves; it's only returning...dun dun dun...the dates between, not the dates themselves. 

19. Request parameters not being taken to uppercase.

20. Other types of screening. Discounted Cash Flow, for instance. 

21. Add watchlist functionality for crypto assets. Differentiate in /data/common/ between watchlist_equity.json and watchlist_crypto.json. Integrate watchlist functionality into GUI and API. Will need to implement API Key authentication functionality before introducing watchlist to API to account for different users's watchlist.

22. Wire DDM functionality into API. Done. Now Test.

23. Research annotations for cashflow object's growth function and portfolio's return/volatility functions. Perhaps a way of injecting them into the GUI easier. Not sure.

26. Document how to use objects and functions in shell/scripts.

27. Raise Exceptions instead of returning False when functions fail. See #4: https://deepsource.io/blog/8-new-python-antipatterns/

29. Return <b>sharpe ratio</b> with response at <i>/api/risk-return</i>. Considering returning the portfolio beta, as well. We'll see. Functionality exists, just needs wired in.

30. Does it make sense to calculate the 'Sharpe Frontier'?

31. Allow relative file references when saving analysis. Right now needs to be absolute path inputted into -save argument. Also, save return profiles. 

32. Export function results as JSON on Angular frontend, i.e. allow users to save results.

33. Facts/opinion tabs.

34. Mark important points of Efficient Frontier, i.e. minimum variance, maximum return, maximum sharpe ratio.

35. Correlation time series.

### NOTES

1. All date strings should be converted to <b>datetime.dates</b> at point of contact with user, i.e. in the main.py file where CLI arguments are parsed, within the gui where user arguments are pulled from widgets or in the server's endpoint views where user arguments are provided through query parameters, before passing it the service/statistics/portfolio functions. All functions in the <i>/app/</i> module assume dates are passed in as <b>datetime.dates</b>.

2. The first time the CLI application is invoked, it loads a huge amount of data in the <i>/static/</i> directory. This may take a few moments to complete. Subsequent invocations of the CLI application will not take anywhere near as long.


### USEFUL LINKS

- [Getting image from API in Angular](https://stackoverflow.com/questions/45530752/getting-image-from-api-in-angular-4-5)