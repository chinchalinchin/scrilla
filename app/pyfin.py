import os, sys, json, datetime
import dotenv
import requests
import numpy

APP_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BUFFER_DIR = os.path.join(APP_DIR, 'data')
ENV = dotenv.load_dotenv(os.path.join(APP_DIR,'.env'))
QUERY_URL = os.getenv('AV_QUERY_URL')
ONE_TRADING_DAY=(1/252)


def retrieve_stock_data(ticker):
    log(f'Retrieving {ticker} Price History...', 'pyfin.retrieve_stock_data')
    url=f'{QUERY_URL}={ticker}'
    prices = requests.get(url).json()
    prices = prices['Time Series (Daily)']
    dump_file = os.path.join(BUFFER_DIR,f'{ticker}.json')
    with open(dump_file, 'w') as outfile:
      json.dump(prices, outfile)
    return prices

# AlphaVantage returns stock data from latest to earliest. Need to skip
# first iteration of loop and then use the previous value as the numerator
# of the log. This is why the loop is confusing.
def calculate_statistics(ticker):
    prices = retrieve_stock_data(ticker)
    sample = len(prices)
    log(f'Last {sample} Days Of {ticker} Prices Retrieved', 'pyfin.calculate_statistics')

    log(f'Calculating {ticker} Annualized Return In The Given Period...', 'pyfin.calculate_statistics')
    # RETURN CALCULATION
    i = 0 
    mean_return = 0
    tomorrows_price = 0
    for price in prices:
        todays_price = prices[price]['4. close']
        if i != 0:
            daily_return = numpy.log(float(tomorrows_price)/float(todays_price))/ONE_TRADING_DAY
            mean_return = mean_return + daily_return/sample 
        tomorrows_price = prices[price]['4. close']
        i += 1
    log(f'{ticker} Annualized Return = {mean_return}', 'pyfin.calculate_statistics')


    log(f'Calculating {ticker} Annualized Volatility In The Given Period...', 'pyfin.calculate_statistics')
    # VOLATILITY CALCULATION
    i = 0
    mean_mod_return = mean_return*numpy.sqrt(ONE_TRADING_DAY)
    variance = 0
    tomorrows_price = 0
    for price in prices:
        todays_price = prices[price]['4. close']
        if i != 0:
            current_mod_return= numpy.log(float(tomorrows_price)/float(todays_price))/numpy.sqrt(ONE_TRADING_DAY) 
            variance = variance + (current_mod_return - mean_mod_return)**2/(sample - 1)
        tomorrows_price = prices[price]['4. close']
        i += 1
    volatility = numpy.sqrt(variance)

    results = {
        'annual_return': mean_return,
        'annual_volatility': volatility
    }
    log(f'{ticker} Annualized Volatility = {volatility}', 'pyfin.calculate_statistics')
    
    return results


def log(msg, function):
    now = datetime.datetime.now()
    print(now, ' :' , function, ' : ',msg)

if __name__ == "__main__": 
    args = sys.argv
    for arg in args[1:]:
        log(f'Calculating {arg} Statistics', 'pyfin.main')
        calculate_statistics(arg)