import itertools, time, requests

#  Note: need to import from package when running from wheel.
# if running locally through main.py file, these imports should be replaced
#       from . import settings, from . import files
# annoying, but it is what it is.
from scrilla import settings
from scrilla import files 

import util.outputter as outputter
import util.helper as helper

logger = outputter.Logger("services", settings.LOG_LEVEL)

CLOSE_PRICE = "close"
OPEN_PRICE = "open"

# TODO: if start_date = end_date, then return only todays date?
# TODO: these functions, validate_order and validate_tradeability, should probably go in util.helper
#       however, they won't have logging output in helper!
def validate_order_of_dates(start_date, end_date):
    switch_flag = start_date is not None and end_date is not None

    if start_date is not None and helper.is_date_today(start_date):
        time_delta = (end_date - start_date).days
        if time_delta == 0: # either end_date is also today
            return True, start_date, end_date
        return False, None, None

    if end_date is not None and helper.is_date_today(end_date):
        end_date = None
        switch_flag = False

    if switch_flag:
        time_delta = end_date - start_date
        
        if time_delta.days < 0:
            start_date, end_date = end_date, start_date
    
    return True, start_date, end_date

def validate_tradeability_of_dates(start_date, end_date):
    if (
        start_date is not None
        and helper.is_date_holiday(start_date)
        or helper.is_date_weekend(start_date)
    ):
        logger.debug(f'{start_date} is invalid. Equities do not trade on holidays or weekends.')

        start_date = helper.get_previous_business_date(start_date)
        logger.debug(f'Setting start date to next business day, {start_date}')

    if (
        end_date is not None
        and helper.is_date_holiday(end_date)
        or helper.is_date_weekend(end_date)
    ):
        logger.debug(f'{end_date} is invalid. Equities do not trade on holidays or weekends.')

        end_date = helper.get_previous_business_date(end_date)
        logger.debug(f'Setting end date to previous business day, {end_date}.')

    return start_date, end_date

def validate_asset_type(asset_type, ticker):
    if asset_type is None:
        logger.debug('No asset type provided, determining from ticker.')
        asset_type=files.get_asset_type(ticker)  
    else: 
        logger.debug(f'Asset type {asset_type} provided')
    return asset_type

def parse_price_from_date(prices, date, asset_type, which_price=CLOSE_PRICE):
    """
    Parameters
    ----------
    1. prices : { str : str } \n
        2D list containing the AlphaVantage response with the first layer peeled off, i.e.
        no metadata, just the date and prices. \n \n
    2. date: str \n
        String of the date to be parsed. Note: this is not a datetime.date object. String
        must be formatted YYYY-MM-DD \n \n
    3. asset_type : str \n
        String that specifies what type of asset price is being parsed. Options are statically
        typed in the  settings.py file:  settings.ASSET_EQUITY,  settings.ASSET_CRYPTO \n \n
    
    Output
    ------
    String containing the price on the specified date.
    """
    try:
        if settings.PRICE_MANAGER == 'alpha_vantage':
            
            if asset_type == settings.ASSET_EQUITY:
                if which_price == CLOSE_PRICE:
                    return prices[date][settings.AV_RES_EQUITY_CLOSE_PRICE]
                if which_price == OPEN_PRICE:
                    return prices[date][settings.AV_RES_EQUITY_OPEN_PRICE]

            elif asset_type == settings.ASSET_CRYPTO:
                if which_price == CLOSE_PRICE:
                    return prices[date][settings.AV_RES_CRYPTO_CLOSE_PRICE]
                if which_price == OPEN_PRICE:
                    return prices[date][settings.AV_RES_CRYPTO_OPEN_PRICE]

    except KeyError:
        logger.info('Price unable to be parsed from date.')
        return False

