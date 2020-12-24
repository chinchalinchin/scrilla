import time
import requests

import app.settings as settings

import util.logger as logger

output = logger.Logger("app.services")

# need current flag 
def get_daily_price_history(ticker, current=True, startdate=None, enddate=None):
    if settings.PRICE_MANAGER == "alpha_vantage":
        if current:
            query = f'{settings.PARAM_TICKER}={ticker}&{settings.PARAM_FUNC}={settings.ARG_FUNC_DAILY}&{settings.PARAM_AV_KEY}={settings.AV_KEY}'
            url=f'{settings.AV_URL}?{query}'     
           
            prices = requests.get(url).json()

            # check for bad response
            if list(prices.keys())[0] == 'Error Message':
                output.debug(prices['Error Message'])
                return False

            # check for API rate limit 
            while list(prices.keys())[0] == 'Note':
                output.debug(f'Waiting for AlphaVantage rate limit to refresh...')
                time.sleep(10)
                prices = requests.get(url).json()

            return prices[settings.AV_FIRST_LAYER]
        
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

def get_daily_price_latest(ticker):
    if settings.PRICE_MANAGER == "alpha_vantage":
        prices = get_daily_price_history(ticker)
        return prices[0][settings.CLOSE_PRICE]

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