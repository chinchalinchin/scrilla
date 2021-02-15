import os, sys, math, json
import datetime
import numpy
from decimal import Decimal

import app.settings as settings
import app.services as services
import app.markets as markets

import util.logger as logger
import util.formatter as formatter
import util.helper as helper

output = logger.Logger('app.statistics', settings.LOG_LEVEL)

# NOTE: the format of 'sample_prices' was chosen so any function that accepts it as an argument
#       can pass the same argument to other statistical functions with minimal formatting.
#       While some of the information in 'sample_prices' may be redundant, i.e. 'tickers' is a subset
#       of 'sample_prices', this format provides an easier method of communication between functions.
#       In particular, the call to 'calculate_risk_return' inside of 'calculate_ito_correlation' is able
#       pass 'sample_prices' directly into 'calculate_risk_return' without having to worry whether it
#       is passing in a 'None'-type object, or a list of prices ordered by date.

def calculate_moving_averages(tickers, start_date=None, end_date=None, sample_prices=None):
    """
    Parameters
    ----------
    1. tickers : [ str ] \n
        array of ticker symbols correspond to the moving averages to be calculated. \n \n 
    2. start_date : datetime.date \n 
        start date of the time period over which the moving averages will be calculated. \n \n 
    3. end_date : datetime.date\n 
        end date of the time period over which the moving averages will be calculated. \n \n 
    4. sample_prices : { 'ticker' (str) : { 'date' (str) : 'price' (str) } } \n
        A list of the asset prices for which moving_averages will be calculated. Overrides calls to service and calculates correlation for sample of prices supplied. Function will disregard start_date and end_date if sample_price is specified. Must be of the format: {'ticker_1': { 'date_1' : 'price_1', 'date_2': 'price_2' .}, 'ticker_2': { 'date_1' : 'price_1:, ... } } and ordered from latest date to earliest date.  \n \n
    
    Output
    ------
    (averages, dates)-tuple, where averages is a 3D array with the following format :
    averages[ticker][period][date] and dates is a list of dates between the start_date
    and end_date

    Notes
    -----
    NOTE #1: assumes price history is ordered from latest to earliest date. \n \n 
    NOTE #2: If no start_date and end_date passed in, static snapshot of moving averages,
            i.e. the moving averages as of today (or last close), are calculated and 
            returned. \n \n
    NOTE #3: If asset types are mixed, then the sample from which the average is calculated
           only consists of prices on business days. In other words, since crypo trades on
           weekends, to compare the moving average of equities and crypto, the moving average
           is only returned for business days. The moving average of crypto is still calculated
           using weekend price data, i.e. the moving average on Monday contains information about
           the moving average on Sunday, but the moving average on Sunday is discarded from the
           returned data, due to the fact equities are not traded on weekends. \n \n 
    NOTE #4: MOVING AVERAGE OVER DATE RANGE LOOP CALCULATION PSEUDO-CODE \n 
              1. for start date to end date: \n
                2. get today's price \n
                3. calculate today's return \n
                4. for all elements of MAs_n \n
                    5. if today's date is less than a MA_n period away from the date of this MAs_n element \n
                        6. add today's return / MA_n_PERIOD to this element of MAs_n \n 
                        7. create today's MAs_n element \n
    """
    moving_averages = []

    # Moving Average Snapshot
    if start_date is None and end_date is None:
        for ticker in tickers:
            output.debug(f'Calculating Moving Average for {ticker}')

            if sample_prices is None:
                prices = services.get_daily_price_history(ticker)
            else:
                prices = sample_prices[ticker]

            asset_type = markets.get_asset_type(ticker)
            trading_period = markets.get_trading_period(asset_type)

            today = False
            count, tomorrows_price, MA_1, MA_2, MA_3 = 1, 0, 0, 0, 0
    
            for date in prices:
                todays_price = services.parse_price_from_date(prices, date, asset_type)
                if today:
                    todays_return = numpy.log(float(tomorrows_price) / float(todays_price))/trading_period
                    output.verbose(f'todays_return == {tomorrows_price}/({todays_price}*{round(trading_period,2)}) = {todays_return}') 

                    if count < settings.MA_1_PERIOD:
                        MA_1 += todays_return / settings.MA_1_PERIOD
                        
                    if count < settings.MA_2_PERIOD:
                        MA_2 += todays_return / settings.MA_2_PERIOD

                    if count < settings.MA_3_PERIOD:
                        MA_3 += todays_return / settings.MA_3_PERIOD  
                        count += 1

                else:
                    today = True

                tomorrows_price = services.parse_price_from_date(prices, date, asset_type)

            output.verbose(f'(MA_1, MA_2, MA_3)_{ticker} = ({MA_1}, {MA_2}, {MA_3}')
            moving_averages.append([MA_1, MA_2, MA_3])

        return moving_averages, None

    # Moving Average Scatter Plot
    else:
        previous_asset_type, portfolio_asset_type = None, None
        mixed_flag = False
        original_day_count = 0

        ### START ARGUMENT VALIDATION ###
        output.debug('Checking provided tickers for mixed asset types.')
        for ticker in tickers:
            asset_type = markets.get_asset_type(ticker)
            portfolio_asset_type = asset_type
            if previous_asset_type is not None:
                if previous_asset_type != asset_type:
                    output.debug('Tickers include mixed asset types, flagging calculation.')
                    portfolio_asset_type = None
                    mixed_flag = True
                    break
            previous_asset_type = asset_type

        if not mixed_flag:
            output.debug(f'Tickers provided all of {portfolio_asset_type} asset type.')

        output.debug('Calculating length of date range in trading days.')
        if mixed_flag:
            original_day_count = helper.business_day_between(start_date, end_date)
        elif portfolio_asset_type == settings.ASSET_EQUITY:
            original_day_count = helper.business_days_between(start_date, end_date)
        elif portfolio_asset_type == settings.ASSET_CRYPTO:
            original_day_count = (end_date - start_date).days
        else:
            original_day_count = helper.business_days_between(start_date, end_date)

        output.debug(f'{end_date} - {start_date} = {original_day_count} trading days')

        for ticker in tickers:
            output.debug(f'Calculating Moving Average for {ticker}.')

            asset_type = markets.get_asset_type(ticker)
            trading_period = markets.get_trading_period(asset_type)

            output.debug(f'Offsetting start date to account for longest Moving Average period.')
            if asset_type == settings.ASSET_CRYPTO:
                output.debug(f'{ticker}_asset_type = Crypto')

                output.debug(f'Configuring date variables to account for all dates.')
                new_start_date = start_date - datetime.timedelta(days=settings.MA_3_PERIOD)
                new_day_count = (end_date - new_start_date).days

                # amend equity trading dates to take account of weekends
            elif asset_type == settings.ASSET_EQUITY:
                output.debug(f'{ticker}_asset_type = Equity')

                output.debug(f'Configuring date variables to account for weekends and holidays.')
                new_start_date = helper.decrement_date_by_business_days(start_date=start_date, 
                                                                        business_days=settings.MA_3_PERIOD)
                new_day_count = helper.business_days_between(new_start_date, end_date)

            else:
                output.debug(f'{ticker}_asset_type = Unknown; Defaulting to business dates')

                output.debug(f'Configuring date variables to account for weekends and holidays.')
                new_start_date = helper.decrement_date_by_business_days(start_date=start_date, 
                                                                        business_days=settings.MA_3_PERIOD)
                new_day_count = helper.business_days_between(new_start_date, end_date)

            output.debug(f'start_date -> new_start_date == {start_date} -> {new_start_date}')
            output.debug(f'{end_date} - {new_start_date} == {new_day_count}')

            if sample_prices is None:
                output.debug(f'No {ticker} sample prices provided, calling service.')
                prices = services.get_daily_price_history(ticker, new_start_date, end_date)
            else:
                output.debug(f'{ticker} sample prices provided, skipping service call.')
                prices = sample_prices[ticker]
        ### END ARGUMENT VALIDATION ###

        ### START MOVING AVERAGE CALCULATION ###
            today = False
            count= 1
            tomorrows_price = 0
            MAs_1, MAs_2, MAs_3 = [], [], []

            # See NOTE #4
            for date in prices:
                output.verbose(f'date: {date}')
                todays_price = services.parse_price_from_date(prices, date, asset_type)

                if today:
                   todays_return = numpy.log(float(tomorrows_price) / float(todays_price))/trading_period
                   output.verbose(f'todays_return == ln({tomorrows_price}/{todays_price})/{round(trading_period,4)}) = {round(todays_return,4)}') 

                   for MA in MAs_1:
                       end_flag = False
                       if len(MAs_1) - MAs_1.index(MA) < settings.MA_1_PERIOD:
                           if len(MAs_1) - MAs_1.index(MA) == settings.MA_1_PERIOD - 1:
                               end_flag = True
                               if asset_type == settings.ASSET_EQUITY:
                                   date_of_MA1 = helper.decrement_date_string_by_business_days(date, MAs_1.index(MA))
                               elif asset_type == settings.ASSET_CRYPTO:
                                   date_of_MA1 = helper.string_to_date(date) - datetime.timedelta(days=MAs_1.index(MA))
                               else: 
                                   date_of_MA1 = helper.string_to_date(date) - datetime.timedelta(days=MAs_1.index(MA)) 

                           MA += todays_return / settings.MA_1_PERIOD

                           if end_flag:
                               output.verbose(f'{ticker}_MA_1({date_of_MA1}) = {MA}')

                    # See NOTE #3
                   if mixed_flag or portfolio_asset_type == settings.ASSET_EQUITY:
                        if not(helper.is_date_string_holiday(date) or helper.is_date_string_weekend(date)): 
                            MAs_1.append( (todays_return / settings.MA_1_PERIOD) )
                   elif portfolio_asset_type == settings.ASSET_CRYPTO:
                       MAs_1.append( (todays_return / settings.MA_1_PERIOD))

                   for MA in MAs_2:
                       end_flag = False
                       if len(MAs_2) - MAs_2.index(MA) < settings.MA_2_PERIOD:
                           if len(MAs_2) - MAs_2.index(MA) == settings.MA_2_PERIOD - 1:
                               end_flag = True
                               if asset_type == settings.ASSET_EQUITY:
                                   date_of_MA2 = helper.decrement_date_string_by_business_days(date, MAs_2.index(MA))
                               elif asset_type == settings.ASSET_CRYPTO:
                                   date_of_MA2 = helper.string_to_date(date) + datetime.timedelta(days=MAs_2.index(MA))
                               else: 
                                   date_of_MA2 = helper.string_to_date(date) + datetime.timedelta(days=MAs_2.index(MA)) 
                               
                           MA += todays_return / settings.MA_2_PERIOD

                           if end_flag:
                               output.verbose(f'{ticker}_MA_2({date_of_MA2}) = {MA}')

                    # See NOTE #3
                   if mixed_flag or portfolio_asset_type == settings.ASSET_EQUITY:
                       if not(helper.is_date_string_holiday(date) or helper.is_date_string_weekend(date)):
                            MAs_2.append((todays_return / settings.MA_2_PERIOD))
                   elif portfolio_asset_type == settings.ASSET_CRYPTO:
                       MAs_2.append((todays_return / settings.MA_2_PERIOD))

                   for MA in MAs_3:
                       end_flag = False
                       if len(MAs_3) - MAs_3.index(MA)  < settings.MA_3_PERIOD:
                           if len(MAs_3) - MAs_3.index(MA) == settings.MA_3_PERIOD - 1:
                               end_flag = True
                               if asset_type == settings.ASSET_EQUITY:
                                   date_of_MA3 = helper.decrement_date_string_by_business_days(date, MAs_3.index(MA))
                               elif asset_type == settings.ASSET_CRYPTO:
                                   date_of_MA3 = helper.string_to_date(date) + datetime.timedelta(days=MAs_3.index(MA))
                               else: 
                                   date_of_MA3 = helper.string_to_date(date) + datetime.timedelta(days=MAs_3.index(MA)) 

                           MA += todays_return / settings.MA_3_PERIOD

                           if end_flag:
                               output.verbose(f'{ticker}_MA_3({date_of_MA3}) = {MA}')

                    # See NOTE #3
                   if mixed_flag or portfolio_asset_type == settings.ASSET_EQUITY:
                       if not(helper.is_date_string_holiday(date) or helper.is_date_string_weekend(date)):
                           MAs_3.append((todays_return / settings.MA_3_PERIOD))
                   elif portfolio_asset_type == settings.ASSET_CRYPTO: 
                       MAs_3.append((todays_return / settings))

                else:
                    today = True
                    
                tomorrows_price = services.parse_price_from_date(prices, date, asset_type)

            MAs_1 = MAs_1[:original_day_count]
            MAs_2 = MAs_2[:original_day_count]
            MAs_3 = MAs_3[:original_day_count]

            moving_averages.append([MAs_1, MAs_2, MAs_3])

        ### END MOVING AVERAGE CALCULATION ###

        ### START RESPONSE FORMATTING ###
        if not mixed_flag:
            if portfolio_asset_type == settings.ASSET_EQUITY:
                dates_between = helper.business_dates_between(start_date, end_date)
            elif portfolio_asset_type == settings.ASSET_CRYPTO:
                dates_between = helper.dates_between(start_date, end_date)
            else:
                dates_between = helper.business_dates_between(start_date, end_date)
        else:
            dates_between = helper.business_dates_between(start_date, end_date)
        
        output.debug(f'If everything is correct, then len(moving_averages[0][1]) == len(dates_between)')
        if len(moving_averages[0][1]) == len(dates_between):
            output.debug("Your program rules.")
            output.debug('{} = {}'.format(len(moving_averages[0][1]), len(dates_between)))
        else: 
            output.debug("Your program sucks.")
            output.debug('{} != {}'.format(len(moving_averages[0][1]), len(dates_between)))

        ### END RESPONSE FORMATTING ###
        return moving_averages, dates_between 

