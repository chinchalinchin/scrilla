import time
import requests

import app.settings as settings

import util.logger as logger

output = logger.Logger("app.services")

def get_price_history(ticker):
    if settings.PRICE_MANAGER == "alpha_vantage":
        url=f'{settings.AV_QUERY_URL}={ticker}'     
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

        prices = prices['Time Series (Daily)']
        return prices