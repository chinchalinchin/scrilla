import os, csv, json
import itertools
import datetime, time
import requests

import app.settings as settings
import app.markets as markets

import util.logger as logger
import util.helper as helper

# os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
CLOSE_PRICE = "close"
OPEN_PRICE = "open"
output = logger.Logger("app.services", settings.LOG_LEVEL)

def parse_price_from_date(prices, date, asset_type, which_price=CLOSE_PRICE):
    """
    Parameters
    ----------
    1. prices : { str : str } \n
        2D list containing the AlphaVantage response with the first layer peeled off, i.e.
        no metadata, just the date and prices. \n \n
    2. date: str \n
        String of the date to be parsed. Note: this is not a datetime.date object. String
        must be formatted YYYY-MM-DD \n \n
    3. asset_type : str \n
        String that specifies what type of asset price is being parsed. Options are statically
        typed in the app.settings.py file: app.settings.ASSET_EQUITY, app.settings.ASSET_CRYPTO \n \n
    
    Output
    ------
    String containing the price on the specified date.
    """
    try:
        if settings.PRICE_MANAGER == 'alpha_vantage':
            if asset_type == settings.ASSET_EQUITY:
                if which_price == CLOSE_PRICE:
                    return prices[date][settings.AV_RES_EQUITY_CLOSE_PRICE]
                elif which_price == OPEN_PRICE:
                    return prices[date][settings.AV_RES_EQUITY_OPEN_PRICE]
            elif asset_type == settings.ASSET_CRYPTO:
                if which_price == CLOSE_PRICE:
                    return prices[date][settings.AV_RES_CRYPTO_CLOSE_PRICE]
        else: 
            # TODO: other service parsing goes here.
            pass

    except:
        output.debug('Price unable to be parsed from date.')
        return False