def query_service_for_daily_price_history(ticker, start_date=None, end_date=None, asset_type=None, full=False):
    """
    Description
    -----------
    Function in charge of querying external services for daily price history. \n \n

    Parameters
    ----------
    1. tickers : [ str ] \n
        Required. List of ticker symbols corresponding to the price histories to be retrieved. \n \n
    2. start_date : datetime.date \n 
        Optional. Start date of price history. Defaults to None. \n \n
    3. end_date : datetime.date \n 
        Optional: End date of price history. Defaults to None. \n \n
    4. full: boolean \n
        Optional: If specified, will return the entire price history. Will override start_date and end_date if provided. Defaults to False. \n \n
    
    Notes
    -----
    By default, AlphaVantage returns the last 100 days of prices for equities, while returning the entire price history for crypto asset. If no start_date or end_date are specified, this function will truncate the crypto price histories to have a length of 100 so the price histories across asset types are the same length. 
    """
    # TODO: price histories aren't the same length, though, because of weekends. 
    # TODO: retrieve crypto history for len(crypto_prices) = 100 + weekends
    # TODO: checking end and start dates for holiday/weekend in this method may 
    #       mess up statistical calculations, i.e. statistics.py expects a sample 
    #       of a certain size and gets a different size.

    ### START: ARGUMENT VALIDATION ###
    if not full:
        if start_date is not None and end_date is not None:
            valid_dates, start_date, end_date = validate_order_of_dates(start_date, end_date)
            if not valid_dates:
                return False
    else:
        logger.debug('Full price history requested, nulling start_date and end_date')
        start_date, end_date = None, None

    asset_type = validate_asset_type(asset_type=asset_type, ticker=ticker)
    
        # Verify dates fall on trading days (i.e. not weekends or holidays) if asset_type is ASSET_EQUITY
    if asset_type == settings.ASSET_EQUITY and (start_date is not None or end_date is not None):
        start_date, end_date = validate_tradeability_of_dates(start_date, end_date)
    ### END: Argument Validation ###

    ### START: Service Query ###
    if settings.PRICE_MANAGER == "alpha_vantage":

        ### START: AlphaVantage Service Query ###
        query = f'{settings.PARAM_AV_TICKER}={ticker}'

        if asset_type == settings.ASSET_EQUITY:
            query += f'&{settings.PARAM_AV_FUNC}={settings.ARG_AV_FUNC_EQUITY_DAILY}'
        elif asset_type == settings.ASSET_CRYPTO:
            query += f'&{settings.PARAM_AV_FUNC}={settings.ARG_AV_FUNC_CRYPTO_DAILY}&{settings.PARAM_AV_DENOM}={settings.DENOMINATION}'
        else:
            return False

            # NOTE: only need to modify EQUITY query, CRYPTO always returns full history
        if (full or start_date is not None or end_date is not None) and (asset_type == settings.ASSET_EQUITY):
            query += f'&{settings.PARAM_AV_SIZE}={settings.ARG_AV_SIZE_FULL}'

        auth_query = query + f'&{settings.PARAM_AV_KEY}={settings.AV_KEY}'
        url=f'{settings.AV_URL}?{auth_query}'  
        logger.debug(f'AlphaVantage query (w/o key) = {query}')   
        
        prices = requests.get(url).json()
        first_element = helper.get_first_json_key(prices)

            # check for bad response
        if first_element == settings.AV_RES_ERROR:
            logger.info(prices[settings.AV_RES_ERROR])
            return False

            # check and wait for API rate limit refresh
        first_pass = True
        while first_element == settings.AV_RES_LIMIT:
            if first_pass:
                logger.debug('AlphaVantage API rate limit per minute exceeded. Waiting.')
                first_pass = False
            else:
                logger.debug('Waiting.')
            
            time.sleep(settings.BACKOFF_PERIOD)
            prices = requests.get(url).json()
            first_element = helper.get_first_json_key(prices)

                # end function is daily rate limit is reached 
            if first_element == settings.AV_RES_DAY_LIMIT:
                logger.info('Daily AlphaVantage rate limit exceeded. No more queries possible!')
                return False
        ### END: AlphaVantage Service Query ###

        ### START: AlphaVantage Equity Response Parsing ###
        # TODO: could possibly initial start_index = 0 and end_index = len(prices)
        #           and then filter through conditional and return prices[start:end]
        #           no matter what?
        # NOTE: Remember AlphaVantage is ordered current to earliest. END_INDEX is 
        # actually the beginning of slice and START_INDEX is actually end of slice. 
        if asset_type == settings.ASSET_EQUITY:
            try:
                if not full and (start_date is not None and end_date is not None):
                    start_string, end_string = helper.date_to_string(start_date), helper.date_to_string(end_date)
                    start_index = list(prices[settings.AV_RES_EQUITY_FIRST_LAYER].keys()).index(start_string)
                    end_index = list(prices[settings.AV_RES_EQUITY_FIRST_LAYER].keys()).index(end_string)
                    prices = dict(itertools.islice(prices[settings.AV_RES_EQUITY_FIRST_LAYER].items(), end_index, start_index+1))
                    return prices

                if not full and (start_date is None and end_date is not None):
                    end_string = helper.date_to_string(end_date)
                    end_index = list(prices[settings.AV_RES_EQUITY_FIRST_LAYER].keys()).index(end_string)
                    prices = dict(itertools.islice(prices[settings.AV_RES_EQUITY_FIRST_LAYER].items(), end_index))
                    return prices

                if not full and (start_date is not None and end_date is None):
                    start_string = helper.date_to_string(start_date)
                    start_index = list(prices[settings.AV_RES_EQUITY_FIRST_LAYER].keys()).index(start_string)
                    prices = dict(itertools.islice(prices[settings.AV_RES_EQUITY_FIRST_LAYER].items(), 0, start_index+1))
                    return prices

                prices = prices[settings.AV_RES_EQUITY_FIRST_LAYER]
                return prices
                    
            except KeyError:
                logger.info('Error encountered parsing AlphaVantage equity response')
                logger.sys_error()
                return False
        ### END: AlphaVantage Equity Response Parsing ###

        ### START: AlphaVantage Crypto Response Parsing ###
        # TODO: len(crypto_prices) - weekends. do i want to do it here? or in statistics.py when
        # the different datasets are actually being compared? probably statistics.py.
        # NO! because statistics.py will need complete datasets to compare, so it's better
        # that crypto returns a dataset longer than is needed!
        #
        # TODO: can probably set RESPONSE_KEY to asset_type and condense the double conditional
        # branching down to one branch. will make it simpler.
        elif asset_type == settings.ASSET_CRYPTO:
            try:
                if not full and (start_date is None and end_date is None):
                    truncated_prices, index = {}, 0
                    for date in prices[settings.AV_RES_CRYPTO_FIRST_LAYER]:
                        if index < 100:
                            truncated_prices[date] = prices[settings.AV_RES_CRYPTO_FIRST_LAYER][date]
                        else:
                            return truncated_prices
                        index += 1

                elif not full and (start_date is not None and end_date is not None):
                    start_string, end_string = helper.date_to_string(start_date), helper.date_to_string(end_date)
                    start_index = list(prices[settings.AV_RES_CRYPTO_FIRST_LAYER].keys()).index(start_string)
                    end_index = list(prices[settings.AV_RES_CRYPTO_FIRST_LAYER].keys()).index(end_string)
                    prices = dict(itertools.islice(prices[settings.AV_RES_CRYPTO_FIRST_LAYER].items(), end_index, start_index))
                    return prices

                elif not full and (start_date is None and end_date is not None):
                    end_string = helper.date_to_string(end_date)
                    end_index = list(prices[settings.AV_RES_CRYPTO_FIRST_LAYER].keys()).index(end_string) 
                    prices = dict(itertools.islice(prices[settings.AV_RES_CRYPTO_FIRST_LAYER].items(), end_index))
                    return prices


                elif not full and (start_date is not None and end_date is None):
                    start_string = helper.date_to_string(end_date)
                    start_index = list(prices[settings.AV_RES_CRYPTO_FIRST_LAYER].keys()).index(start_string)
                    prices = dict(itertools.islice(prices[settings.AV_RES_CRYPTO_FIRST_LAYER].items(), 0, start_index))
                    return prices

                else:
                    prices = prices[settings.AV_RES_CRYPTO_FIRST_LAYER]
                    return prices
            except KeyError:
                logger.info('Error encountered parsing AlphaVantage crypto response.')
                logger.sys_error()
                return False

        ### END: AlphaVantage Crypto Response Parsing ###

    else:
        logger.info("No PRICE_MANAGER set in .env file!")
        return False

