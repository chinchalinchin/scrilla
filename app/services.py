import os, json, datetime, time
import requests

import app.settings as settings

import util.logger as logger
import util.helpers as helper

output = logger.Logger("app.services")

def retrieve_prices_from_cache_or_web(ticker, current=True):
    now = datetime.datetime.now()
    timestamp = '{}{}{}'.format(now.month, now.day, now.year)
    buffer_store= os.path.join(settings.CACHE_DIR, f'{timestamp}_{ticker}.json')
    
    if os.path.isfile(buffer_store):
        output.debug(f'Loading in cached {ticker} prices...')
        with open(buffer_store, 'r') as infile:
            prices = json.load(infile)

    else:     
        output.debug(f'Retrieving {ticker} prices from Service Manager...')    
        prices = get_daily_price_history(ticker=ticker, asset=settings.ASSET_EQUITY, current=current)

        output.debug(f'Storing {ticker} price history in cache...')
        with open(buffer_store, 'w') as outfile:
            json.dump(prices, outfile)

    return prices

# need current flag 
def get_daily_price_history(ticker, asset, current=True, startdate=None, enddate=None):
    if settings.PRICE_MANAGER == "alpha_vantage":
        if current:
            query = f'{settings.PARAM_TICKER}={ticker}&{settings.PARAM_AV_KEY}={settings.AV_KEY}'

            if asset == settings.ASSET_EQUITY:
                query += f'&{settings.PARAM_FUNC}={settings.ARG_FUNC_EQUITY_DAILY}'

            elif asset == settings.ASSET_CRYPTO:
                query += f'&{settings.PARAM_FUNC}={settings.ARG_FUNC_CRYPTO_DAILY}&{settings.PARAM_DENOM}={settings.DENOMINATION}'

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

            if asset == settings.ASSET_EQUITY:
                return prices[settings.AV_EQUITY_FIRST_LAYER]
            elif asset == settings.ASSET_CRYPTO:
                return prices[settings.AV_CRYPTO_FIRST_LAYER]

        else:
            if startdate is None and enddate is None:
                # TODO
                pass

            elif startdate is None and enddate is not None:
                # TODO
                pass

            elif startdate is not None and enddate is None:
                # TODO
                pass

            else:
                # TODO
                pass

def get_daily_price_latest(ticker, asset):
    if settings.PRICE_MANAGER == "alpha_vantage":
        prices = get_daily_price_history(ticker, asset)
        first_element = helper.get_first_json_key(prices)
        if asset == settings.ASSET_EQUITY:
            return prices[first_element][settings.AV_EQUITY_CLOSE_PRICE]
        elif asset == settings.ASSET_CRYPTO:
            return prices[first_element][settings.AV_CRYPTO_CLOSE_PRICE]

def get_daily_stats_history(statistics, startdate=None, enddate=None):
    if settings.STAT_MANAGER == "quandl":
        stats = []
        
        for statistic in statistics:
            
            if startdate is None and enddate is None:
                url = f'{settings.Q_URL}/{statistic}?{settings.PARAM_Q_KEY}={settings.Q_KEY}'
            
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
        
def get_daily_stats_latest(statistics):
    if settings.STAT_MANAGER == "quandl":
        current_stats = []
        stats_history = get_daily_stats_history(statistics)
        for stat in stats_history:
            current_stats.append(stat[0][1])
        return current_stats

# TODO
def init_static_data():
    # if static folder does not contain economic.json, ticker.json AND crypto.json 
    # OR settings.INIT:
        # grab economic indicator symbols and store in STATIC_DIR
        # grab ticker symbols and store in STATIC_DIR
        # grab crypto symbols and store in STATIC_DIR
        # return type.json
    pass

# TODO
def get_static_data(type):
    # grab type from STATIC_DIR
    pass