def query_service_for_daily_price_history(ticker, start_date=None, end_date=None, asset_type=None, full=False):
    """
    Description
    -----------
    Function in charge of querying external services for daily price history. \n \n

    Parameters
    ----------
    1. tickers : [ str ] \n
        Required. List of ticker symbols corresponding to the price histories to be retrieved. \n \n
    2. start_date : datetime.date \n 
        Optional. Start date of price history. Defaults to None. \n \n
    3. end_date : datetime.date \n 
        Optional: End date of price history. Defaults to None. \n \n
    4. full: boolean \n
        Optional: If specified, will return the entire price history. Will override start_date and end_date if provided. Defaults to False. \n \n
    
    Notes
    -----
    By default, AlphaVantage returns the last 100 days of prices for equities, while returning the entire price history for crypto asset. If no start_date or end_date are specified, this function will truncate the crypto price histories to have a length of 100 so the price histories across asset types are the same length. 
    """
    # TODO: price histories aren't the same length, though, because of weekends. 
    # TODO: retrieve crypto history for len(crypto_prices) = 100 + weekends
    # TODO: checking end and start dates for holiday/weekend in this method may 
    #       mess up statistical calculations, i.e. statistics.py expects a sample 
    #       of a certain size and gets a different size.

    ### START: ARGUMENT VALIDATION ###
    switch_flag = start_date is not None and end_date is not None

        # Check if start_date is today
    if not full:
        if start_date is not None:
            if helper.is_date_today(start_date):
                output.debug(f'Invalid date range. Start Date {start_date} is today!')
                return False
            # Check if end_date is today
        if end_date is not None:
            if helper.is_date_today(end_date):
                output.debug(f'End Date {end_date} is today!')
                end_date = None
            # Check if end_date < start_date or end_date = start_date
        if switch_flag:
            time_delta = end_date - start_date
            if time_delta.days < 0:
                buffer = end_date
                end_date = start_date
                start_date = end_date
            elif time_delta == 0:
                output.debug(f'End Date {end_date} = Start Date {start_date}!')
                return False
    else:
        output.debug(f'Full price history requested, nulling start_date and end_date')
        start_date, end_date = None, None

    if asset_type is None:
        output.debug('No asset type provided, determining from ticker.')
        asset_type=markets.get_asset_type(ticker)  
    else: 
        output.debug(f'Asset type {asset_type} provided')
        asset_type=asset_type

        # Verify dates fall on trading days (i.e. not weekends or holidays) if asset_type is ASSET_EQUITY
    if asset_type == settings.ASSET_EQUITY and (start_date is not None or end_date is not None):
        if start_date is not None:
            if helper.is_date_holiday(start_date):
                output.debug(f'{start_date} is a holiday. Equities do not trade on holidays.')

                start_date = helper.get_previous_business_date(start_date)
                output.debug(f'Setting start date to next business day, {start_date}')

            elif helper.is_date_weekend(start_date):
                output.debug(f'{start_date} is a weekend. Equities do not trade on weekends.')

                start_date = helper.get_previous_business_date(start_date)
                output.debug(f'Setting start date to previous business day, {start_date}')
        
        if end_date is not None:
            if helper.is_date_holiday(end_date):
                output.debug(f'{end_date} is a holiday. Equities do not trade on holidays.')

                end_date = helper.get_previous_business_date(end_date)
                output.debug(f'Setting end date to previous business day, {end_date}.')

            elif helper.is_date_weekend(end_date):
                output.debug(f'{end_date} is a weekend. Equities do not trade on weekends.')
                
                end_date = helper.get_previous_business_date(end_date)
                output.debug(f'Setting end date to previous business day, {end_date}.')
    ### END: ARGUMENT VALIDATION ###

    ### START: SERVICE QUERY CREATION ###
    if settings.PRICE_MANAGER == "alpha_vantage":

        query = f'{settings.PARAM_AV_TICKER}={ticker}'

        if asset_type == settings.ASSET_EQUITY:
            query += f'&{settings.PARAM_AV_FUNC}={settings.ARG_AV_FUNC_EQUITY_DAILY}'
        elif asset_type == settings.ASSET_CRYPTO:
            query += f'&{settings.PARAM_AV_FUNC}={settings.ARG_AV_FUNC_CRYPTO_DAILY}&{settings.PARAM_AV_DENOM}={settings.DENOMINATION}'
        else:
            return False

            # NOTE: only need to modify EQUITY query, CRYPTO always returns full history
        if (full or start_date is not None or end_date is not None) and (asset_type == settings.ASSET_EQUITY):
            if asset_type == settings.ASSET_EQUITY:
                query += f'&{settings.PARAM_AV_SIZE}={settings.ARG_AV_SIZE_FULL}'

        auth_query = query + f'&{settings.PARAM_AV_KEY}={settings.AV_KEY}'
        url=f'{settings.AV_URL}?{auth_query}'  
        output.debug(f'AlphaVantage query (w/o key) = {query}')   
        
        prices = requests.get(url).json()
        first_element = helper.get_first_json_key(prices)

        # check for bad response
        if first_element == settings.AV_RES_ERROR:
            output.debug(prices[settings.AV_RES_ERROR])
            return False

        # check and wait for API rate limit refresh
        first_pass = True
        while first_element == settings.AV_RES_LIMIT:
            if first_pass:
                output.debug('AlphaVantage API rate limit exceeded. Waiting...')
                first_pass = False
            else:
                output.debug('Waiting...')
            time.sleep(10)
            prices = requests.get(url).json()
            first_element = helper.get_first_json_key(prices)

        # Equity Response Parsing
        # TODO: could possibly initial start_index = 0 and end_index = len(prices)
        #           and then filter through conditional and return prices[start:end]
        #           no matter what?
        # NOTE: Remember AlphaVantage is ordered current to earliest. END_INDEX is 
        # actually the beginning of slice and START_INDEX is actually end of slice. 
        if asset_type == settings.ASSET_EQUITY:
            if not full and (start_date is not None and end_date is not None):
                try:
                    start_string, end_string = helper.date_to_string(start_date), helper.date_to_string(end_date)
                    start_index = list(prices[settings.AV_RES_EQUITY_FIRST_LAYER].keys()).index(start_string)
                    end_index = list(prices[settings.AV_RES_EQUITY_FIRST_LAYER].keys()).index(end_string)
                    prices = dict(itertools.islice(prices[settings.AV_RES_EQUITY_FIRST_LAYER].items(), end_index, start_index))
                except:
                    output.sys_error()
                    output.debug('Indicated dates not found in AlphaVantage Response.')
                    return False

            elif not full and (start_date is None and end_date is not None):
                try:
                    end_string = helper.date_to_string(end_date)
                    end_index = list(prices[settings.AV_RES_EQUITY_FIRST_LAYER].keys()).index(end_string)
                    prices = dict(itertools.islice(prices[settings.AV_RES_EQUITY_FIRST_LAYER].items(), end_index))
                except:
                    output.debug('End Date not found in AlphaVantage Response.')
                    return False

            elif not full and (start_date is not None and end_date is None):
                try:
                    start_string = helper.date_to_string(start_date)
                    start_index = list(prices[settings.AV_RES_EQUITY_FIRST_LAYER].keys()).index(start_string)
                    prices = dict(itertools.islice(prices[settings.AV_RES_EQUITY_FIRST_LAYER].items(), 0, start_index))
                except:
                    output.debug('End Date not found in AlphaVantage Response.')
                    return False
            
            else:
                try:
                    prices = prices[settings.AV_RES_EQUITY_FIRST_LAYER]
                except: 
                    output.debug('Error encountered ')
                    prices = False
            return prices

        # TODO: len(crypto_prices) - weekends. do i want to do it here? or in statistics.py when
        # the different datasets are actually being compared? probably statistics.py.
        # NO! because statistics.py will need complete datasets to compare, so it's better
        # that crypto returns a dataset longer than is needed!
        #
        # TODO: can probably set RESPONSE_KEY to asset_type and condense the double conditional
        # branching down to one branch. will make it simpler.
        elif asset_type == settings.ASSET_CRYPTO:
            if not full and (start_date is None and end_date is None):
                truncated_prices, index = {}, 0
                for date in prices[settings.AV_RES_CRYPTO_FIRST_LAYER]:
                    if index < 100:
                        truncated_prices[date] = prices[settings.AV_RES_CRYPTO_FIRST_LAYER][date]
                    else:
                        return truncated_prices
                    index += 1

            elif not full and (start_date is not None and end_date is not None):
                try:
                    start_string, end_string = helper.date_to_string(start_date), helper.date_to_string(end_date)
                    start_index = list(prices[settings.AV_RES_CRYPTO_FIRST_LAYER].keys()).index(start_string)
                    end_index = list(prices[settings.AV_RES_CRYPTO_FIRST_LAYER].keys()).index(end_string)
                    prices = dict(itertools.islice(prices[settings.AV_RES_CRYPTO_FIRST_LAYER].items(), end_index, start_index))
                except:
                    output.debug('Indicated dates not found in AlphaVantage Response.')
                    return False

            elif not full and (start_date is None and end_date is not None):
                try:
                    end_string = helper.date_to_string(end_date)
                    end_index = list(prices[settings.AV_RES_CRYPTO_FIRST_LAYER].keys()).index(end_string) 
                    prices = dict(itertools.islice(prices[settings.AV_RES_CRYPTO_FIRST_LAYER].items(), end_index))
                except:
                    output.debug('End Date not found in AlphaVantage Response.')
                    return False

            elif not full and (start_date is not None and end_date is None):
                try:
                    start_string = helper.date_to_string(end_date)
                    start_index = list(prices[settings.AV_RES_CRYPTO_FIRST_LAYER].keys()).index(start_string)
                    prices = dict(itertools.islice(prices[settings.AV_RES_CRYPTO_FIRST_LAYER].items(), 0, start_index))
                except:
                    output.debug('End Date not found in AlphaVantage Response.')
                    return False

            else:
                prices = prices[settings.AV_RES_CRYPTO_FIRST_LAYER]
            
            return prices

    else:
        output.debug("No PRICE_MANAGER set in .env file!")

