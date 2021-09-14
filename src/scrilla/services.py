import itertools, time, requests

from scrilla import settings, errors, cache, static
import scrilla.util.outputter as outputter
import scrilla.util.helper as helper

logger = outputter.Logger("services", settings.LOG_LEVEL)

class StatManager():
    """
    Description
    -----------
        StatManager is an interface between the application and the external services that hydrate it with financial statistics data. This class gets instantiated on the level of the scrilla.services module with the value defined in `scrilla.settings.STAT_MANAGER`. This value is in turn defined by the value of the `STAT_MANAGER` environment variable. This value determines how the url is constructed, which API credentials get appended to the external query and the keys used to parse the response JSON container the statistical data.
    """
    def __init__(self, type):
        self.type = type

    def construct_url(self, symbol, start_date, end_date):
        if self.type == static.keys['SERVICES']['STATISTICS']['QUANDL']['MANAGER']:
            url = f'{settings.Q_URL}/'
            query = f'{settings.PATH_Q_FRED}/{symbol}?'
    
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
            return url
        raise errors.ConfigurationError('No STAT_MANAGER found in the parsed environment settings')

    def get_stats(self, symbol, start_date, end_date):
        url = self.construct_url(symbol, start_date, end_date)
        response = requests.get(url).json()

        if self.type == static.keys['SERVICES']['STATISTICS']['QUANDL']['MANAGER']:

            raw_stat = response[settings.Q_FIRST_LAYER][settings.Q_SECOND_LAYER]
            formatted_stat = {}
        
            for stat in raw_stat:
                formatted_stat[stat[0]] = stat[1]
            return formatted_stat

        raise errors.ConfigurationError('No STAT_MANAGER found in the parsed environment settings')

class DividendManager():
    
    def __init__(self, type):
        self.type = type

    @staticmethod
    def construct_url(ticker):
        if settings.DIV_MANAGER == "iex":
        
            query=f'{ticker}/{settings.PATH_IEX_DIV}/{settings.PARAM_IEX_RANGE_5YR}'
            url = f'{settings.IEX_URL}/{query}?{settings.PARAM_IEX_KEY}={settings.IEX_KEY}'
    
            logger.debug(f'IEX Cloud Path Query (w/o key) = {query}')

            return url
            
        raise errors.ConfigurationError('No DIV_MANAGER found in the parsed environment settings')

    def get_dividends(self, ticker):
        url = self.construct_url(ticker)
        response = requests.get(url).json()

        formatted_response = {}

        for item in response:
            date = str(item[settings.IEX_RES_DATE_KEY])
            div = item[settings.IEX_RES_DIV_KEY]
            formatted_response[date] = div
        
        return formatted_response