def calculate_risk_return(ticker, start_date=None, end_date=None, sample_prices=None):
    """
    Parameters
    ----------
    1. ticker : str \n
        Ticker symbols whose risk-return profile is to be calculated. \n \n 
    2. start_date : datetime.date \n 
        Start date of the time period over which the risk-return profile is to be calculated. Defaults to None. \n \n
    3. end_date : datetime.date \n 
        End date of the time period over which the risk-return profile is to be calculated. Defaults to None. \n \n
    5. sample_prices : { 'date' (str) : 'price' (str) } \n
        A list of the asset prices for which correlation will be calculated. Overrides calls to service and calculates correlation for sample of prices supplied. Function will disregard start_date and end_date if sample_price is specified:  { 'ticker' : { 'date_1' : 'price_1', 'date_2': 'price_2' ... } }  and ordered from latest date to earliest date.  \n \n

    Output
    ------
    { 'annual_return' : float, 'annual_volatility': float } \n \n

    Notes
    -----
    NOTE #1: assumes price history is ordered from latest to earliest date. \n \n 
    """
    now = datetime.datetime.now()
    timestamp = '{}{}{}'.format(now.month, now.day, now.year)
    buffer_store= os.path.join(settings.CACHE_DIR, f'{timestamp}_{ticker}_{settings.CACHE_STAT_KEY}.{settings.FILE_EXT}')

    asset_type = markets.get_asset_type(ticker)
    trading_period = markets.get_trading_period(asset_type)

    if not trading_period:
        output.debug("Asset did not map to (crypto, equity) grouping")
        return False

    if sample_prices is None:
        if start_date is None and end_date is None:
            output.debug(f'Checking for cached {ticker} statistics.')

            if os.path.isfile(buffer_store):
                output.debug(f'Loading in cached {ticker} statistics.')
                with open(buffer_store, 'r') as infile:
                    results = json.load(infile)
                return results
            else:
                output.debug(f'No cached {ticker} statistics found, calling service.')
                prices = services.get_daily_price_history(ticker=ticker)
        else: 
            output.debug(f'No sample prices provided, calling service.')
            prices = services.get_daily_price_history(ticker=ticker, start_date=start_date, end_date=end_date)
    else:
        output.debug(f'{ticker} sample prices provided, skipping service call.')
        prices = sample_prices[ticker]

    if not prices:
        output.debug(f'No prices could be retrieved for {ticker}')
        return False
    
    sample = len(prices)
    # calculate sample mean annual return
    i, mean_return, tomorrows_price = 0, 0, 0 
    output.debug(f'Calculating mean annual return over last {sample} days for {ticker}')

    for date in prices:
        todays_price = services.parse_price_from_date(prices, date, asset_type)

        if i != 0:
            output.verbose(f'{date}: (todays_price, tomorrows_price) = ({todays_price}, {tomorrows_price})')
            daily_return = numpy.log(float(tomorrows_price)/float(todays_price))/trading_period
            mean_return = mean_return + daily_return/sample
            output.verbose(f'{date}: (daily_return, mean_return) = ({round(daily_return, 2)}, {round(mean_return, 2)})')

        else:
            output.verbose('Skipping first date.')
            i += 1  

        tomorrows_price = services.parse_price_from_date(prices, date, asset_type)
        
    # calculate sample annual volatility
    today = False
    variance, tomorrows_price = 0, 0
    mean_mod_return = mean_return*numpy.sqrt(trading_period)
    output.debug(f'Calculating mean annual volatility over last {sample} days for {ticker}')

    for date in prices:
        todays_price = services.parse_price_from_date(prices, date, asset_type)

        if today:
            output.verbose(f'{date}: (todays_price, tomorrows_price) = ({todays_price}, {tomorrows_price})')
            current_mod_return= numpy.log(float(tomorrows_price)/float(todays_price))/numpy.sqrt(trading_period) 
            variance = variance + (current_mod_return - mean_mod_return)**2/(sample - 1)
            output.verbose(f'{date}: (daily_variance, sample_variance) = ({round(current_mod_return, 2)}, {round(variance, 2)})')

        else:
            today = True

        tomorrows_price = services.parse_price_from_date(prices, date, asset_type)

    # adjust for output
    volatility = numpy.sqrt(variance)
    # ito's lemma
    mean_return = mean_return + 0.5*(volatility**2)
    output.debug(f'(mean_return, sample_volatility) = ({round(mean_return, 2)}, {round(volatility, 2)})')

    results = {
        'annual_return': mean_return,
        'annual_volatility': volatility
    }

    # store results in buffer for quick access
    if start_date is None and end_date is None:
        output.debug(f'Storing {ticker} statistics in cache...')
        with open(buffer_store, 'w') as outfile:
            json.dump(results, outfile)

    return results