# TODO: Crypto queries return all dates and price even if no start_date is provided.
#       Need to truncuate crypto queries to last 100 days for caching. 
# TODO: should I query database in app module or server module? regardless, function calls
#       should go through this method so they always check the cache, rather than having 
#       objects that call this function check the cache (currently how it does it).
# TODO: don't query the database here. leave services to interface with services. leave
#       database stuff to django. 
#       But then how will statistics calculate based on database values? 
def get_daily_price_history(ticker, start_date=None, end_date=None):
    """
    Parameters
    ----------
    tickers : [ str ]
        Required. List of ticker symbols corresponding to the price histories to be retrieved.

    Output
    ------
    { date (str) : price (str) }
        List of prices and their corresponding dates. 
    Notes
    -----
    Only recent prices are cached, i.e. the last 100 days of prices. Calls for other periods of time will not be cached and can take considerably longer to load, due to the API rate limits on AlphaVantage. This function
    should only be used to retrieve the last 100 days of prices. 
    """

    if start_date is None and end_date is None:
        output.debug(f'Checking for {ticker} prices in cache..')
        now = datetime.datetime.now()
        timestamp = '{}{}{}'.format(now.month, now.day, now.year)
        buffer_store= os.path.join(settings.CACHE_DIR, f'{timestamp}_{ticker}.{settings.CACHE_EXT}')
        
        if os.path.isfile(buffer_store):
            output.debug(f'Loading in cached {ticker} prices...')
            with open(buffer_store, 'r') as infile:
                if settings.CACHE_EXT == "json":
                    output.debug(f'Cached {ticker} prices found.')
                    prices = json.load(infile)
                # TODO: load other file types
            return prices
        else:
            output.debug(f'Retrieving {ticker} prices from Service Manager...')  
            prices = query_service_for_daily_price_history(ticker=ticker)

            output.debug(f'Storing {ticker} price history in cache...')
            with open(buffer_store, 'w') as outfile:
                if settings.CACHE_EXT == "json":
                    json.dump(prices, outfile)
                # TODO: dump other file types
            return prices
    else:
        output.debug(f'No cached prices for date ranges past default. Passing to service call...')
        prices = query_service_for_daily_price_history(ticker=ticker, start_date=start_date, end_date=end_date)
        return prices