class PriceManager():
    """
    Description
    -----------
        PriceManager is an interface between the application and the external services that hydrate it with price data. This class gets instantiated on the level of the scrilla.services module with the value defined in `scrilla.settings.PRICE_MANAGER`. This value is in turn defined by the value of the `PRICE_MANAGER` environment variable. This value determines how the url is constructed, which API credentials get appended to the external query and the keys used to parse the response JSON containing the price data. \n \n

    Methods 
    -------
    1. construct_url:
        Parameters
        ----------
        1. ticker : str \n
            Required. Ticker symbol of the asset whose prices are being retrieved. \n \n
        2. asset_type : str \n
            Required: Asset type of the asset whose prices are being retrieved. Options are statically
            accessible in the `scrillla.static` module dictionary `scrilla.static.keys['ASSETS']`. \n \n

        Returns
        -------
            The URL with the authenticated query appended, i.e. with the service's API key injected into the parameters. Be careful not to expose the return value of this function! \n \n

        Raises
        ------
        1. errors.ConfigurationError \n
            If one of the settings is improperly configured or one of the environment variables was unable to be parsed from the environment, this error will be thrown. \n \n

    2. get_prices 
        Parameters
        ----------
        1. ticker : str \n
            Required. Ticker symbol of the asset whose prices are being retrieved. \n \n
        2. asset_type : str \n
            Required: Asset type of the asset whose prices are being retrieved. Options are statically
            accessible in the `scrillla.static` module dictionary `scrilla.static.keys['ASSETS']`. \n \n
        
        Returns
        -------

        Raises
        ------
        1. errors.ConfigurationError \n
            If one of the settings is improperly configured or one of the environment variables was unable to be parsed from the environment, this error will be thrown. \n \n
        2. errors.APIResponseError \n
            If the service from which data is being retrieved is down, the request has been rate limited or some otherwise anomalous event has taken place, this error will be thrown. \n \n

    3. slice_prices
        Parameters
        ----------
        1. start_date : datetime.date \n 
        2. end_date : datetime.date \n
        3. asset_type : str \n
            Required: Asset type of the asset whose prices are being retrieved. Options are statically
            accessible in the `scrillla.static` module dictionary `scrilla.static.keys['ASSETS']`. \n \n
        4. response : dict \n
            Required: the full response from the price manager, i.e. the entire price history returned by the external service in charge of retrieving pricce histories. \n \n
       
        Returns
        -------

        Raises
        ------
        1. KeyError \n
            If the inputted or validated dates do not exist in the price history, a KeyError will be thrown. This could be due to the equity not having enough price history, i.e. it started trading a month ago and doesn't have 100 days worth of prices yet, or some other anomalous event in an equity's history. 
        2. errors.ConfigurationError \n
            If one of the settings is improperly configured or one of the environment variables was unable to be parsed from the environment, this error will be thrown. \n \n
    
    4. parse_price_from_date
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
            accessible in the `scrillla.static` module dictionary `scrilla.static.keys['ASSETS']` \n \n
        4. which_price : str \n
            String that specifies which price is to be retrieved, the closing price or the opening prices. Options are statically accessible 
    
        Returns
        ------
            String containing the price on the specified date.
        
        Raises
        ------
        1. KeyError \n
            If the inputted or validated dates do not exist in the price history, a KeyError will be thrown. This could be due to the equity not having enough price history, i.e. it started trading a month ago and doesn't have 100 days worth of prices yet, or some other anomalous event in an equity's history. 
        2. errors.InputValidationError \n
            If prices was unable to be grouped into a (crypto, equity)-asset class or the opening/closing price did not exist for whatever reason, this error will be thrown.
    """
    def __init__(self, type):
        self.type = type

    def construct_url(self, ticker, asset_type):
        if self.type == static.keys['SERVICES']['PRICES']['ALPHA_VANTAGE']['MANAGER']:
            query = f'{settings.PARAM_AV_TICKER}={ticker}'

            if asset_type == static.keys['ASSETS']['EQUITY']:
                query += f'&{settings.PARAM_AV_FUNC}={settings.ARG_AV_FUNC_EQUITY_DAILY}'
            elif asset_type == static.keys['ASSETS']['CRYPTO']:
                query += f'&{settings.PARAM_AV_FUNC}={settings.ARG_AV_FUNC_CRYPTO_DAILY}&{settings.PARAM_AV_DENOM}={static.constants["DENOMINATION"]}'

                    # NOTE: only need to modify EQUITY query, CRYPTO always returns full history
            if (asset_type == static.keys['ASSETS']['EQUITY']):
                query += f'&{settings.PARAM_AV_SIZE}={settings.ARG_AV_SIZE_FULL}'

            auth_query = query + f'&{settings.PARAM_AV_KEY}={settings.AV_KEY}'
            url=f'{settings.AV_URL}?{auth_query}'  
            logger.debug(f'AlphaVantage query (w/o key) = {query}') 
            return url

        raise errors.ConfigurationError('No PRICE_MANAGER found in the parsed environment settings')


    def get_prices(self, ticker, start_date, end_date, asset_type):
        url = self.construct_url(ticker, asset_type)
        response = requests.get(url).json()

        if self.type == static.keys['SERVICES']['PRICES']['ALPHA_VANTAGE']['MANAGER']:
            first_element = helper.get_first_json_key(response)
            # end function is daily rate limit is reached 
            if first_element == settings.AV_RES_DAY_LIMIT:
                raise errors.APIResponseError(response[settings.AV_RES_DAY_LIMIT])
                # check for bad response
            if first_element == settings.AV_RES_ERROR:
                raise errors.APIResponseError(response[settings.AV_RES_ERROR])

            # check and wait for API rate limit refresh
            first_pass, first_element = True, helper.get_first_json_key(response)

            while first_element == settings.AV_RES_LIMIT:
                if first_pass:
                    logger.debug('AlphaVantage API rate limit per minute exceeded. Waiting.')
                    first_pass = False
                else:
                    logger.debug('Waiting.')
                
                time.sleep(static.constants['BACKOFF_PERIOD'])
                response = requests.get(url).json()
                first_element = helper.get_first_json_key(response)

                if first_element == settings.AV_RES_ERROR:
                    raise errors.APIResponseError(response[settings.AV_RES_ERROR])

            return self.slice_prices(start_date=start_date, end_date=end_date, asset_type=asset_type, prices=response)
        
        raise errors.ConfigurationError('No PRICE_MANAGER found in the parsed environment settings')

    def slice_prices(self, start_date, end_date, asset_type, prices):
        # NOTE: only really needed for `alpha_vantage` responses so far, due to the fact AlphaVantage either returns everything or 100 days or prices.
        if self.type == static.keys['SERVICES']['PRICES']['ALPHA_VANTAGE']['MANAGER']:
            # NOTE: Remember AlphaVantage is ordered current to earliest. END_INDEX is 
            # actually the beginning of slice and START_INDEX is actually end of slice. 
            try:
                start_string, end_string = helper.date_to_string(start_date), helper.date_to_string(end_date)
                if asset_type == static.keys['ASSETS']['EQUITY']:
                    start_index = list(prices[settings.AV_RES_EQUITY_FIRST_LAYER].keys()).index(start_string)
                    end_index = list(prices[settings.AV_RES_EQUITY_FIRST_LAYER].keys()).index(end_string)
                    prices = dict(itertools.islice(prices[settings.AV_RES_EQUITY_FIRST_LAYER].items(), end_index, start_index+1))
                    return prices
                if asset_type == static.keys['ASSETS']['CRYPTO']:
                    start_index = list(prices[settings.AV_RES_CRYPTO_FIRST_LAYER].keys()).index(start_string)
                    end_index = list(prices[settings.AV_RES_CRYPTO_FIRST_LAYER].keys()).index(end_string)
                    prices = dict(itertools.islice(prices[settings.AV_RES_CRYPTO_FIRST_LAYER].items(), end_index, start_index+1))
                    return prices
                
            except KeyError as ke:
                raise ke
        
        raise errors.ConfigurationError('No PRICE_MANAGER found in the parsed environment settings')
    
    def parse_price_from_date(self, prices, date, asset_type, which_price):
        try:
            if self.type== 'alpha_vantage':
                if asset_type == static.keys['ASSETS']['EQUITY']:
                    if which_price == static.keys['PRICES']['CLOSE']:
                        return prices[date][settings.AV_RES_EQUITY_CLOSE_PRICE]
                    if which_price == static.keys['PRICES']['OPEN']:
                        return prices[date][settings.AV_RES_EQUITY_OPEN_PRICE]

                elif asset_type == static.keys['ASSETS']['CRYPTO']:
                    if which_price == static.keys['PRICES']['CLOSE']:
                        return prices[date][settings.AV_RES_CRYPTO_CLOSE_PRICE]
                    if which_price == static.keys['PRICES']['OPEN']:
                        return prices[date][settings.AV_RES_CRYPTO_OPEN_PRICE]
            
            raise errors.InputValidationError(f'Verify {asset_type}, {which_price} are allowable values')

        except KeyError as ke:
            logger.debug('Price unable to be parsed from date.')
            raise ke

