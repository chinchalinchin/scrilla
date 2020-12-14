import os, sys, json
import app.utilities as utilities
import requests
import numpy
import time

def retrieve_stock_data(ticker):
    output = utilities.Logger('app.pyfin.retrieve_stock_data')

    buffer_store= os.path.join(utilities.BUFFER_DIR, f'{ticker}.json')
    # check if price history exists in cache
    if os.path.isfile(buffer_store):
        output.debug(f'Loading in cached prices...')
        with open(buffer_store, 'r') as infile:
            prices = json.load(infile)

    # retrieve prices from external source
    else:     
        output.debug(f'Retrieving prices from AlphaVantage query...')
        url=f'{utilities.QUERY_URL}={ticker}'     
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

        # save prices to cache for quick access
        dump_file = os.path.join(utilities.BUFFER_DIR,f'{ticker}.json')
        output.debug(f'Storing {ticker} price history in cache...')
        with open(dump_file, 'w') as outfile:
            json.dump(prices, outfile)

    return prices

# NOTE: AlphaVantage returns price history fom latest to earliest date.
def calculate_risk_return(ticker, input_prices=None):
    output = utilities.Logger('app.pyfin.calculate_statistics')

    # check if results exist in buffer directory
    buffer_store= os.path.join(utilities.BUFFER_DIR, f'{ticker}_statistics.json')
    if os.path.isfile(buffer_store):
        with open(buffer_store, 'r') as infile:
            results = json.load(infile)
    else:
        # check if prices have been passed in as an argument
        if input_prices is None:
            prices = retrieve_stock_data(ticker)
            if not prices:
                return False
        else: 
            prices = input_prices

        sample = len(prices)

        # calculate mean annual return
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
        # output.log(f'{ticker} \u03BC', mean_return)


        # calculate sample annual volatility
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

        # Store results in buffer for quick access
        dump_file = os.path.join(utilities.BUFFER_DIR,f'{ticker}_statistics.json')
        with open(dump_file, 'w') as outfile:
            json.dump(results, outfile)
    
    return results

def calculate_correlation(ticker_1, ticker_2):
    buffer_store_1= os.path.join(utilities.BUFFER_DIR, f'{ticker_1}_{ticker_2}_correlation.json')
    buffer_store_2= os.path.join(utilities.BUFFER_DIR, f'{ticker_2}_{ticker_1}_correlation.json')

    # check if results exist in cache location 1
    if os.path.isfile(buffer_store_1):
        with open(buffer_store_1, 'r') as infile:
            results = json.load(infile)
            correlattion = results['correlation']

    # check if results exist in cache location 2
    elif os.path.isfile(buffer_store_2):
        with open(buffer_store_2, 'r') as infile:
            results = json.load(infile)
            correlattion = results['correlation']

    # calculate results from sample
    else:
        prices_1 = retrieve_stock_data(ticker_1)
        prices_2 = retrieve_stock_data(ticker_2)
        if not (prices_1 and prices_2):
            return False 
        
        stats_1 = calculate_risk_return(ticker_1, prices_1)
        stats_2 = calculate_risk_return(ticker_2, prices_2)

        mod_mean_1 = stats_1['annual_return']*numpy.sqrt(utilities.ONE_TRADING_DAY)
        mod_mean_2 = stats_2['annual_return']*numpy.sqrt(utilities.ONE_TRADING_DAY)

        # calculate correlation
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

        # output.log(f'covar_({ticker_1}, {ticker_2})', covariance)
        # output.log(f'\u03A1_({ticker_1}, {ticker_2})', correlation)

        result = { 'correlation': correlation }

        dump_file = os.path.join(utilities.BUFFER_DIR,f'{ticker_1}_{ticker_2}_correlation.json')
        with open(dump_file, 'w') as outfile:
            json.dump(result, outfile)

    return result