def get_daily_price_latest(ticker):
    if settings.PRICE_MANAGER == "alpha_vantage":
        asset_type = markets.get_asset_type(ticker)
        prices = get_daily_price_history(ticker)
        first_element = helper.get_first_json_key(prices)

        if asset_type == settings.ASSET_EQUITY:
            return prices[first_element][settings.AV_RES_EQUITY_CLOSE_PRICE]

        elif asset_type == settings.ASSET_CRYPTO:
            return prices[first_element][settings.AV_RES_CRYPTO_CLOSE_PRICE]
            
    else:
        output.debug("No PRICE_MANAGER set in .env file!")
        return None

def query_service_for_daily_stats_history(statistics, start_date=None, end_date=None):
    if settings.STAT_MANAGER == "quandl":
        stats = []
        
        for statistic in statistics:
            url = f'{settings.Q_URL}/{settings.PATH_Q_FRED}/{statistic}?{settings.PARAM_Q_KEY}={settings.Q_KEY}'
            query = ""
            
            if end_date is not None:
                end_string = helper.date_to_string(end_date)
                query += f'&{settings.PARAM_Q_END}={end_string}' 
                pass

            if start_date is not None:
                start_string = helper.date_to_string(start_date)
                query += f'&{settings.PARAM_Q_END}={end_string}'

            url += query
        
            response = requests.get(url).json()

            # TODO: test for error messages or API rate limits

            stats.append(response[settings.Q_FIRST_LAYER][settings.Q_SECOND_LAYER])

        return stats
    else:
        output.debug("No STAT_MANAGER set in .env file!")
        return None

def get_daily_stats_history(statistics):
    # TODO: implement caching for statistics
    return query_service_for_daily_stats_history(statistics)

def get_daily_stats_latest(statistics):
    if settings.STAT_MANAGER == "quandl":
        current_stats = []
        stats_history = get_daily_stats_history(statistics)

        for stat in stats_history:
            current_stats.append(stat[0][1])

        return current_stats

    else:
        output.debug("No STAT_MANAGER set in .env file!")
        return None

