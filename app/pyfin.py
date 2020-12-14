import os, sys, json
import util
import requests
import numpy
import time

def retrieve_stock_data(ticker):
    debug = util.Logger('app.pyfin.retrieve_stock_data')

    debug.log(f'Retrieving {ticker} Price History...')
    url=f'{util.QUERY_URL}={ticker}'
    prices = requests.get(url).json()
    while list(prices.keys())[0] == 'Note':
        time.sleep(10)
        prices = requests.get(url).json()

    prices = prices['Time Series (Daily)']
    dump_file = os.path.join(util.BUFFER_DIR,f'{ticker}.json')
    with open(dump_file, 'w') as outfile:
      json.dump(prices, outfile)
    return prices

# NOTE: AlphaVantage returns prices from latest to earliest
def calculate_statistics(ticker):
    debug = util.Logger('app.pyfin.calculate_statistics')

    prices = retrieve_stock_data(ticker)
    sample = len(prices)
    debug.log(f'Last {sample} Days Of {ticker} Prices Retrieved')

    debug.log(f'Calculating {ticker} Annualized Return In The Given Period...')
    # RETURN CALCULATION
    i = 0 
    mean_return = 0
    tomorrows_price = 0
    for price in prices:
        todays_price = prices[price]['4. close']
        if i != 0:
            daily_return = numpy.log(float(tomorrows_price)/float(todays_price))/util.ONE_TRADING_DAY
            mean_return = mean_return + daily_return/sample 
        tomorrows_price = prices[price]['4. close']
        i += 1
    debug.log(f'{ticker} Annualized Return = {mean_return}')


    debug.log(f'Calculating {ticker} Annualized Volatility In The Given Period...')
    # VOLATILITY CALCULATION
    i = 0
    mean_mod_return = mean_return*numpy.sqrt(util.ONE_TRADING_DAY)
    variance = 0
    tomorrows_price = 0
    for price in prices:
        todays_price = prices[price]['4. close']
        if i != 0:
            current_mod_return= numpy.log(float(tomorrows_price)/float(todays_price))/numpy.sqrt(util.ONE_TRADING_DAY) 
            variance = variance + (current_mod_return - mean_mod_return)**2/(sample - 1)
        tomorrows_price = prices[price]['4. close']
        i += 1
    volatility = numpy.sqrt(variance)
    results = {
        'annual_return': mean_return,
        'annual_volatility': volatility
    }
    debug.log(f'{ticker} Annualized Volatility = {volatility}')
    
    return results

def calculate_covariance(ticker_1, ticker_2):
    prices_1 = retrieve_stock_data(ticker_1)
    prices_2 = retrieve_stock_data(ticker_2)

if __name__ == "__main__": 
    debug = util.Logger('app.pyfin.main')

    args = sys.argv
    for arg in args[1:]:
        debug.log(f'Calculating {arg} Statistics')
        calculate_statistics(arg)