price_manager = PriceManager(settings.PRICE_MANAGER)
stat_manager = StatManager(settings.STAT_MANAGER)
div_manager = DividendManager(settings.DIV_MANAGER)
price_cache = cache.PriceCache()        
stat_cache = cache.StatCache()
div_cache = cache.DividendCache()

def get_daily_price_history(ticker, start_date=None, end_date=None, asset_type=None):
    """
    Description
    -----------
    Wrapper around external service request for price data. Relies on an instance of `PriceManager` configured by `settings.PRICE_MANAGER` value, which in turn is configured by the `PRICE_MANAGER` environment variable, to hydrate with data. \n \n
    
    Before deferring to the `PriceManager` and letting it call the external service, however, this function checks if response is in local cache. If the response is not in the cache, it will pass the request off to `PriceManager` and then save the response in the cache so subsequent calls to the function can bypass the service request. Used to prevent excessive external HTTP requests and improve the performance of the application. Other parts of the program should interface with the external price data services through this function to utilize the cache functionality.  \n \n

    Parameters
    ----------
    1. ticker :  str  \n
        Required. Ticker symbol corresponding to the price history to be retrieved. \n \n
    2. start_date : datetime.date \n 
        Optional. Start date of price history. Defaults to None. If `start_date is None`, the calculation is made as if the `start_date` were set to 100 trading days ago. If `get_asset_type(ticker)=="crypto"`, this includes weekends and holidays. If `get_asset_type(ticker)=="equity"`, this excludes weekends and holidays. \n \n
    3. end_date : datetime.date \n 
        Optional End date of price history. Defaults to None. If `end_date is None`, the calculation is made as if the `end_date` were set to today. If `get_asset_type(ticker)=="crypto"`, this means today regardless. If `get_asset_type(ticker)=="equity"`, this excludes weekends and holidays so that `end_date` is set to the previous business date. \n \n
    4. asset_type : string \n
        Optional. Asset type of the ticker whose history is to be retrieved. Used to prevent excessive calls to IO and list searching. `asset_type` is determined by comparing the ticker symbol `ticker` to a large static list of ticker symbols maintained in installation directory's /data/static/ subdirectory, which can slow the program down if the file is constantly accessed and lots of comparison are made against it. Once an `asset_type` is calculated, it is best to preserve it in the process environment somehow, so this function allows the value to be passed in. If no value is detected, it will make a call to the aforementioned directory and parse the file to determine to the `asset_type`. Asset types are statically accessible through the `scrilla.static.keys['ASSETS']` dictionary. \n \n

    Raises
    ------
    1. scrilla.errors.InputValidationError \n
        If the arguments inputted into the function fail to exist within the domain the function, this error will be thrown.
    2. scrilla.errors.APIResponseError \n
        If the external service rejects the request for price data, whether because of rate limits or some other factor, the function will raise this exception.
    3. KeyError \n
        If the inputted or validated dates do not exist in the price history, a KeyError will be thrown. This could be due to the equity not having enough price history, i.e. it started trading a month ago and doesn't have 100 days worth of prices yet, or some other anomalous event in an equity's history. 
    4. errors.ConfigurationError \n
        If one of the settings is improperly configured or one of the environment variables was unable to be parsed from the environment, this error will be thrown. \n \n

    Returns
    ------
    { 'date' (str) : { 'open': value (str), 'close': value (str) }, 'date' (str): { 'open' : value (str), 'close' : value(str) }, ... }
        Dictionary with date strings formatted `YYYY-MM-DD` as keys and a nested dictionary containing the 'open' and 'close' price as values. Ordered from latest to earliest. \n \n
    
    Notes
    -----
    1. The default analysis period, if no `start_date` and `end_date` are specified, is determined by the *DEFAULT_ANALYSIS_PERIOD" variable in the `settings,py` file. The hardcoded value of this setting is 100. Should probably put this variable into the enviroment in the future and allow user to configure it. \n \n
    """
    try:
        asset_type = errors.validate_asset_type(ticker, asset_type)
        start_date, end_date = errors.validate_dates(start_date, end_date, asset_type)
    except errors.InputValidationError as ive:
        raise ive

    prices = price_cache.filter_price_cache(ticker=ticker, start_date=start_date, end_date=end_date)

    # if end_date not in prices.keys() or if prices != days_between(start, end), then cache is out of date
    if prices is not None and helper.date_to_string(end_date) in prices.keys() and (
        (asset_type == static.keys['ASSETS']['EQUITY']
            and (helper.business_days_between(start_date, end_date) + 1) == len(prices))
        or 
        (asset_type == static.keys['ASSETS']['CRYPTO']
            and (helper.days_between(start_date, end_date) + 1) == len(prices))
    ):
        return prices
        
    try:
        prices = price_manager.get_prices(ticker=ticker,start_date=start_date, end_date=end_date, asset_type=asset_type)
    except errors.APIResponseError as api:
        raise api
    except errors.InputValidationError as ive:
        raise ive

    parsed_prices ={}
    for date in prices:
        close_price = price_manager.parse_price_from_date(prices=prices, date=date, asset_type=asset_type, 
                                                    which_price=static.keys['PRICES']['CLOSE'])
        open_price = price_manager.parse_price_from_date(prices=prices, date=date, asset_type=asset_type, 
                                                    which_price=static.keys['PRICES']['OPEN'])
        parsed_prices[date] = { static.keys['PRICES']['OPEN'] : open_price, static.keys['PRICES']['CLOSE'] : close_price }
        price_cache.save_row(ticker=ticker, date=date, open_price=open_price, close_price=close_price)

    return parsed_prices
    