def init_static_data():
    if settings.INIT or \
        ((not os.path.isfile(settings.STATIC_ECON_FILE)) or \
            (not os.path.isfile(settings.STATIC_TICKERS_FILE)) or \
                (not os.path.isfile(settings.STATIC_CRYPTO_FILE))):

        output.info('Initializing static data. Please wait. This may take a moment...')
        output.info('NOTE: set LOG_LEVEL = "debug" for more output while you wait.')

        # Clear static folder if initializing, otherwise unnecessary
        if settings.INIT:
            output.debug('Initialzing because settings.INIT set to True')
            helper.clear_directory(settings.STATIC_DIR, retain=True, outdated_only=False)
        
        else:
            output.debug('Initializing because settings.STATIC_DIR directory is missing file(s)')

        # Initialize Static Price Data
        if settings.PRICE_MANAGER == "alpha_vantage": 

            # grab ticker symbols and store in STATIC_DIR
            if not os.path.isfile(settings.STATIC_TICKERS_FILE):
                output.debug(f'Missing {settings.STATIC_TICKERS_FILE}, querying \'{settings.PRICE_MANAGER}\'...')

                query=f'{settings.PARAM_AV_FUNC}={settings.ARG_AV_FUNC_EQUITY_LISTINGS}'
                url = f'{settings.AV_URL}?{query}&{settings.PARAM_AV_KEY}={settings.AV_KEY}'

                output.debug(f'Preparsing to parse \'{settings.PRICE_MANAGER}\' Response to query: {query}')
                helper.parse_csv_response_column(column=0, url=url, firstRowHeader=settings.AV_RES_EQUITY_KEY, 
                                                    savefile=settings.STATIC_TICKERS_FILE, filetype=settings.STATIC_EXT)

            # grab crypto symbols and store in STATIC_DIR
            if not os.path.isfile(settings.STATIC_CRYPTO_FILE):
                output.debug(f'Missing {settings.STATIC_CRYPTO_FILE}, querying \'{settings.PRICE_MANAGER}\'.')
                url = settings.AV_CRYPTO_LIST

                output.debug(f'Preparsing to parse \'{settings.PRICE_MANAGER}\' Response to query: {url}')
                helper.parse_csv_response_column(column=0, url=url, firstRowHeader=settings.AV_RES_CRYPTO_KEY, 
                                                    savefile=settings.STATIC_CRYPTO_FILE, filetype=settings.STATIC_EXT)

        else:
            output.debug("No PRICE_MANAGER set in .env file!")

        # Initialize Static Statistic Data
        if settings.STAT_MANAGER == "quandl":
            
            # grab econominc indicator symbols and store in STATIC_DIR
            if not os.path.isfile(settings.STATIC_ECON_FILE):
                output.debug(f'Missing {settings.STATIC_ECON_FILE}, querying \'{settings.STAT_MANAGER}\'...')

                query = f'{settings.PATH_Q_FRED}/{settings.PARAM_Q_METADATA}'
                url = f'{settings.Q_META_URL}/{query}?{settings.PARAM_Q_KEY}={settings.Q_KEY}'

                output.debug(f'Preparsing to parse \'{settings.PRICE_MANAGER}\' Response to query: {query}')
                helper.parse_csv_response_column(column=0, url=url, firstRowHeader=settings.Q_RES_STAT_KEY,
                                                    savefile=settings.STATIC_ECON_FILE, filetype=settings.STATIC_EXT,
                                                    zipped=settings.Q_RES_STAT_ZIP_KEY)

        else:
            output.debug("No STAT_MANAGER set in .env file!")
    else:
        output.debug('Static data already initialized!')

def get_static_data(static_type):
    output.debug(f'Loading in cached {static_type} symbols...')
    path = None

    if static_type == settings.ASSET_CRYPTO:
        path = settings.STATIC_CRYPTO_FILE
    
    elif static_type == settings.ASSET_EQUITY:
        path = settings.STATIC_TICKERS_FILE
    
    elif static_type == settings.STAT_ECON:
        path = settings.STATIC_ECON_FILE
    
    else:
        return False

    if path is not None:
        if not os.path.isfile(path):
            init_static_data()

        with open(path, 'r') as infile:
            symbols = json.load(infile)   
            return symbols
    else:
        return False