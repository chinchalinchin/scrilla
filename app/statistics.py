import os, sys, json
import utilities
import requests
import numpy
import time

def retrieve_stock_data(ticker):
    debug = utilities.Logger('app.pyfin.retrieve_stock_data')

    debug.log(f'Retrieving {ticker} Price History...')
    url=f'{utilities.QUERY_URL}={ticker}'
    prices = requests.get(url).json()
    while list(prices.keys())[0] == 'Note':
        debug.log('Waiting For AlphaVantage API Rate Limit To Reset...')
        time.sleep(10)
        prices = requests.get(url).json()

    prices = prices['Time Series (Daily)']
    dump_file = os.path.join(utilities.BUFFER_DIR,f'{ticker}.json')
    with open(dump_file, 'w') as outfile:
      json.dump(prices, outfile)
    return prices

# NOTE: AlphaVantage returns price history fom latest to earliest date.
def calculate_risk_return(ticker, preloaded_prices=None):
    debug = utilities.Logger('app.pyfin.calculate_statistics')
    if preloaded_prices is None:
        prices = retrieve_stock_data(ticker)
    else: 
        prices = preloaded_prices

    sample = len(prices)
    debug.log(f'Last {sample} Days Of {ticker} Prices Retrieved')

    debug.log(f'Calculating {ticker} Annualized Return In The Given Period...')
    # RETURN CALCULATION
    i = 0 
    mean_return = 0
    tomorrows_price = 0
    for date in prices:
        todays_price = prices[date]['4. close']
        if i != 0:
            daily_return = numpy.log(float(tomorrows_price)/float(todays_price))/utilities.ONE_TRADING_DAY
            mean_return = mean_return + daily_return/sample 
        tomorrows_price = prices[date]['4. close']
        i += 1
    debug.log(f'{ticker} Annualized Return = {mean_return}')


    debug.log(f'Calculating {ticker} Annualized Volatility In The Given Period...')
    # VOLATILITY CALCULATION
    i = 0
    mean_mod_return = mean_return*numpy.sqrt(utilities.ONE_TRADING_DAY)
    variance = 0
    tomorrows_price = 0
    for date in prices:
        todays_price = prices[date]['4. close']
        if i != 0:
            current_mod_return= numpy.log(float(tomorrows_price)/float(todays_price))/numpy.sqrt(utilities.ONE_TRADING_DAY) 
            variance = variance + (current_mod_return - mean_mod_return)**2/(sample - 1)
        tomorrows_price = prices[date]['4. close']
        i += 1
    volatility = numpy.sqrt(variance)
    results = {
        'annual_return': mean_return,
        'annual_volatility': volatility
    }

    dump_file = os.path.join(utilities.BUFFER_DIR,f'{ticker}_statistics.json')
    with open(dump_file, 'w') as outfile:
      json.dump(results, outfile)
    debug.log(f'{ticker} Annualized Volatility = {volatility}')
    
    return results

def calculate_correlation(ticker_1, ticker_2):
    prices_1 = retrieve_stock_data(ticker_1)
    prices_2 = retrieve_stock_data(ticker_2)
    
    stats_1 = calculate_risk_return(ticker_1, prices_1)
    stats_2 = calculate_risk_return(ticker_2, prices_2)

    mod_mean_1 = stats_1['annual_return']*numpy.sqrt(utilities.ONE_TRADING_DAY)
    mod_mean_2 = stats_2['annual_return']*numpy.sqrt(utilities.ONE_TRADING_DAY)

    # CORRELATION CALCULATION
    i = 0 
    covariance = 0
    tomorrows_price_1 = 0
    tomorrows_price_2 = 0
    if len(prices_1) == len(prices_2) or len(prices_1) < len(prices_2):
        sample_prices = prices_1
    else:
        sample_prices = prices_2
  
    sample = len(sample_prices)
    for date in sample_prices:
            todays_price_1 = prices_1[date]['4. close']
            todays_price_2 = prices_2[date]['4. close']
            if i != 0:
                current_mod_return_1= numpy.log(float(tomorrows_price_1)/float(todays_price_1))/numpy.sqrt(utilities.ONE_TRADING_DAY) 
                current_mod_return_2= numpy.log(float(tomorrows_price_2)/float(todays_price_2))/numpy.sqrt(utilities.ONE_TRADING_DAY) 

                covariance = covariance + (current_mod_return_1 - mod_mean_1)*(current_mod_return_2 - mod_mean_2)/(sample - 1)
            tomorrows_price_1 = prices_1[date]['4. close']
            tomorrows_price_2 = prices_2[date]['4. close']
            i += 1

    correlation = covariance/ (stats_1['annual_volatility']*stats_2['annual_volatility'])

    debug.log(f'({ticker_1}, {ticker_2}) Annualized Covariance = {covariance}')
    debug.log(f'({ticker_1}, {ticker_2}) Annualized Correlation = {correlation}')

    results = {
        'correlation': correlation
    }

    dump_file = os.path.join(utilities.BUFFER_DIR,f'{ticker_1}_{ticker_2}_correlation.json')
    with open(dump_file, 'w') as outfile:
      json.dump(results, outfile)

    return correlation

if __name__ == "__main__": 
    debug = utilities.Logger('app.pyfin.main')

    args = sys.argv
    calculate_correlation(args[1], args[2])
    # for arg in args[1:]:
       # debug.log(f'Calculating {arg} Statistics')
        