def get_daily_price_latest(ticker, asset_type=None):
    """
    Description
    -----------
    Returns the latest closing price. \n \n

    Parameters
    ----------
    1. ticker: str \n 
        Required: ticker symbol whose latest closing price is to be retrieved. \n \n
    2. asset_type : string \n
        Optional. Asset type of the ticker whose history is to be retrieved. Will be calculated from the `ticker` symbol if not provided. \n \n
    """
    prices = get_daily_price_history(ticker=ticker,asset_type=asset_type)
    if prices is not None:
        first_element = helper.get_first_json_key(prices)
        return prices[first_element][static.keys['PRICES']['OPEN']]
    return None

def get_daily_stats_history(symbol, start_date=None, end_date=None):
    """
    Description
    -----------
    Wrapper around external service request for financial statistics data. Relies on an instance of `StatManager` configured by `settings.STAT_MANAGER` value, which in turn is configured by the `STAT_MANAGER` environment variable, to hydrate with data. \n \n
    
    Before deferring to the `StatManager` and letting it call the external service, however, this function checks if response is in local cache. If the response is not in the cache, it will pass the request off to `StatManager` and then save the response in the cache so subsequent calls to the function can bypass the service request. Used to prevent excessive external HTTP requests and improve the performance of the application. Other parts of the program should interface with the external statistics data services through this function to utilize the cache functionality.  \n \n

    Parameters
    ----------
    1. symbol: str \n 
        Required. Symbol representing the statistic whose history is to be retrieved. List of allowable values can be found here: https://www.quandl.com/data/FRED-Federal-Reserve-Economic-Data/documentation \n \n
     2. start_date : datetime.date \n 
        Optional. Start date of price history. Defaults to None. If `start_date is None`, the calculation is made as if the `start_date` were set to 100 trading days ago. This excludes weekends and holidays. \n \n
    3. end_date : datetime.date \n 
        Optional End date of price history. Defaults to None. If `end_date is None`, the calculation is made as if the `end_date` were set to today. This excludes weekends and holidays so that `end_date` is set to the last previous business date. \n \n
    
    Raises
    ------
    1. scrilla.errors.InputValidationError \n
        If the arguments inputted into the function fail to exist within the domain the function, this error will be thrown.
    2. scrilla.errors.APIResponseError \n
        If the external service rejects the request for price data, whether because of rate limits or some other factor, the function will raise this exception.
    3. KeyError \n
        If the inputted or validated dates do not exist in the price history, a KeyError will be thrown. This could be due to the equity not having enough price history, i.e. it started trading a month ago and doesn't have 100 days worth of prices yet, or some other anomalous event in an equity's history. 
    4. errors.ConfigurationError \n
        If one of the settings is improperly configured or one of the environment variables was unable to be parsed from the environment, this error will be thrown. \n \n

    Returns
    ------
    { 'date' (str) :  value (str),  'date' (str):  value (str), ... }
        Dictionary with date strings formatted `YYYY-MM-DD` as keys and the statistic on that date as the corresponding value. \n \n
    """
    try:
            # NOTE: financial statistics aren't reported on weekends or holidays, so their date validation is functionally
            #       equivalent to an equity's date validation.
        start_date,end_date=errors.validate_dates(start_date=start_date, end_date=end_date, asset_type=static.keys['ASSETS']['EQUITY'])
    except errors.InputValidationError as ive:
        raise ive

    stats = stat_cache.filter_stat_cache(symbol=symbol, start_date=start_date, end_date=end_date)

    if stats is not None: # or in end_date is not in stats.keys() ? 
        return stats

    try:
        stats = stat_manager.get_stats(symbol=symbol, start_date=start_date, end_date=end_date)
    except errors.APIResponseError as api:
        raise api
    except errors.InputValidationError as ive:
        raise ive
    # TODO: see other cache filters todos. Need to be more careful with new information. cache is NOT the source of truth. basically, need to check if the len(stats) = dates_between(start, end) and that start_Date in stat.keys() and end_date in stat.keys()!

    for date in stats:
        stat_cache.save_row(symbol=symbol, date=date, value=stats[date])

    return stats

