import os, csv, json
import itertools
import datetime, time
import requests

import app.settings as settings
import app.markets as markets

import util.logger as logger
import util.helper as helper

output = logger.Logger("app.services")

# Arguments: tickers -> [string]
#            startdate -> datetime.date
#            enddate -> datetime.date
    # TODO: don't cache stats if start_date and end_date are specified
def retrieve_prices_from_cache(ticker, start_date=None, end_date=None):
    now = datetime.datetime.now()
    # TODO: if startdate and enddate are supplied need to change timestamp
    timestamp = '{}{}{}'.format(now.month, now.day, now.year)
    buffer_store= os.path.join(settings.CACHE_DIR, f'{timestamp}_{ticker}.json')
    
    if os.path.isfile(buffer_store):
        output.debug(f'Loading in cached {ticker} prices...')
        with open(buffer_store, 'r') as infile:
            prices = json.load(infile)

    else:     
        output.debug(f'Retrieving {ticker} prices from Service Manager...')  
        prices = get_daily_price_history(ticker=ticker, startdate=start_date, enddate=end_date)

        output.debug(f'Storing {ticker} price history in cache...')
        with open(buffer_store, 'w') as outfile:
            json.dump(prices, outfile)

    return prices

# TODO: test api keys here
def test_api_keys():
    return True

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

            url=f'{settings.AV_URL}?{query}'     
  
            # NOTE: can probably move all of this below outside of the current conditional and apply all the 
            #   conditional logic to the url, so this stuff needs to be done just once.
            prices = requests.get(url).json()
           
            # check for bad response
            first_element = helper.get_first_json_key(prices)

            if first_element == 'Error Message':
                output.debug(prices['Error Message'])
                return False

            # check for API rate limit 
            while first_element == 'Note':
                output.debug(f'Waiting for AlphaVantage rate limit to refresh...')
                time.sleep(10)
                prices = requests.get(url).json()
                first_element = helper.get_first_json_key(prices)

            if asset_type == settings.ASSET_EQUITY:
                return prices[settings.AV_RES_EQUITY_FIRST_LAYER]

            elif asset_type == settings.ASSET_CRYPTO:
                truncated_prices, index = {}, 0
                for date in prices[settings.AV_RES_CRYPTO_FIRST_LAYER]:
                    if index < 100:
                        truncated_prices[date] = prices[settings.AV_RES_CRYPTO_FIRST_LAYER][date]
                    else:
                        return truncated_prices
                    index += 1
                # NOTE: AlphaVantage returns entire history for any crypto API call
                # unlike the equity API calls, so the response for crypto is truncated
                # to make sure responses for current calculations are of the same length.

        else:
            if start_date is not None and end_date is not None:
                # TODO
                pass

            elif start_date is None and end_date is not None:
                # TODO
                pass

            elif start_date is not None and end_date is None:
                # TODO
                pass

            else:
                # TODO
                pass
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
            
                response = requests.get(url).json()

                stats.append(response[settings.Q_FIRST_LAYER][settings.Q_SECOND_LAYER])

            elif startdate is None and enddate is not None:
                # TODO
                pass

            elif startdate is not None and enddate is None:
                # TODO
                pass

            else:
                # TODO
                pass
        
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
            helper.clear_dir(settings.STATIC_DIR, retain=True)
        
        else:
            output.debug('Initializing because settings.STATIC_DIR directory is missing file(s)')

        # Initialize Static Price Data
        if settings.PRICE_MANAGER == "alpha_vantage": 

            # grab ticker symbols and store in STATIC_DIR
            if not os.path.isfile(settings.STATIC_TICKERS_FILE):
                output.debug(f'Missing {settings.STATIC_TICKERS_FILE}, querying AlphaVantage...')

                query=f'{settings.PARAM_AV_FUNC}={settings.ARG_AV_FUNC_EQUITY_LISTINGS}&{settings.PARAM_AV_KEY}={settings.AV_KEY}'
                url = f'{settings.AV_URL}?{query}'

                output.debug(f'Preparsing to parse AlphaVantage Response to query: {query}')
                helper.parse_csv_response_column(column=0, url=url, firstRowHeader=settings.AV_RES_EQUITY_KEY, 
                                                    savefile=settings.STATIC_TICKERS_FILE)

            # grab crypto symbols and store in STATIC_DIR
            if not os.path.isfile(settings.STATIC_CRYPTO_FILE):
                output.debug(f'Missing {settings.STATIC_CRYPTO_FILE}, querying AlphaVantage...')
                url = settings.AV_CRYPTO_LIST

                output.debug(f'Preparsing to parse AlphaVantage Response to query: {url}')
                helper.parse_csv_response_column(column=0, url=url, firstRowHeader=settings.AV_RES_CRYPTO_KEY, 
                                                    savefile=settings.STATIC_CRYPTO_FILE)

        else:
            output.debug("No PRICE_MANAGER set in .env file!")

        # Initialize Static Statistic Data
        if settings.STAT_MANAGER == "quandl":
            
            # grab econominc indicator symbols and store in STATIC_DIR
            if not os.path.isfile(settings.STATIC_ECON_FILE):
                output.debug(f'Missing {settings.STATIC_ECON_FILE}, querying Quandl...')

                url = f'{settings.Q_META_URL}/{settings.PATH_Q_FRED}/{settings.PARAM_Q_METADATA}?{settings.PARAM_Q_KEY}={settings.Q_KEY}'

                helper.parse_csv_response_column(column=0, url=url, firstRowHeader=settings.Q_RES_STAT_KEY,
                                                    savefile=settings.STATIC_ECON_FILE, zipped=settings.Q_RES_STAT_ZIP_KEY)

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