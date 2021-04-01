# ENVIRONMENT

## Loading Varibles Into Terminal Session

You will want to export the environment variables defined in the <i>/env/<b>environment</b>.env</i> file into your current terminal session while using and developing the application. You can `source` the <i>scripts/util/env-vars.sh</i> shell script to load these variables,

> source ./scripts/util/env-vars.sh

If this script is provided an argument, it will search for an <i>.env</i> file within the <i>/env/</i> with the name supplied, i.e.,

> source ./scripts/util/env-vars.sh container

will attempt to export the <i>/env/container.env</i> variables into your session. If it does not find this file, it will copy the <i>/env/.sample.env</i> into a new file with that name and ask you configure it before executing the script again. If no argument is provided, it will search for <i>/env/.env</i> and perform the same checks.

## Environment Variables

See the comments in the <i>/env/.sample.env</i> for more information on each variable. Most of the defaults shouldn't need changed except for <b>ALPHA_VANTAGE_KEY</b>, <b>IEX_KEY</b> and <b>QUANDL_KEY</b>.

### Service Configuration

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

### Algorithm Configuration

12. <b>ITO_STEPS</b>: The number of segments into which the integration domain is divided during the calculation of Ito Integrals.
13. <b>FRONTIER_STEPS</b>: Number of data points calculated in a portfolio's efficient frontier. Each data point consists of a (return, volatility)-tuple for a specific allocation of assets. 
14. <b>MA_1</b>: Number of days in the first Moving Average period. Defaults to 20 if not provided.
15. <b>MA_2</b>: Number of days in the second Moving Average period. Defaults to 60 if not provided.
16. <b>MA_3</b>: Number of days in the third Moving Average period. Defaulst to 100 if not provided.
17. <b>RISK_FREE</b>: values = ("3-Month", "5-Year", "10-Year", "30-Year"). The US Treasury yield used as a proxy for the risk free rate when valuing securities and equities.
18. <b>MARKET_PROXY</b>: Recommend values: ("SPY", "DIA", "QQQ"). Defines the equity ticker symbol used by the application as a proxy for market return. While the recommended values are preferred, there is nothing preventing more obscure ticker symbols from being used the MARKET. GME, for instance. ;)

### CLI Configuration

19. <b>LOG_LEVEL</b>: values = ("info", "debug", "verbose"). Verbose is <i>extremely</i> verbose. The result of every single calculation within the application will be outputted. 
20. <b>FILE_EXT</b>: values = ("json"). Determines in what format cached price, statistic and dividend histories are saved. Currently only supports JSON. In the future, will support XML and CSV.

### GUI Configuration

21. <b>GUI_WIDTH</b>: Defines the width in pixels of the application's root <b>PyQt</b> widget. Defaults to 800 if not provided.
22. <b>GUI_HEIGHT</b>: Defines the height in pixels of the application's root <b>PyQt</b> widget. Defaults to 800 if not provided.

### Application Server Configuration

23. <b>SECRET_KEY</b>: The secret used by Django to sign requests.
24. <b>APP_ENV</b>: Informs the application which environment is it running in, i.e. either <i>local</i> or <i>container</i>
25. <b>APP_PORT</b>: Configures the port on which the WSGI application runs.
26. <b>DEBUG</b>: Configures Django's debug mode. 
27. <b>DJANGO_SUPERUSER_EMAIL</b>:
28. <b>DJANGO_SUPERUSER_USERNAME</b>:
29. <b>DJANGO_SUPERUSER_PASSWORD</b>:

### Database Configuration

- Note: If `APP_ENV not in ['local', 'container']`, then the server will default to a SQLite database and the following environment variables will 
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