def calculate_ito_correlation(ticker_1, ticker_2, start_date=None, end_date=None, sample_prices=None):
    """
    Parameters
    ----------
    1. ticker_1 : str \n
        Ticker symbol for first asset. \n \n
    2. ticker_2 : str \n 
        Ticker symbol for second asset \n \n
    3. start_date : datetime.date \n 
        Start date of the time period over which correlation will be calculated. \n \n 
    4. end_date : datetime.date \n 
        End date of the time period over which correlation will be calculated. \n \n  
    5. sample_prices : { 'ticker' (str) : { 'date' (str) : 'price' (str) } } \n
        A list of the asset prices for which correlation will be calculated. Overrides calls to service and calculates correlation for sample of prices supplied. Will disregard start_date and end_date. Must be of the format: {'AAPL': { 'date_1' : 'price_1', 'date_2': 'price_2' ...}, 'BX': { 'date_1' : 'price_1:, ... } } and ordered from latest date to earliest date.  \n \n
    
    Output
    ------
    { 'correlation' : float } \n

    Notes
    -----
    NOTE #1: 
    NOTE #2: assumes price history returns from latest to earliest date.\n \n
    NOTE #3: does not cache correlation if start_date and end_date are specified, 
          i.e. only caches current correlation from the last 100 days.\n \n
    """
    ### START DATA RETRIEVAL ###
    now = datetime.datetime.now()
    timestamp = '{}{}{}'.format(now.month, now.day, now.year)
    buffer_store_1= os.path.join(settings.CACHE_DIR, f'{timestamp}_{ticker_1}_{ticker_2}_correlation.json')
    buffer_store_2= os.path.join(settings.CACHE_DIR, f'{timestamp}_{ticker_2}_{ticker_1}_correlation.json')

    if sample_prices is None:
        # reset sample price and set entries to None for consistency in calculate_risk_return call below.
        output.debug('No sample prices provided. Calling service for prices.')

        sample_prices = {}
        
        if start_date is None and end_date is None:
            # check if results exist in cache location 1
            output.debug('Checking for correlation calculation in cache.')
            if os.path.isfile(buffer_store_1):
                output.debug(f'Loading in cached ({ticker_1}, {ticker_2}) correlation.')
                with open(buffer_store_1, 'r') as infile:
                    output.debug(f'Cached ({ticker_1}, {ticker_2}) correlation loaded.')
                    results = json.load(infile)
                    correlation = results
                return correlation

            # check if results exist in cache location 2
            elif os.path.isfile(buffer_store_2):
                output.debug(f'Loading in cached ({ticker_1}, {ticker_2}) correlation.')
                with open(buffer_store_2, 'r') as infile:
                    output.debug(f'Cached ({ticker_1}, {ticker_2}) correlation loaded.')
                    results = json.load(infile)
                    correlation = results
                return correlation
            else:
                output.debug(f'No cached ({ticker_1}, {ticker_2}) correlation found, retrieving price histories for calculation.')
                prices_1 = services.get_daily_price_history(ticker=ticker_1)
                prices_2 = services.get_daily_price_history(ticker=ticker_2)
                sample_prices[ticker_1], sample_prices[ticker_2] = prices_1, prices_2
        else:
            output.debug('No sample prices provided, retrieving price histories for calculation.')
            prices_1 = services.get_daily_price_history(ticker=ticker_1, start_date=start_date, end_date=end_date)
            prices_2 = services.get_daily_price_history(ticker=ticker_2, start_date=start_date, end_date=end_date)
            sample_prices[ticker_1], sample_prices[ticker_2] = prices_1, prices_2

    else:
        output.debug('Sample prices provided, skipping service calls.')
        prices_1, prices_2 = sample_prices[ticker_1], prices_2[ticker_2]
        
    if (not prices_1) or (not prices_2):
        output.debug("Prices cannot be retrieved for correlation calculation")
        return False 
    ### END DATA RETRIEVAL ###
    
    ### START SAMPLE STATISTICS CALCULATION ###
    output.debug(f'Preparing to calculate correlation for ({ticker_1},{ticker_2})')
    stats_1 = calculate_risk_return(ticker_1, start_date, end_date, sample_prices)
    stats_2 = calculate_risk_return(ticker_2, start_date, end_date, sample_prices)

    if (not stats_1) or (not stats_2):
        output.debug("Sample statistics cannot be calculated for correlation calculation")
        return False

    asset_type_1 = markets.get_asset_type(ticker_1)
    asset_type_2 = markets.get_asset_type(ticker_2)
    
    # ito's lemma
    if asset_type_1 == settings.ASSET_EQUITY:
        mod_mean_1 = (stats_1['annual_return'] - 0.5*(stats_1['annual_volatility'])**2)*numpy.sqrt(settings.ONE_TRADING_DAY)
    elif asset_type_1 == settings.ASSET_CRYPTO:
        mod_mean_1 = (stats_1['annual_return'] - 0.5*(stats_1['annual_volatility'])**2)*numpy.sqrt((1/365))

    if asset_type_2 == settings.ASSET_EQUITY:
        mod_mean_2 = (stats_2['annual_return'] - 0.5*(stats_2['annual_volatility'])**2)*numpy.sqrt(settings.ONE_TRADING_DAY)
    elif asset_type_2 == settings.ASSET_CRYPTO:
        mod_mean_2 = (stats_2['annual_return'] - 0.5*(stats_2['annual_volatility'])**2)*numpy.sqrt((1/365))

    # TODO: Pretty sure I no longer need these constants. The correlation loop implicitly ignores
    # dates where both assets do not have corresponding prices, i.e. if price 1 is None and price 2
    # is not None, the loop will skip that date.
    # I could possibly use these constants to retrieve a longer price history for equities, so
    # the sample size isn't decreased by mismatched trading days between asset types.
    weekend_offset_1, weekend_offset_2 = 0, 0

    # if asset_types are same
    if asset_type_1 == asset_type_2:
        same_type = True
        output.debug(f'Asset({ticker_1}) and Asset({ticker_2}) are the same type of asset')

        if asset_type_1 == settings.ASSET_CRYPTO:
            trading_period = (1/365)
        elif asset_type_1 == settings.ASSET_EQUITY:
            trading_period = settings.ONE_TRADING_DAY
        else:
            trading_period = settings.ONE_TRADING_DAY


    # if asset_types are different, collect # of days where one assets trades and the other does not.
    else:
        same_type = False
        output.debug(f'Asset({ticker_1}) and Asset({ticker_2}) are not the same type of asset')

        if asset_type_1 == settings.ASSET_CRYPTO and asset_type_2 == settings.ASSET_EQUITY:
            for date in prices_1:
                if helper.is_date_string_weekend(date):
                    weekend_offset_1 += 1
            trading_period = settings.ONE_TRADING_DAY

        elif asset_type_1 == settings.ASSET_EQUITY and asset_type_2 == settings.ASSET_CRYPTO:
            for date in prices_2:
                if helper.is_date_string_weekend(date):
                    weekend_offset_1 += 1
            trading_period = settings.ONE_TRADING_DAY

    # make sure datasets are only compared over corresponding intervals, i.e.
    # always calculate correlation over smallest interval.
    if (len(prices_1) - weekend_offset_1) == (len(prices_2) - weekend_offset_2) \
        or (len(prices_1) - weekend_offset_1) < (len(prices_2) - weekend_offset_2):
        sample_prices = prices_1
        offset = weekend_offset_1
    else:
        sample_prices = prices_2
        offset = weekend_offset_2
    
    output.debug(f'(trading_period, offset) = ({trading_period}, {offset})')
    output.debug(f'Calculating ({ticker_1}, {ticker_2}) correlation.')

    # Initialize loop variables
    i, covariance, tomorrows_price_1, tomorrows_price_2 = 0, 0, 1, 1
    delta = 0
    tomorrows_date, todays_date = "", ""
    sample = len(sample_prices)

    #### START CORRELATION LOOP ####
    for date in sample_prices:
        todays_price_1 = services.parse_price_from_date(prices_1, date, asset_type_1)
        todays_price_2 = services.parse_price_from_date(prices_2, date, asset_type_2)
        todays_date = date
        output.verbose(f'(todays_date, todays_price_{ticker_1}, todays_price_{ticker_2}) = ({todays_date}, {todays_price_1}, {todays_price_2})')
            
        # if both prices exist, proceed
        if todays_price_1 and todays_price_2 and tomorrows_price_1 and tomorrows_price_2:
            if i != 0:
                output.verbose(f'Iteration #{i}')
                output.verbose(f'(todays_price, tomorrows_price)_{ticker_1} = ({todays_price_1}, {tomorrows_price_1})')
                output.verbose(f'(todays_price, tomorrows_price)_{ticker_2} = ({todays_price_2}, {tomorrows_price_2})')
                
                if delta != 0:
                    output.verbose(f'current delta = {delta}')

                time_delta = (1+delta)/numpy.sqrt(trading_period)
                current_mod_return_1= numpy.log(float(tomorrows_price_1)/float(todays_price_1))*time_delta
                current_mod_return_2= numpy.log(float(tomorrows_price_2)/float(todays_price_2))*time_delta
                current_sample_covariance = (current_mod_return_1 - mod_mean_1)*(current_mod_return_2 - mod_mean_2)/(sample - 1)
                covariance = covariance + current_sample_covariance
            
                output.verbose(f'(return_1, return_2) = ({round(current_mod_return_1, 2)}, {round(current_mod_return_2, 2)})')
                output.verbose(f'(current_sample_covariance, covariance) = ({round(current_sample_covariance, 2)}, {round(covariance, 2)})')
                
                # once missed data points are skipped, annihiliate delta
                if delta != 0:
                    delta = 0
                
            i += 1

        # if one price doesn't exist, then a data point has been lost, so revise sample. 
        # collect number of missed data points (delta) to offset return calculation
        else: 
            output.verbose('Lost a day. Revising covariance and sample.')
            revised_covariance = covariance*(sample - 1)
            sample -= 1 
            covariance = revised_covariance/(sample - 1)
            delta += 1
            if i == 0:
                i += 1
            output.verbose(f'(revised_covariance, revised_sample) = ({covariance}, {sample})')
        
        tomorrows_price_1 = services.parse_price_from_date(prices_1, date, asset_type_1)
        tomorrows_price_2 = services.parse_price_from_date(prices_2, date, asset_type_2)
        tomorrows_date = date
    #### END CORRELATION LOOP ####

    correlation = covariance/(stats_1['annual_volatility']*stats_2['annual_volatility'])

    result = { 'correlation' : correlation }

    if start_date is None and end_date is None:
        output.debug(f'Storing ({ticker_1}, {ticker_2}) correlation in cache...')
        with open(buffer_store_1, 'w') as outfile:
            json.dump(result, outfile)

    return result

