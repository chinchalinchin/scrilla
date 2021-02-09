# Pynance: A Financial Optimization Application

This is a financial application that calculates asset correlation, statistics and optimal portfolio allocations using data it retrieves from a variety of sources, chief among them [AlphaVantage](https://www.alphavantage.co) and [Quandl](https://www.quandl.com/). Statistics are calculated using [Ito Calculus](https://en.wikipedia.org/wiki/It%C3%B4_calculus) and should be consistent with the results demanded by [Modern Portfolio Theory](https://en.wikipedia.org/wiki/Modern_portfolio_theory) and [Financial Engineering](https://en.wikipedia.org/wiki/Black%E2%80%93Scholes_equation). The portfolios are optimized by minimizing the portfolio's variance/volatility, i.e. by finding the optimal spot on the portfolio's efficient frontier as defined by the [CAPM model](https://en.wikipedia.org/wiki/Capital_asset_pricing_model).

The program's functions are wrapped in [PyQt5](https://doc.qt.io/qtforpython/index.html) widgets which provide visualizations from [matplotlib](https://matplotlib.org/3.3.3/contents.html) in addition to the raw output.

The program's function can also be wired into a WSGI Application using the [Django framework](https://docs.djangoproject.com/en/3.1/) provided in the <i>/server/</i> directory. See **WSGI Application** for more information. The WSGI application can be containerized using the <i>Dockerfile</i> in the project root and deployed as a microservice. 

# Set Up

## Prerequisites
- [Python 3.8 +](https://www.python.org/downloads/) <br>
- [Docker](https://www.docker.com/products/docker-desktop) (<span style="font-size:0.5em;">Not required, but recommended for deploying application as a microservice.</span>)<br>

## Environment

You may want to export the environment variables defined in the <i>/env/.env</i> file into your current terminal session. You can use the <i>scripts/util/env-vars.sh</i> shell script to load these variables,

> ./scripts/util/env-vars.sh

If this script is provided an argument, it will search for an <i>.env</i> file withiin the <i>/env/</i> with the name supplied, i.e.,

> ./scripts/util/env-vars.sh container

will attempt to export the <i>/env/container.env</i> variables into your session. If it does not find this file, it will copy the <i>/env/.sample.env</i> into a new file with that name and ask you configure it before executing the script again.

## CLI Application

First, from the project root directory, (activate your virtual environment, if using one, and) install all of the requirements,

> pip install -r requirements.txt

For the application to retrieve data, it must be connected to AlphaVantage and Quandl. Register for API keys at [AlphaVantage](https://www.alphavantage.co) and [Quandl](https://www.quandl.com/). The application searches for environment variables called **ALPHA_VANTAGE_KEY** and **QUANDL_KEY** that contain the respective API keys. These variables are loaded in through the <i>/env/.env</i> environment. There are several other environment variables that configure various aspects of the application. A <i>.sample.env</i> file has been included to demonstrate the appropriate format for all variables, in addition to providing explanations for the other variables that can be changed. Besides the API keys, none of the other environment variables need to be changed from their defaults for the application to function properly. The easiest way to set up is to simply 

> cp .sample.env .env

And then change the **ALPHA_VANTAGE_KEY** and **QUANDL_KEY** variables to the values you received when you registered on their respective site. Once the API keys have been set, execute the <i>./main.py script</i>. Supply this script an argument with a dash that specifies the function you wish to execute and the ticker symbols you wish to apply the function to. 

After the application searches for API keys in the <i>.env</i> file, it will search for API keys in <i>config.json</i>. If this file exists, it will override any keys found in <i>.env</i>. If no keys are found within either file, a popup dialog box (QInputDialog from PyQt.QtWidgets) will prompt the user to register for their keys and enter them into a text field. The application will then test the API key entered and if it is valid, save it in the <i>config.json</i> file. Subsequent application calls will leverage the credentials in this file.

You can add the <i>/scripts/</i> directory to your path to provide access to the BASH script for invoking the application with a python wrapper, i.e. if <i>/scripts/</i> is on your path, then

> pynance -help

will execute the same function as 

> python $PATH_TO_PROJECT/main.py -help

from any directory on your computer.

### Examples 

If I wanted to calculate the risk-return profile for the Facebook (FB), Amazon (AMZN) and Exxon (XOM), I would execute the following command from the project's root directory,

> python ./main.py -rr FB AMZN XOM

To list the functions available for pynance, use the <i>-help</i> flag to print a help message, i.e.

> python ./main.py -help

Or use the <i>-ex</i> flag to display a list of examples of syntax,

> python ./main.py -ex

If you prefer a GUI, most of pynance's functionality has been wired into a PyQt widget GUI that can be launched with,

> python ./main.py -gui

The GUI is still in development and so may have a few bugs lurking within it. If you discover one, contact the owner of this repo.

Note, if you put the <i>/scripts/</i> directory on your PATH, it provides a light wrapper around the python invocation so you can dispense with the `python ./main.py` part of each command. In other words, if <i>/scripts/</i> is on your PATH, you can execute the following command from any directory,

> pynance -min SPY GLD EWA

to perform the same operation as the following command performed in the project root directory,

> python ./main.py -min SPY GLD EWA

In addition, some of the functions have extra arguments that can be provided to filter the output. For example, moving averages can be calculated for a range of dates by using the `-start` and `-end` flags, i.e.

> python ./main.py -mov -start 2020-03-05 -end 2021-02-01 ALLY BX

will output the (date, average)-tuple series of moving averages defined by the environment variables **MA_1**, **MA_2** and **MA_3** between the dates of 2020-03-05 and 2021-02-01. Note dates must be provided in the <i>YYYY-MM-DD</i> format. See

> python ./main.py -ex

or

> pynance -ex

for more examples of additional arguments that can be provided to functions.

## WSGI Application

### Local Setup

The application's functions can also be exposed through an API (a work in progress). To launch the API on your <i>localhost</i>, first configure the **SERVER_PORT** in the <i>/env/.env</i> file. Then, from the <i>/server/pynance_api</i> directory execute,

> python manage.py runserver $SERVER_PORT

Alternatively, you can run the <i>/scripts/server/launch-server.sh</i> script with an argument of <i>-local</i>,

>./scripts/server/launch-server.sh -local

This will launch embed the Django app on your <i>localhost</i> and expose the 

### Container Setup

If you have your environment file initialized, then the **IMG_NAME**, **TAG_NAME** and **CONTAINER_NAME** environment variables will set the (obviously) image, tag and container respectively. 

To start up the server in a container, execute the <i>launch-server</i> script, but provide it an argument of `-container`,

>./scripts/server/launch-server.sh -container

Or, if you want to build the image without spinning up the container,

>./scripts/docker/build-container.sh

Once the image has been built, you can spin up the container using (assuming your environment file has been initialized and loaded into your shell sessoin),

> docker run --publish $SERVER_PORT:$SERVER_PORT --env-file /path/to/env/file $IMG_NAME:$IMG_TAG

Note, the image will need an environment file to function properly. The application container also supports the CLI functionality by providing the `docker run` command with the function you wish to execute (you do not need to publish the container on port in this case),

> docker run --env-file /path/to/env/file $IMG_NAME:$IMG_TAG -rr BX AMC BB

The <i>Dockerfile</i> defines the virtual <i>/cache/</i> and <i>/static/</i> directories as volumes, so that you can mount your local directories onto the container. The first time the CLI is ever run, it loads in a substantial amount of static data. Because of this, it is recommended that you mount atleast the <i>/static/</i> directory onto its virtual counterpart,

> docker run --env-file /path/to/env/file --mount type=bind,source=/path/to/project/static/,target=/home/static/ $IMG_NAME:$IMG_TAG -min SPY QQQ 

The same applies for publishing the application over a <i>localhost</i> port. To run the container in as efficient as manner as possible, execute the following,

> docker run --publish $SERVER_PORT:$SERVER_PORT --env-file /path/to/env/file --mount type=bind,source=/path/to/project/static/,target=/home/static/ --mount type=bind,source=/path/to/project/cache/,target=/home/cache/ $IMG_NAME:$IMG_TAG

## API

1. <h2>/api/risk-return</h2>
    **Description**<br>
    Returns the annualized mean annual return and the annualized volatility over the specified date range for the supplied list of ticker symbols.<br><br>
    **Query Parameters**<br>
    - <i>tickers</i>: an array of the stock/crypto tickers (specified by repeated instances of the <i>tickers</i> parameters).<br>
    - <i>start</i>: start date of calculation's time period. Format: YYYY-MM-DD<br>
    - <i>end</i>: end date of calculation's time period. Format: YYYY-MM-DD<br>
    **Examples**<br>
    - /api/risk-return?tickers=ALLY&tickers=SNE&tickers=GME<br>
    - /api/risk-return?tickers=TSLA&start=2020-03-22<br>

2. <h2>/api/optimize</h2>
    **Description**<br>
    Returns the optimal portfolio allocation (i.e. the portfolio with the minimal volatility) for the supplied list of ticker subject to the target return. If no target return is specified, the portfolio's volatility is minimized without constraints.<br><br>
    **Query Paramters**<br>
    - <i>tickers</i>: an array of the stock/crypto tickers (specified by repeated instances of the <i>tickers</i> parameters).<br>
    - <i>target</i>: the target return subject to which the portfolio will be optimized.<br>
    - <i>start</i>: start date of calculation's time period. Format: YYYY-MM-DD<br>
    - <i>end</i>: end date of calculation's time period. Format: YYYY-MM-DD<br>
    **Examples**<br>
    - /api/optimize?tickers=SRAC&tickers=SPCE&tickers=AMZN<br>
    - /api/optimize?tickers=FB&tickers=GOOG&tickers=AMZN&tickers=NFLX&target=0.68

## Environment

See the comments in the <i>/env/.sample.env</i> for more information on each variable. Most of the defaults shouldn't need changed except for **ALPHA_VANTAGE_KEY** and **QUANDL_KEY**.

### Service Configuration

1. PRICE_MANAGER: defines the service manager in charge of retrieving asset price historical data.
2. STAT_MANAGER: defines the service manager in charge of retrieving economic statistics historical data.
3. ALPHA_VANTAGE_URL: URL used to query AlphaVantage for provided price histories.
4. ALPHA_VANTAGE_CRYPTO_META_URL: URL used to query to AlphaVantage for metadata on crypto market.
5. ALPHA_VANTAGE_KEY: API key required to authenticate AlphaVantage queries.
6. QUANDL_URL: URL used to query Quandl fo economic statistics historical data.
7. QUANDL_META_URL: URL used to query Quandl for metadata on economic statistics.
8. QUANDL_KEY: API key required to authenticate Quandl queries.

### Algorithm Configuratoin

9. FRONTIER_STEPS: Number of data points calculated in a portfolio's efficient frontier. Each data point consists of a (return, volatility)-tuple for a specific allocation of assets. 
10. MA_1: Number of days in the first Moving Average period. Defaults to 20 if not provided.
11. MA_2: Number of days in the second Moving Average period. Defaults to 60 if not provided.
12. MA_3: Number of days in the third Moving Average period. Defaulst to 100 if not provided.

### CLI Configuration

13. DEBUG: Increases the amount of output, in order to find problems in the application's algorithms.
14. VERBOSE: Vastly increases the amount of output. Will include output from each calculation conducted. 
15. INVESTMENT_MODE: Determines whether or not asset allocations are outputted in percentages or dollars. If set to <i>True</i>, the CLI will prompt the user to input the amount of money invested in a given portfolio before outputting results.
16. INIT: A flag that will cause the application to always initialize the <i>/static/</i> directory everytime it executes. TODO: probably don't need this anymore since there is a CLI function that will re-initialize the <i>/static/</i> directory.

### GUI Configuration

17. GUI_WIDTH: Defines the width in pixels of the application's root **PyQt** widget. Defaults to 800 if not provided.
18. GUI_HEIGHT: Defines the height in pixels of the application's root **PyQt** widget. Defaults to 800 if not provided.

### Server Configuration

19. SECRET_KEY: The secret used by Django to sign requests.
20. APP_ENV: Informs the application which environment is it running in, i.e. either <i>local</i> or <i>container</i>
21. SERVER_PORT: Configures the port on which the WSGI application runs.

### Container Configuration
22. IMG_NAME: Name of the image created during the Docker build.
23. TAG_NAME: Tag applied to the image created during the Docker build.
24. CONTAINER_NAME: Name of the container applied to the image when it is spun up.

# TODOS

1. add different price_managers and stat_managers besides AlphaVantage and Quandl. Find API service for options quotes.

2. Rejigger moving averages algorithm (calculation and plotting) to accept current snapshot of moving averages and print bar graph (already does this), or accept a history of moving averages and created a line plot with several labeled serieses (moving average algorithm returns the sample data correctly, need to configure plotting of sample data now).

3. Rejigger GUI to have DateWidgets to select dates in GUI and take advantage of the new date filtering functionality.

4. [Free Icons](https://streamlineicons.com/) for GUI. Verify licensing terms. 

5. Cancel button needs to exit application when prompting user for API keys.

6. Return None instead of False when errors are encountered in methods, so methods can have strict typing. Better for documentation! 

7. set up argument parsing for Investment Mode so user doesn't have to change .env variable to use Investment Mode from cli.

8. Hook up 'Optimize' widget to optimize subject to constraint.

9. Use fundamentals API from Alpha Vantage to calculate things like EBITBA, Enterprise Value, Price to Earnings, etc.

10. Hook API into pynance functions and create micro-service for the app.
    - During Docker image build, be sure to initialize static data so user doesn't have to.
    - Create docker image
    - Possibly initialize database image through compose to cache data instead of saving it to virtual filesystem. Either that, or define a volume to persist cache across image builds. 
    - Endpoints that serve images of graphs calculated from the core app. 

11. Create functions for calculation and plotting of yield curve.

12. Create tabs in GUI for: Markets, Fundamentals, Options, Economy. Markets will feature the portfolio optimization and financial price statistics such as moving averages and efficient frontiers. Fundamentals will feature graphs and calculations of accounting statistics like EBITDA, Enterprise Value, etc. Options will feature functions for calculating IV of options, displaying the volatility skew, historical vs. implied volatility, and option greeks. Economy will feature graphs of the yield curve, GDP, etc. 

13. Copy IV algorithm and option greek algorithms from old python cli program. 

14. Implement start and end date arguments for optimization algorithms, so user can optimizer over any given date range.

15. TEST MOVING AVERAGE ALGORITHM FOR MIX OF ASSET TYPES. I think there may be some mismatch of types in date comparisons.

16. Expand optimization algorithms to take into account START_DATE and END_DATE! Need to adjust Portfolio class! 

17. Scrap historical closing prices up to current year from API and store in database. Set up container orchestration via <i>docker-compose</i> 

18. ERROR: There seems to be a problem with the correlation algorithm over time ranges longer than 100 days. NOTE: Pretty sure this is resolved now, but needs further testing. Correlation algorithm needs test for mix of asset types as well, i.e. equities and crypto.

19. Condense DEBUG and VERBOSE environment variables into a string valued variable for simpler output configuration, i.e. LOG_LEVEL or some such instead of separating the two options.

### NOTES

1. IMPORTANT: All date strings should be converted to **datetime.dates** at point of contact with user, i.e. in the main.py file where CLI arguments are parsed, within the gui where user arguments are pulled from widgets or in the server's endpoint views where user arguments are provided through query parameters, before passing it the service/statistics/portfolio functions. All functions in the <i>/app/</i> module assume dates are passed in as **datetime.dates**.