# Checks the file cache for price histories. Otherwise, it hands the request off to the service manager.
def get_daily_price_history(ticker, start_date=None, end_date=None):
    """
    Description
    -----------
    Wrapper around external service request. Checks if response is in local cache before calling service. \n \n


    Parameters
    ----------
    1. tickers : [ str ] \n 
        Required. List of ticker symbols corresponding to the price histories to be retrieved. \n \n
    2. start_date : datetime.date \n 
        Optional: Start date of historical range. Defaults to None. \n \n 
    3. end_date: datetime.date \n 
        Optional: End date of historical range. Defaults to None. 

    Output
    ------
    { date (str) : price (str) }
        Dictionary of prices and their corresponding dates as keys. 
    """

    prices = files.retrieve_local_object(local_object=files.OBJECTS['prices'], 
                                                args={"ticker": ticker, "start_date": start_date, "end_date": end_date})
    if prices is not None:
        return prices
        
    logger.debug(f'Retrieving {ticker} prices from Service Manager.')  
    prices = query_service_for_daily_price_history(ticker=ticker, start_date=start_date, end_date=end_date)

    files.store_local_object(local_object=files.OBJECTS['prices'],value=prices, 
                                args={"ticker": ticker, "start_date": start_date, "end_date": end_date})
    return prices
    
