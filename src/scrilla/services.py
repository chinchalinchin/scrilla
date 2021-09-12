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

class InputValidationError(Exception):
    def __init__(self, message):
        super().__init__(message)

class APIResponseError(Exception):
    def __init__(self, message):
        super().__init__(message)


def validate_dates(start_date, end_date, asset_type):
    # verify dates are in order if they exist
    if end_date is not None and start_date is not None:
        start_date, end_date = helper.validate_order_of_dates(start_date, end_date)

    # if end date exists, make sure it is valid
    if end_date is not None:
        end_date = helper.truncate_future_from_date(end_date)
        if asset_type == settings.ASSET_EQUITY and not helper.is_trading_date(end_date):
            end_date = helper.get_previous_business_date(end_date)
    # else create a sensible end date
    else:
        if asset_type == settings.ASSET_CRYPTO:
            end_date = helper.get_today()
        else:
            end_date = helper.get_last_trading_date()        

    # if start date exists, make sure it is valide
    if start_date is not None:
        if helper.is_future_date(start_date):
            # only invalid user input is if start date doesn't exist yet
            raise InputValidationError(f'Start Date of {helper.date_to_string(start_date)} is in the future')

        if asset_type == settings.ASSET_EQUITY and not helper.is_trading_date(start_date):
            start_date = helper.get_previous_business_date(start_date)

    # else create a sensible start date
    else:
        if asset_type == settings.ASSET_CRYPTO:
            start_date = helper.decrement_date_by_days(end_date, settings.DEFAULT_ANALYSIS_PERIOD)
        else:
            start_date = helper.decrement_date_by_business_days(end_date, settings.DEFAULT_ANALYSIS_PERIOD)

    return start_date, end_date    


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
    String containing the price on the specified date or None if price unable to be parsed.
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
        logger.debug('Price unable to be parsed from date.')
        return None

def query_service_for_daily_price_history(ticker, start_date=None, end_date=None, asset_type=None):
    """
    Description
    -----------
    Function in charge of querying external services for daily price history. \n \n

    Parameters
    ----------
    1. ticker : [ str ] \n
        Required. Ticker symbol corresponding to the price history to be retrieved. \n \n
    2. start_date : datetime.date \n 
        Optional. Start date of price history. Defaults to None. If `start_date is None`, the calculation is made as if the `start_date` were set to 100 trading days ago. If `get_asset_type(ticker)=="crypto"`, this includes weekends and holidays. If `get_asset_type(ticker)=="equity"`, this excludes weekends and holidays. \n \n
    3. end_date : datetime.date \n 
        Optional End date of price history. Defaults to None. If `end_date is None`, the calculation is made as if the `end_date` were set to today. If `get_asset_type(ticker)=="crypto"`, this means today regardless. If `get_asset_type(ticker)=="equity"`, this excludes weekends and holidays and `end_date` is set to the previous business date. \n \n
    4. asset_type : string \n
        Optional. Asset type of the ticker whose history is to be retrieved. Used to prevent excessive calls to IO and list searching. `asset_type` is determined by comparing the ticker symbol `ticker` to a large static list of ticker symbols maintained in installation directory's /data/static/ subdirectory, which can slow the program down if the file is constantly accessed and lots of comparison are made against it. Once an asset_type is calculated, it is best to preserve it in the process environment somehow, so this function allows the value to be passed in. If no value is detected, it will make a call to the aforementioned directory and parse the file to determine to the `asset_type`. There may be a better way of doing this, in fact I imagine there is, but for now, this works. If it starts getting too complicated as the program grows, this is the first area that should be refactored, i.e. how to preserve a ticker's asset type in memory instead of determining it from a large IO file. 
    Raises
    ------
    1. InputValidationException \n
    2. APIErrorException \n

    Notes
    -----
    The default analysis period, if no `start_date` and `end_date` are specified, is determined by the *DEFAULT_ANALYSIS_PERIOD* variable in the `settings,py` file. The hardcoded value of this setting is 100. Should probably put this variable into the enviroment in the future and allow user to configure it. 
    """
    if asset_type is not None:
        asset_type = files.get_asset_type(ticker) 

    try:
        validate_dates(start_date, end_date, asset_type)
    except InputValidationError as ive:
        raise ive

    ### START: Service Query ###
    if settings.PRICE_MANAGER == "alpha_vantage":

        ### START: AlphaVantage Service Query ###
        query = f'{settings.PARAM_AV_TICKER}={ticker}'

        if asset_type == settings.ASSET_EQUITY:
            query += f'&{settings.PARAM_AV_FUNC}={settings.ARG_AV_FUNC_EQUITY_DAILY}'
        elif asset_type == settings.ASSET_CRYPTO:
            query += f'&{settings.PARAM_AV_FUNC}={settings.ARG_AV_FUNC_CRYPTO_DAILY}&{settings.PARAM_AV_DENOM}={settings.DENOMINATION}'

            # NOTE: only need to modify EQUITY query, CRYPTO always returns full history
        if (asset_type == settings.ASSET_EQUITY):
            query += f'&{settings.PARAM_AV_SIZE}={settings.ARG_AV_SIZE_FULL}'

        auth_query = query + f'&{settings.PARAM_AV_KEY}={settings.AV_KEY}'
        url=f'{settings.AV_URL}?{auth_query}'  
        logger.debug(f'AlphaVantage query (w/o key) = {query}')   
        
        prices = requests.get(url).json()
        first_element = helper.get_first_json_key(prices)

            # check for bad response
        if first_element == settings.AV_RES_ERROR:
            raise APIResponseError(prices[settings.AV_RES_ERROR])

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
                raise APIResponseError('Daily AlphaVantage rate limit exceeded. No more queries possible!')
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

    files.store_local_object(local_object=files.OBJECTS['prices'], value=prices, 
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

        if start_date is not None and end_date is not None:
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