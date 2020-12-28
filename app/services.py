import os, csv, json
import datetime, time
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

def get_daily_price_history(ticker, asset, current=True, startdate=None, enddate=None):
    if settings.PRICE_MANAGER == "alpha_vantage":
        if current:
            query = f'{settings.PARAM_AV_TICKER}={ticker}&{settings.PARAM_AV_KEY}={settings.AV_KEY}'

            if asset == settings.ASSET_EQUITY:
                query += f'&{settings.PARAM_AV_FUNC}={settings.ARG_AV_FUNC_EQUITY_DAILY}'

            elif asset == settings.ASSET_CRYPTO:
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

            if asset == settings.ASSET_EQUITY:
                return prices[settings.AV_RES_EQUITY_FIRST_LAYER]
            elif asset == settings.ASSET_CRYPTO:
                return prices[settings.AV_RES_CRYPTO_FIRST_LAYER]

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
    else:
            output.debug("No STAT_MANAGER set in .env file!")

def get_daily_price_latest(ticker, asset):
    if settings.PRICE_MANAGER == "alpha_vantage":
        prices = get_daily_price_history(ticker, asset)
        first_element = helper.get_first_json_key(prices)
        if asset == settings.ASSET_EQUITY:
            return prices[first_element][settings.AV_RES_EQUITY_CLOSE_PRICE]
        elif asset == settings.ASSET_CRYPTO:
            return prices[first_element][settings.AV_RES_CRYPTO_CLOSE_PRICE]
    else:
        output.debug("No PRICE_MANAGER set in .env file!")
        return None

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

# TODO
def init_static_data():
    
    if settings.INIT or \
        ((not os.path.isfile(settings.STATIC_ECON_FILE)) or \
            (not os.path.isfile(settings.STATIC_TICKERS_FILE)) or \
                (not os.path.isfile(settings.STATIC_CRYPTOFILE))):

        # Clear static folder is initializing, otherwise unnecessary
        if settings.INIT:
            helper.clear_static()

        # Initialize Static Price Data
        if settings.PRICE_MANAGER == "alpha_vantage": 
            # grab ticker symbols and store in STATIC_DIR
            query=f'{settings.PARAM_AV_FUNC}={settings.ARG_AV_FUNC_EQUITY_LISTINGS}&{settings.PARAM_AV_KEY}={settings.AV_KEY}'
            url = f'{settings.AV_URL}?{query}'

            with requests.Session() as s:
                download = s.get(url)
                decoded_content = download.content.decode('utf-8')
                cr = csv.reader(decoded_content.splitlines(), delimiter=',')
                
                tickers = []
                for row in cr:
                    if row[0] != settings.AV_RES_EQUITY_KEY:
                        tickers.append(row[0])

                with open(settings.STATIC_TICKERS_FILE, 'w') as outfile:
                    json.dump(tickers, outfile)
                
                s.close()

            # grab crypto symbols and store in STATIC_DIR
            url = settings.AV_CRYPTO_LIST

            with requests.Session() as s:
                download = s.get(url)
                decoded_content = download.content.decode('utf-8')
                cr = csv.reader(decoded_content.splitlines(), delimiter=',')
                
                crypto = []
                for row in cr:
                    if row[0] != settings.AV_RES_CRYPTO_KEY:
                        crypto.append(row[0])
                
                with open(settings.STATIC_CRYPTO_FILE, 'w') as outfile:
                    json.dump(crypto, outfile)
                
                s.close()

        else:
            output.debug("No PRICE_MANAGER set in .env file!")

        # Initialize Static Statistic Data
        if settings.STAT_MANAGER == "quandl":
            pass

        else:
            output.debug("No STAT_MANAGER set in .env file!")

# TODO
def get_static_data(type):
    # grab type from STATIC_DIR
    pass