def get_daily_price_latest(ticker):
    """
    Description
    -----------
    Returns the latest closing price. \n \n

    Parameters
    ----------
    1. ticker: str \n 
        Required: ticker symbol whose latest closing price is to be retrieved. \n \n
    """
    if settings.PRICE_MANAGER == "alpha_vantage":
        asset_type = files.get_asset_type(ticker)
        prices = get_daily_price_history(ticker)
        first_element = helper.get_first_json_key(prices)

        if asset_type == settings.ASSET_EQUITY:
            return prices[first_element][settings.AV_RES_EQUITY_CLOSE_PRICE]

        if asset_type == settings.ASSET_CRYPTO:
            return prices[first_element][settings.AV_RES_CRYPTO_CLOSE_PRICE]
            
    else:
        logger.info("No PRICE_MANAGER set in .env file!")
        return None

def query_service_for_daily_stats_history(statistic, start_date=None, end_date=None, full=False):
    """
    Description
    -----------
    Makes an HTTP request to the STAT_MANAGER defined in the settings.py and configured through the environment variable STAT_MANAGER. \n \n 

    Parameters
    ----------
    1. statistic: str \n 
        Required. Symbol representing the statistic whose history is to be retrieved. \n \n
    2. start_date: datetime.date \n 
        Optional: Start date of historical range. Defaults to None. \n \n 
    3. end_date: datetime.date \n 
        Optional: End date of historical range. Defaults to None.
    """
    if settings.STAT_MANAGER == "quandl":
        stat = {}
    
        if full:
            start_date, end_date = None, None

        if start_date is not None or end_date is not None:
            valid_dates, start_date, end_date = validate_order_of_dates(start_date, end_date)
            if not valid_dates:
                return False

            start_date, end_date = validate_tradeability_of_dates(start_date, end_date)

        url = f'{settings.Q_URL}/'
        query = f'{settings.PATH_Q_FRED}/{statistic}?'
    
        if end_date is not None:
            end_string = helper.date_to_string(end_date)
            query += f'&{settings.PARAM_Q_END}={end_string}' 
            pass

        if start_date is not None:
            start_string = helper.date_to_string(start_date)
            query += f'&{settings.PARAM_Q_START}={start_string}'

        auth_query = f'{query}&{settings.PARAM_Q_KEY}={settings.Q_KEY}'
        url += auth_query
        logger.debug(f'Quandl query (w/o key) = {query}')   

        response = requests.get(url).json()

        # TODO: test for error messages or API rate limits

        raw_stat = response[settings.Q_FIRST_LAYER][settings.Q_SECOND_LAYER]
        formatted_stat = {}

        # TODO: this method always returns the last 100, even if end_date - start_date < 100. Need to change the next
        # few lines to only select response entries that fall within dates.

        if not full:
            raw_stat = raw_stat[:settings.DEFAULT_ANALYSIS_PERIOD]

        for stat in raw_stat:
            formatted_stat[stat[0]] = stat[1]

        return formatted_stat
    logger.info("No STAT_MANAGER set in .env file!")
    return None

