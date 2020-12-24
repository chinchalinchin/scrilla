import os, sys, json
import datetime
import numpy
from decimal import Decimal

import app.settings as settings
import app.services as services

import util.logger as logger

output = logger.Logger('app.statistics')

def retrieve_stock_data(ticker, current=True):
    now = datetime.datetime.now()
    timestamp = '{}{}{}'.format(now.month, now.day, now.year)
    buffer_store= os.path.join(settings.CACHE_DIR, f'{timestamp}_{ticker}.json')
    
    if os.path.isfile(buffer_store):
        output.debug(f'Loading in cached {ticker} prices...')
        with open(buffer_store, 'r') as infile:
            prices = json.load(infile)

    else:     
        output.debug(f'Retrieving {ticker} prices from Service Manager...')    
        prices = services.get_price_history(ticker, current)

        output.debug(f'Storing {ticker} price history in cache...')
        with open(buffer_store, 'w') as outfile:
            json.dump(prices, outfile)

    return prices

# NOTE: AlphaVantage returns price history from latest to earliest date.s
def calculate_moving_averages(tickers, current=True, enddate=None):
    moving_averages = []
    
    if current:
        for ticker in tickers:
            prices = retrieve_stock_data(ticker)
            count = 1
            MA_1, MA_2, MA_3 = 0, 0, 0
            
            for date in prices:
                price = prices[date][settings.CLOSE_PRICE]

                if count < settings.MA_1_PERIOD:
                    MA_1 += Decimal(price) / Decimal(settings.MA_1_PERIOD)
                    
                if count < settings.MA_2_PERIOD:
                    MA_2 += Decimal(price) / Decimal(settings.MA_2_PERIOD)

                if count < settings.MA_3_PERIOD:
                    MA_3 += Decimal(price) / Decimal(settings.MA_3_PERIOD)   
                count += 1
            moving_averages.append([MA_1, MA_2, MA_3])
        return moving_averages
    else:
        pass
        # TODO: need to pull entire price history from AlphaVantage

# NOTE: AlphaVantage returns price history from latest to earliest date.
def calculate_risk_return(ticker, input_prices=None):
    now = datetime.datetime.now()
    timestamp = '{}{}{}'.format(now.month, now.day, now.year)
    buffer_store= os.path.join(settings.CACHE_DIR, f'{timestamp}_{ticker}_statistics.json')

    if os.path.isfile(buffer_store):
        output.debug(f'Loading in cached {ticker} statistics...')
        with open(buffer_store, 'r') as infile:
            results = json.load(infile)
    else:
        if input_prices is None:
            prices = retrieve_stock_data(ticker)
            if not prices:
                return False
        else: 
            output.debug(f'Using inputted {ticker} prices for calculation...')
            prices = input_prices

        sample = len(prices)

        # calculate mean annual return
        i = 0 
        mean_return = 0
        tomorrows_price = 0
        for date in prices:
            todays_price = prices[date][settings.CLOSE_PRICE]
            if i != 0:
                daily_return = numpy.log(float(tomorrows_price)/float(todays_price))/settings.ONE_TRADING_DAY
                mean_return = mean_return + daily_return/sample 
            tomorrows_price = prices[date][settings.CLOSE_PRICE]
            i += 1

        # calculate sample annual volatility
        i = 0
        mean_mod_return = mean_return*numpy.sqrt(settings.ONE_TRADING_DAY)
        variance = 0
        tomorrows_price = 0
        for date in prices:
            todays_price = prices[date][settings.CLOSE_PRICE]
            if i != 0:
                current_mod_return= numpy.log(float(tomorrows_price)/float(todays_price))/numpy.sqrt(settings.ONE_TRADING_DAY) 
                variance = variance + (current_mod_return - mean_mod_return)**2/(sample - 1)
            tomorrows_price = prices[date][settings.CLOSE_PRICE]
            i += 1

        # adjust for output
        volatility = numpy.sqrt(variance)
        # ito's lemma
        mean_return = mean_return + 0.5*(volatility**2)
        
        results = {
            'annual_return': mean_return,
            'annual_volatility': volatility
        }

        # store results in buffer for quick access
        output.debug(f'Storing {ticker} statistics in cache...')
        with open(buffer_store, 'w') as outfile:
            json.dump(results, outfile)
    
    return results

def calculate_correlation(ticker_1, ticker_2):
    now = datetime.datetime.now()
    timestamp = '{}{}{}'.format(now.month, now.day, now.year)
    buffer_store_1= os.path.join(settings.CACHE_DIR, f'{timestamp}_{ticker_1}_{ticker_2}_correlation.json')
    buffer_store_2= os.path.join(settings.CACHE_DIR, f'{timestamp}_{ticker_2}_{ticker_1}_correlation.json')

    # check if results exist in cache location 1
    if os.path.isfile(buffer_store_1):
        output.debug(f'Loading in cached ({ticker_1}, {ticker_2}) correlation...')
        with open(buffer_store_1, 'r') as infile:
            results = json.load(infile)
            correlation = results['correlation']

    # check if results exist in cache location 2
    elif os.path.isfile(buffer_store_2):
        output.debug(f'Loading in cached ({ticker_1}, {ticker_2}) correlation...')
        with open(buffer_store_2, 'r') as infile:
            results = json.load(infile)
            correlation = results['correlation']

    # calculate results from sample
    else:
        prices_1 = retrieve_stock_data(ticker_1)
        prices_2 = retrieve_stock_data(ticker_2)
        if not (prices_1 and prices_2):
            return False 
        
        stats_1 = calculate_risk_return(ticker_1, prices_1)
        stats_2 = calculate_risk_return(ticker_2, prices_2)

        # ito's lemma
        mod_mean_1 = (stats_1['annual_return'] - 0.5*(stats_1['annual_volatility'])**2)*numpy.sqrt(settings.ONE_TRADING_DAY)
        mod_mean_2 = (stats_2['annual_return'] - 0.5*(stats_2['annual_volatility'])**2)*numpy.sqrt(settings.ONE_TRADING_DAY)

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
                todays_price_1 = prices_1[date][settings.CLOSE_PRICE]
                todays_price_2 = prices_2[date][settings.CLOSE_PRICE]
                if i != 0:
                    current_mod_return_1= numpy.log(float(tomorrows_price_1)/float(todays_price_1))/numpy.sqrt(settings.ONE_TRADING_DAY) 
                    current_mod_return_2= numpy.log(float(tomorrows_price_2)/float(todays_price_2))/numpy.sqrt(settings.ONE_TRADING_DAY) 
                    covariance = covariance + (current_mod_return_1 - mod_mean_1)*(current_mod_return_2 - mod_mean_2)/(sample - 1)
                tomorrows_price_1 = prices_1[date][settings.CLOSE_PRICE]
                tomorrows_price_2 = prices_2[date][settings.CLOSE_PRICE]
                i += 1

        correlation = covariance/(stats_1['annual_volatility']*stats_2['annual_volatility'])

    result = { 'correlation': correlation }

    output.debug(f'Storing ({ticker_1}, {ticker_2}) correlation in cache...')
    with open(buffer_store_1, 'w') as outfile:
        json.dump(result, outfile)

    return result