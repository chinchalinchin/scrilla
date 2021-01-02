import os, csv, json
import itertools
import datetime, time
import requests

import app.settings as settings
import app.markets as markets

import util.logger as logger
import util.helper as helper

output = logger.Logger("app.services")

def parse_price_from_date(prices, date, asset_type):
    try:
        if asset_type == settings.ASSET_EQUITY:
            return prices[date][settings.AV_RES_EQUITY_CLOSE_PRICE]
        elif asset_type == settings.ASSET_CRYPTO:
            return prices[date][settings.AV_RES_CRYPTO_CLOSE_PRICE]
    except:
        return False
        
# ARGUMENTS: 
#            tickers : [ string ] : list of symbols whose prices will be retrieved
#            start_date : datetime.date : start of time period 
#            end_date : datetime.date : end of time period
#
# NOTE: Only recent prices are cached, i.e. the last 100 days of prices. Calls
# for other periods of time are not cached and will take longer to load due to 
# the API rate limit from AlphaVantage.
def retrieve_prices_from_cache(ticker, start_date=None, end_date=None):
    buffer_flag = (start_date is None and end_date is None)

    if buffer_flag:
        now = datetime.datetime.now()
        timestamp = '{}{}{}'.format(now.month, now.day, now.year)
        buffer_store= os.path.join(settings.CACHE_DIR, f'{timestamp}_{ticker}.{settings.CACHE_EXT}')
        
        if os.path.isfile(buffer_store):
            output.debug(f'Loading in cached {ticker} prices...')
            with open(buffer_store, 'r') as infile:
                if settings.CACHE_EXT == "json":
                    prices = json.load(infile)
            return prices
    
    output.debug(f'Retrieving {ticker} prices from Service Manager...')  
    prices = get_daily_price_history(ticker=ticker, startdate=start_date, enddate=end_date)

    if buffer_flag:
        output.debug(f'Storing {ticker} price history in cache...')
        with open(buffer_store, 'w') as outfile:
            if settings.CACHE_EXT == "json":
                json.dump(prices, outfile)

    return prices

# Note, by default, AlphaVantage returns last 100 days of prices for equities, while returning the 
# entire price history for crypto assets by default. By default, this method will return the last 
# 100 days of prices for any type of asset provided to the input 'ticker'. 
#
# TODO: Implement 'startdate' and 'enddate' features
# Arguments: startdate -> datetime.date
#             enddate -> datetime.date
def get_daily_price_history(ticker, start_date=None, end_date=None):
    asset_type=markets.get_asset_type(ticker)  

    if settings.PRICE_MANAGER == "alpha_vantage":
        # Retrieve last 100 days of closing prices
        if start_date is None and end_date is None:
            query = f'{settings.PARAM_AV_TICKER}={ticker}&{settings.PARAM_AV_KEY}={settings.AV_KEY}'

            if asset_type == settings.ASSET_EQUITY:
                query += f'&{settings.PARAM_AV_FUNC}={settings.ARG_AV_FUNC_EQUITY_DAILY}'

            elif asset_type == settings.ASSET_CRYPTO:
                query += f'&{settings.PARAM_AV_FUNC}={settings.ARG_AV_FUNC_CRYPTO_DAILY}&{settings.PARAM_AV_DENOM}={settings.DENOMINATION}'

            else:
                return False

        elif start_date is not None and end_date is not None:
            if asset_type == settings.ASSET_EQUITY:
                # TODO
                pass
            elif asset_type == settings.ASSET_CRYPTO:
                # TODO
                pass

        elif start_date is None and end_date is not None:
            if asset_type == settings.ASSET_EQUITY:
                # TODO
                pass
            elif asset_type == settings.ASSET_CRYPTO:
                # TODO
                pass

        # if start_date is not None and end_date is None
        else:
            if asset_type == settings.ASSET_EQUITY:
                # TODO
                pass
            elif asset_type == settings.ASSET_CRYPTO:
                # TODO
                pass

        url=f'{settings.AV_URL}?{query}'     

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

        if asset_type == settings.ASSET_EQUITY:
            return prices[settings.AV_RES_EQUITY_FIRST_LAYER]

        elif asset_type == settings.ASSET_CRYPTO:
            truncated_prices, index = {}, 0
            if start_date is None and end_date is None:
                for date in prices[settings.AV_RES_CRYPTO_FIRST_LAYER]:
                    if index < 100:
                        truncated_prices[date] = prices[settings.AV_RES_CRYPTO_FIRST_LAYER][date]
                    else:
                        return truncated_prices
                    index += 1
            else:
                return prices[settings.AV_RES_CRYPTO_FIRST_LAYER]
            # NOTE: AlphaVantage returns entire history for any crypto API call
            # unlike the equity API calls, so the response for crypto is truncated
            # to make sure responses for current calculations are of the same length.

    else:
            output.debug("No STAT_MANAGER set in .env file!")

def get_daily_price_latest(ticker):
    if settings.PRICE_MANAGER == "alpha_vantage":
        asset_type = markets.get_asset_type(ticker)
        prices = retrieve_prices_from_cache(ticker)
        first_element = helper.get_first_json_key(prices)

        if asset_type == settings.ASSET_EQUITY:
            return prices[first_element][settings.AV_RES_EQUITY_CLOSE_PRICE]

        elif asset_type == settings.ASSET_CRYPTO:
            return prices[first_element][settings.AV_RES_CRYPTO_CLOSE_PRICE]
            
    else:
        output.debug("No PRICE_MANAGER set in .env file!")
        return None

def get_daily_stats_history(statistics, startdate=None, enddate=None):
    if settings.STAT_MANAGER == "quandl":
        stats = []
        
        for statistic in statistics:
            if startdate is None and enddate is None:
                url = f'{settings.Q_URL}/{settings.PATH_Q_FRED}/{statistic}?{settings.PARAM_Q_KEY}={settings.Q_KEY}'
            
            elif startdate is None and enddate is not None:
                # TODO
                pass

            elif startdate is not None and enddate is None:
                # TODO
                pass

            else:
                # TODO
                pass
        
            response = requests.get(url).json()

            # TODO: test for error messages or API rate limits

            stats.append(response[settings.Q_FIRST_LAYER][settings.Q_SECOND_LAYER])

        return stats
    else:
        output.debug("No STAT_MANAGER set in .env file!")
        return None
        
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

        output.comment('Initializing Static Data. Please wait. This may take a moment...')
        output.comment('NOTE: set DEBUG = True for more output while you wait.')

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

def get_static_data(static_type):
    output.debug(f'Loading in cached {static_type} symbols...')
    path = ""

    if static_type == settings.ASSET_CRYPTO:
        path = settings.STATIC_CRYPTO_FILE
    
    elif static_type == settings.ASSET_EQUITY:
        path = settings.STATIC_TICKERS_FILE
    
    elif static_type == settings.STAT_ECON:
        path = settings.STATIC_ECON_FILE
    
    else:
        return False

    if not os.path.isfile(path):
        init_static_data()

    with open(path, 'r') as infile:
        symbols = json.load(infile)   
    
    return symbols