def get_daily_stats_latest(symbol):
    """
    Description
    -----------
    Returns the latest value for the inputted statistic symbol. \n \n

    Parameters
    ----------
    1. statistic: str \n 
        Required. Symbol representing the statistc whose value it to be retrieved. \n \n
    """
    stats_history = get_daily_stats_history(symbol=symbol)
    first_element = helper.get_first_json_key(stats_history)
    return stats_history[first_element]


def get_dividend_history(ticker):
    """
    Description
    -----------
    Wrapper around external service request for dividend payment data. Relies on an instance of `DivManager` configured by `settings.DIV_MANAGER` value, which in turn is configured by the `DIV_MANAGER` environment variable, to hydrate with data. \n \n
    
    Before deferring to the `DivManager` and letting it call the external service, however, this function checks if response is in local cache. If the response is not in the cache, it will pass the request off to `DivManager` and then save the response in the cache so subsequent calls to the function can bypass the service request. Used to prevent excessive external HTTP requests and improve the performance of the application. Other parts of the program should interface with the external statistics data services through this function to utilize the cache functionality.  \n \n

    Parameters
    ----------
    1. ticker : str \n 
        Required. Ticker symbol of the equity whose dividend history is to be retrieved. \n \n 
    
    Raises
    ------
    1. scrilla.errors.InputValidationError \n
        If the arguments inputted into the function fail to exist within the domain the function, this error will be thrown.
    2. scrilla.errors.APIResponseError \n
        If the external service rejects the request for price data, whether because of rate limits or some other factor, the function will raise this exception.
    3. KeyError \n
        If the inputted or validated dates do not exist in the price history, a KeyError will be thrown. This could be due to the equity not having enough price history, i.e. it started trading a month ago and doesn't have 100 days worth of prices yet, or some other anomalous event in an equity's history. 
    4. errors.ConfigurationError \n
        If one of the settings is improperly configured or one of the environment variables was unable to be parsed from the environment, this error will be thrown. \n \n

    Returns
    ------
    { 'date' (str) :  amount (str),  'date' (str):  amount (str), ... }
        Dictionary with date strings formatted `YYYY-MM-DD` as keys and the dividend payment amount on that date as the corresponding value. \n \n
    """
    logger.debug(f'Checking for {ticker} dividend history in cache.')
    divs = div_cache.filter_dividend_cache(ticker=ticker)

    if divs is not None:
        # TODO: same as others
        return divs 

    try:
        logger.debug(f'Retrieving {ticker} dividends from service')  
        divs = div_manager.get_dividends(ticker=ticker)
    except errors.APIResponseError as api:
        raise api
    except errors.InputValidationError as ive:
        raise ive
    
    logger.debug(f'Storing {ticker} dividend history in cache.')

    for date in divs:
        div_cache.save_row(ticker=ticker, date=date, amount=divs[date])

    return divs


# NOTE: Quandl outputs interest in percentage terms. 
# TODO: verify the interest rate is annual. may need to convert.
def get_risk_free_rate():
    """
    Description
    -----------
    Returns the risk free rate, defined as the annualized yield on a specific US Treasury duration, as a decimal. The US Treasury yield used as a proxy for the risk free rate is defined in the `settings.py` file and is configured through the RISK_FREE environment variable. \n \n 
    """
    risk_free_rate_key = settings.RISK_FREE_RATE
    risk_free_rate = get_daily_stats_latest(symbol=risk_free_rate_key)
    return (risk_free_rate)/100