def get_ito_correlation_matrix_string(tickers, indent=0, start_date=None, end_date=None, sample_prices=None):
    """
    Parameters
    ----------
    1. tickers : [str] \n
        Array of tickers for which the correlation matrix will be calculated and formatted. \n \n
    2. indent : int \n 
        Amount of indent on each new line of the correlation matrix. \n \n
    3. start_date : datetime.date \n 
        Start date of the time period over which correlation will be calculated. \n \n 
    4. end_date : datetime.date \n 
        End date of the time period over which correlation will be calculated. \n \n  
    
    Output
    ------
    A correlation matrix string formatted with new lines and spaces.\n
    """
    entire_formatted_result, formatted_title = "", ""

    line_length, percent_length, first_symbol_length = 0, 0, 0
    new_line=""
    no_symbols = len(tickers)

    for i in range(no_symbols):
        this_symbol = tickers[i]
        symbol_string = ' '*indent + f'{this_symbol} '

        if i != 0:
            this_line = symbol_string + ' '*(line_length - len(symbol_string) - 7*(no_symbols - i))
            # NOTE: seven is number of chars in ' 100.0%'
        else: 
            this_line = symbol_string
            first_symbol_length = len(this_symbol)

        new_line = this_line
        
        for j in range(i, no_symbols):
            if j == i:
                new_line += " 100.0%"
            
            else:
                that_symbol = tickers[j]
                result = calculate_ito_correlation(this_symbol, that_symbol, start_date, end_date, sample_prices) 
                if not result:
                    output.debug(f'Cannot correlation for ({this_symbol}, {that_symbol})')
                    return False
                formatted_result = str(100*result['correlation'])[:formatter.SIG_FIGS]
                new_line += f' {formatted_result}%'

        entire_formatted_result += new_line + '\n'
        
        if i == 0:
            line_length = len(new_line)

    formatted_title += ' '*(indent + first_symbol_length+1)
    for symbol in tickers:
        sym_len = len(symbol)
        formatted_title += f' {symbol}'+ ' '*(7-sym_len)
        # NOTE: seven is number of chars in ' 100.0%'
    formatted_title += '\n'

    whole_thing = formatted_title + entire_formatted_result
    return whole_thing