# Goes through file cache if start_date and end_date are not provided,
#   otherwise, hands the call off to the service manager.
def get_daily_stats_history(statistic, start_date=None, end_date=None):
    """
    Description
    -----------
    Wrapper around external service call. Checks if response is in local cache before making service call.

    Parameters
    ----------
    1. statistic: str \n 
        Required. Symbol representing the statistic whose history is to be retrieved. \n \n
    2. start_date: datetime.date \n 
        Optional: Start date of historical range. Defaults to None. \n \n 
    3. end_date: datetime.date \n 
        Optional: End date of historical range. Defaults to None.
    """
    stats = files.retrieve_local_object(local_object=files.OBJECTS['statistic'],
                                        args={"stat_symbol": statistic,"start_date": start_date,
                                              "end_date": end_date})
    if stats is not None:
        return stats 
    logger.debug(f'Retrieivng {statistic} statistics from Service Manager')
    stats = query_service_for_daily_stats_history(statistic=statistic, start_date=start_date, end_date=end_date)

    logger.debug(f'Storing {statistic} statistics in cache')
    files.store_local_object(local_object=files.OBJECTS['statistic'], value=stats,
                             args={"stat_symbol": statistic, "start_date": start_date,
                                    "end_date": end_date})
    return stats

def get_daily_stats_latest(statistic):
    """
    Description
    -----------
    Returns the latest value for the inputted statistic symbol. \n \n

    Parameters
    ----------
    1. statistic: str \n 
        Required. Symbol representing the statistc whose value it to be retrieved. \n \n
    """
    if settings.STAT_MANAGER == "quandl":
        stats_history = get_daily_stats_history(statistic=statistic)
        first_element = helper.get_first_json_key(stats_history)
        return stats_history[first_element]

    logger.info("No STAT_MANAGER set in .env file!")
    return None

def query_service_for_dividend_history(ticker):
    """
    Description
    -----------
    Makes HTTP request to the DIV_MANAGER defined in the settings.py and configured through the DIV_MANAGER environment variable. \n \n 

    Parameters
    ----------
    1. ticker : str \n 
        Required. Tickery symbol of the equity whose dividend history is to be retrieved. \n \n 
    """
    if settings.DIV_MANAGER == "iex":
        
        query=f'{ticker}/{settings.PATH_IEX_DIV}/{settings.PARAM_IEX_RANGE_5YR}'
        url = f'{settings.IEX_URL}/{query}?{settings.PARAM_IEX_KEY}={settings.IEX_KEY}'
    
        logger.debug(f'IEX Cloud Path Query (w/o key) = {query}')
        response = requests.get(url).json()

        formatted_response = {}

        for item in response:
            date_string = str(item[settings.IEX_RES_DATE_KEY])
            div_string = item[settings.IEX_RES_DIV_KEY]
            formatted_response[date_string] = div_string

        return formatted_response

def get_dividend_history(ticker):
    logger.debug(f'Checking for {ticker} dividend history in cache.')

    dividends = files.retrieve_local_object(local_object=files.OBJECTS['dividends'],
                                            args={"ticker": ticker})
    if dividends is not None:
        return dividends

    logger.debug(f'Retrieving {ticker} prices from Service Manager.')  
    dividends = query_service_for_dividend_history(ticker=ticker)

    logger.debug(f'Storing {ticker} price history in cache.')
    files.store_local_object(local_object=files.OBJECTS['dividends'], value=dividends, args={"ticker": ticker})
    return dividends

def get_percent_stat_symbols():
    if settings.STAT_MANAGER == 'quandl':
        percent_stats = settings.ARG_Q_YIELD_CURVE.values()
        return percent_stats

# NOTE: Quandl outputs interest in percentage terms. 
# TODO: verify the interest rate is annual. may need to convert.
def get_risk_free_rate():
    """
    Description
    -----------
    Returns the risk free rate as a decimal. The risk free rate is defined in the `settings.py` file and is configured through the RISK_FREE environment variable. \n \n 
    """
    risk_free_rate_key = settings.RISK_FREE_RATE
    risk_free_rate = get_daily_stats_latest(statistic=risk_free_rate_key)
    return (risk_free_rate)/100