def sample_correlation(x, y):
    if len(x) != len(y):
        output.debug(f'Samples are not comparable')
        return False
    elif len(x) == 1 or len(x) == 1:
        output.debug(f'Sample correlation cannot be computed for a sample size less than or equal to 1.')
    else:
        sumproduct, sum_x_squared, sum_x, sum_y, sum_y_squared= 0, 0, 0, 0, 0
        n = len(x)
        for i in range(len(x)):
            sumproduct += x[i]*y[i]
            sum_x += x[i]
            sum_x_squared = x[i]**2
            sum_y += y[i]
            sum_y += y[i]**2
        correl_num = ((n*sumproduct) - sum_x*sum_y)
        correl_den = numpy.sqrt((n*sum_x_squared-sum_x**2)*(n*sum_y_squared-sum_y**2))

        # LET'S DO SOME MATHEMATICS! (to get around division by zero!)
        #   Unfortunately, this only works when A and B > 0 because log
        #       of a negative number only exists in complex plane.
        #   1. correl = A/B
        #   2. log(correl) = log(A/B) = log(A) - log(B)
        #   3. exp(log(correl)) = exp(log(A/B))
        #   4. correl = exp(log(A/B))
        if correl_num > 0 and correl_den > 0:
            log_correl = numpy.log(correl_num) - numpy.log(correl_den)
            correlation = numpy.exp(log_correl)
        else:
            if correl_den != 0:
                correlation = correl_num / correl_den
            else:
                output.debug('Denominator for correlation formula to small for division')
                return False

        return correlation

def sample_mean(x):
    xbar, n = 0, len(x)
    if n == 0:
        output.debug('Sample mean cannot be computed for a sample size of 0.')
        return False
    else:
        for i in x:
            xbar += i/n
        return xbar

def sample_variance(x):
    mu, sigma, n = sample_mean(x=x), 0, len(x)
    if n == 1 or n == 0:
        output.debug('Sample variance cannot be computed for a sample size less than  or equal to 1.')
        return False
    else:
        for i in x:
            sigma += ((i-mu)**2)/(n-1)
        return sigma

def regression_beta(x, y):
    correl = sample_correlation(x=x, y=y)
    vol_x = numpy.sqrt(sample_variance(x=x))
    vol_y = numpy.sqrt(sample_variance(x=y))
    if not correl or not vol_x or not vol_y:
        output.debug('Error calculating statistics for regression Beta.')
        return False
    else:
        beta = correl * vol_y / vol_x
        return beta

def regression_alpha(x, y):
    y_mean, x_mean = sample_mean(y), sample_mean(x)
    if not y_mean or not x_mean:
        output.debug('Error calculating statistics for regression alpha')
    else:
        alpha = y_mean - regression_beta(x=x, y=y)*x_mean
        return alpha
    

