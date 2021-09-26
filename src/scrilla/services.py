# This file is part of scrilla: https://github.com/chinchalinchin/scrilla.

# scrilla is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 3
# as published by the Free Software Foundation.

# scrilla is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with scrilla.  If not, see <https://www.gnu.org/licenses/>
# or <https://github.com/chinchalinchin/scrilla/blob/develop/main/LICENSE>.

import itertools, time, datetime, requests
from typing import Union

from scrilla import settings, errors, cache, static
import scrilla.util.outputter as outputter
import scrilla.util.helper as helper

logger = outputter.Logger("services", settings.LOG_LEVEL)

class StatManager():
    """
    Description
    -----------
        StatManager is an interface between the application and the external services that hydrate it with financial statistics data. This class gets instantiated on the level of the `scrilla.services` module with the value defined in `scrilla.settings.STAT_MANAGER`. This value is in turn defined by the value of the `STAT_MANAGER` environment variable. This value determines how the url is constructed, which API credentials get appended to the external query and the keys used to parse the response JSON container the statistical data.
    """
    def __init__(self, type):
        self.type = type
        if self.is_quandl():
            self.service_map = static.keys["SERVICES"]["STATISTICS"]["QUANDL"]["MAP"]

    def is_quandl(self):
        """
        Returns
        -------
        bool \n
            `True` if this instace of `StatManager` is a Quandl interface. `False` otherwise. \n\n

        .. notes::
            * This is for use within the class and probably won't need to be accessed outside of it. `StatManager` is intended to hide the data implementation from the rest of the library, i.e. it is ultimately agnostic about where the data comes where. It should never need to know `StatManger` is a Quandl interface. Just in case the library ever needs to populate its data from another source. \n \n

        """
        if self.type == static.keys['SERVICES']['STATISTICS']['QUANDL']['MANAGER']:
            return True
        return False

    def construct_query(self, start_date : datetime.date, end_date: datetime.date) -> str:
        """
        Description
        -----------
        Constructs and formats the query parameters for the external statistics service. Note, this method appends the API key to the query. Be careful with the returned value.

        Parameters
        ----------
        1. start_date : datetime.date \n 
            Start date of historical sample to be retrieved. \n \n
        2. end_date : datetime.date \n 
            End date of historical sample to be retrieved. \n \n

        Raises
        ------
        1. scrilla.errors.ConfigurationError \n
            If the `STAT_MANAGER` hasn't been set through an enviornment variable, this error will be thrown. \n \n

        Returns
        -------
        str \n
            The formatted query for the specific service defined by `self.type`. \n \n

        """
        query = ""
        if self.is_quandl():

            if end_date is not None:
                end_string = helper.date_to_string(end_date)
                query += f'&{self.service_map["PARAMS"]["END"]}={end_string}' 

            if start_date is not None:
                start_string = helper.date_to_string(start_date)
                query += f'&{self.service_map["PARAMS"]["START"]}={start_string}'
        
            logger.debug(f'Quandl query (w/o key) = {query}')

            if query:
                return f'{query}&{self.service_map["PARAMS"]["KEY"]}={settings.Q_KEY}'

            return f'{self.service_map["PARAMS"]["KEY"]}={settings.Q_KEY}'
        raise errors.ConfigurationError('No STAT_MANAGER found in the parsed environment settings')



    def construct_stat_url(self, symbol, start_date, end_date):
        """
        Description
        -----------
        Constructs the full URL path for the external statistics service. Note, this method will return the URL with an API key appended as a query parameter. Be careful with the returned value. \n\n

        Parameters
        ----------
        1. symbol: str \n
            Symbol representing the statistical series to be retrieved. List of allowable symbols can be found here: https://data.nasdaq.com/data/FRED-federal-reserve-economic-data
        2. start_date : datetime.date \n 
            Start date of historical sample to be retrieved. \n \n
        3. end_date : datetime.date \n 
            End date of historical sample to be retrieved. \n \n
 
        Raises
        ------
        1. scrilla.errors.ConfigurationError \n
            If the `STAT_MANAGER` hasn't been set through an enviornment variable, this error will be thrown. \n \n

        Returns
        -------
        str \n
            The formatted URL for the specific statistics service defined by `self.type`. \n \n
        """
        if self.is_quandl():
            url = f'{settings.Q_URL}/{self.service_map["PATHS"]["FRED"]}/{symbol}?'
            url += self.construct_query(start_date, end_date)
            return url
        raise errors.ConfigurationError('No STAT_MANAGER found in the parsed environment settings')

    def construct_interest_url(self,start_date, end_date):
        """
        Description
        -----------
        Constructs the full URL path for the external interest rate service. Note, this method will return the URL with an API key appended as a query parameter. Be careful with the returned value. \n\n

        Parameters
        ----------
        2. start_date : datetime.date \n 
            Start date of historical sample to be retrieved. \n \n
        3. end_date : datetime.date \n 
            End date of historical sample to be retrieved. \n \n
 
        Raises
        ------
        1. scrilla.errors.ConfigurationError \n
            If the `STAT_MANAGER` hasn't been set through an enviornment variable, this error will be thrown. \n \n

        Returns
        -------
        str \n
            The formatted URL for the specific interest rate service defined by `self.type`. \n \n

        .. notes::
            * The URL returned by this method will always contain a query for a historical range of US Treasury Yields, i.e. this method is specifically for queries involving the "Risk-Free" (right? right? *crickets*) Yield Curve. 
        """
        if self.is_quandl():
            url = f'{settings.Q_URL}/{self.service_map["PATHS"]["YIELD"]}?'
            url += self.construct_query(start_date=start_date, end_date=end_date)
            return url
        raise errors.ConfigurationError('No STAT_MANAGER found in the parsed environment settings')


    def get_stats(self, symbol, start_date, end_date):
        url = self.construct_stat_url(symbol, start_date, end_date)
        response = requests.get(url).json()

        if self.is_quandl():
            raw_stat = response[self.service_map["KEYS"]["FIRST_LAYER"]][self.service_map["KEYS"]["SECOND_LAYER"]]
            formatted_stat = {}
        
            for stat in raw_stat:
                formatted_stat[stat[0]] = stat[1]
            return formatted_stat

        raise errors.ConfigurationError('No STAT_MANAGER found in the parsed environment settings')

    def get_interest_rates(self, start_date, end_date):
        url = self.construct_interest_url(start_date=start_date, end_date=end_date)
        response = requests.get(url).json()

        if self.is_quandl():
            raw_interest = response[self.service_map["KEYS"]["FIRST_LAYER"]][self.service_map["KEYS"]["SECOND_LAYER"]]

            formatted_interest = {}
            for rate in raw_interest:
                formatted_interest[rate[0]] = rate[1:]
            return formatted_interest

        raise errors.ConfigurationError('No STAT_MANAGER found in the parsed environment settings')

    def format_for_maturity(self, maturity, results):
        try:
            maturity_key = static.keys['YIELD_CURVE'].index(maturity)
        except:
            raise errors.InputValidationError(f'{maturity} is not a valid maturity for US Treasury Bonds')

        if self.is_quandl():
            
            formatted_interest = {}
            for result in results:
                formatted_interest[result] = results[result][maturity_key]
            return formatted_interest
        
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
        str \n
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
                    logger.comment('AlphaVantage API rate limit per minute exceeded. Waiting...')
                    first_pass = False
                else:
                    logger.comment('Waiting...')
                
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
            service_map = static.keys['SERVICES']['PRICES']['ALPHA_VANTAGE']['MAP']

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
                service_map = static.keys['SERVICES']['PRICES']['ALPHA_VANTAGE']['MAP']

                if asset_type == static.keys['ASSETS']['EQUITY']:
                    if which_price == static.keys['PRICES']['CLOSE']:
                        return prices[date][service_map['KEYS']['EQUITY']['CLOSE']]
                    if which_price == static.keys['PRICES']['OPEN']:
                        return prices[date][service_map['KEYS']['EQUITY']['CLOSE']]

                elif asset_type == static.keys['ASSETS']['CRYPTO']:
                    if which_price == static.keys['PRICES']['CLOSE']:
                        return prices[date][service_map['KEYS']['CRYPTO']['CLOSE']]
                    if which_price == static.keys['PRICES']['OPEN']:
                        return prices[date][service_map['KEYS']['CRYPTO']['OPEN']]
            
            raise errors.InputValidationError(f'Verify {asset_type}, {which_price} are allowable values')

        except KeyError as ke:
            logger.debug('Price unable to be parsed from date.')
            raise ke

price_manager = PriceManager(settings.PRICE_MANAGER)
stat_manager = StatManager(settings.STAT_MANAGER)
div_manager = DividendManager(settings.DIV_MANAGER)
price_cache = cache.PriceCache()        
interest_cache = cache.InterestCache()

def get_daily_price_history(ticker: str, start_date : datetime.date=None, 
                            end_date: datetime.date =None, asset_type: str=None) -> list:
    """
    Wrapper around external service request for price data. Relies on an instance of `PriceManager` configured by `settings.PRICE_MANAGER` value, which in turn is configured by the `PRICE_MANAGER` environment variable, to hydrate with data. \n \n
    
    Before deferring to the `PriceManager` and letting it call the external service, however, this function checks if response is in local cache. If the response is not in the cache, it will pass the request off to `PriceManager` and then save the response in the cache so subsequent calls to the function can bypass the service request. Used to prevent excessive external HTTP requests and improve the performance of the application. Other parts of the program should interface with the external price data services through this function to utilize the cache functionality.

    Parameters
    ----------
    1. **ticker** :  ``str``
        Ticker symbol corresponding to the price history to be retrieved.
    2. **start_date** : ``datetime.date`` 
        *Optional*. Start date of price history. Defaults to None. If `start_date is None`, the calculation is made as if the `start_date` were set to 100 trading days ago. If `scrilla.files.get_asset_type(ticker)==scrill.static.keys['ASSETS']['CRYPTO']`, this includes weekends and holidays. If `scrilla.files.get_asset_type(ticker)==scrilla.static.keys['ASSETS']['EQUITY']`, this excludes weekends and holidays.
    3. **end_date** : ``datetime.date``
        Optional End date of price history. Defaults to None. If `end_date is None`, the calculation is made as if the `end_date` were set to today. If `scrilla.files.get_asset_type(ticker)==scrill.static.keys['ASSETS']['CRYPTO']`, this means today regardless. If `scrilla.files.get_asset_type(ticker)==scrilla.static.keys['ASSETS']['EQUITY']`, this excludes weekends and holidays so that `end_date` is set to the previous business date. 
    4. **asset_type** : ``string``
        *Optional*. Asset type of the ticker whose history is to be retrieved. Used to prevent excessive calls to IO and list searching. `asset_type` is determined by comparing the ticker symbol `ticker` to a large static list of ticker symbols maintained in installation directory's /data/static/ subdirectory, which can slow the program down if the file is constantly accessed and lots of comparison are made against it. Once an `asset_type` is calculated, it is best to preserve it in the process environment somehow, so this function allows the value to be passed in. If no value is detected, it will make a call to the aforementioned directory and parse the file to determine to the `asset_type`. Asset types are statically accessible through the `scrilla.static.keys['ASSETS']` dictionary.

    Returns
    ------
    ``dict``: `{ 'date' (str) : { 'open': value (str), 'close': value (str) }, 'date' (str): { 'open' : value (str), 'close' : value(str) }, ... }`, dictionary with date strings formatted `YYYY-MM-DD` as keys and a nested dictionary containing the 'open' and 'close' price as values. Ordered from latest to earliest.
    
    .. notes::
        * The default analysis period, if no `start_date` and `end_date` are specified, is determined by the *DEFAULT_ANALYSIS_PERIOD** variable in the `settings,py` file. The default value of this variable is 100.
    """
    asset_type = errors.validate_asset_type(ticker, asset_type)
    start_date, end_date = errors.validate_dates(start_date, end_date, asset_type)
    
    prices = price_cache.filter_price_cache(ticker=ticker, start_date=start_date, end_date=end_date)

    if prices is not None and helper.date_to_string(end_date) in prices.keys() and (
        (asset_type == static.keys['ASSETS']['EQUITY']
            and (helper.business_days_between(start_date, end_date) + 1) == len(prices))
        or 
        (asset_type == static.keys['ASSETS']['CRYPTO']
            and (helper.days_between(start_date, end_date) + 1) == len(prices))
    ):
        return prices

    if prices is not None:
        logger.debug(f'Cached {ticker} prices are out of date, passing request off to external service')
        
    prices = price_manager.get_prices(ticker=ticker,start_date=start_date, end_date=end_date, asset_type=asset_type)

    parsed_prices ={}
    for date in prices:
        close_price = price_manager.parse_price_from_date(prices=prices, date=date, asset_type=asset_type, 
                                                    which_price=static.keys['PRICES']['CLOSE'])
        open_price = price_manager.parse_price_from_date(prices=prices, date=date, asset_type=asset_type, 
                                                    which_price=static.keys['PRICES']['OPEN'])
        parsed_prices[date] = { static.keys['PRICES']['OPEN'] : open_price, static.keys['PRICES']['CLOSE'] : close_price }
        price_cache.save_row(ticker=ticker, date=date, open_price=open_price, close_price=close_price)

    return parsed_prices
    
def get_daily_price_latest(ticker: str, asset_type: str=None) -> float:
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

def get_daily_fred_history(symbol: str, start_date: datetime.date=None, end_date: datetime.date=None) -> list:
    """
    Description
    -----------
    Wrapper around external service request for financial statistics data constructed by the Federal Reserve Economic Data. Relies on an instance of `StatManager` configured by `settings.STAT_MANAGER` value, which in turn is configured by the `STAT_MANAGER` environment variable, to hydrate with data. \n \n
    
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
    4. scrilla.errors.ConfigurationError \n
        If one of the settings is improperly configured or one of the environment variables was unable to be parsed from the environment, this error will be thrown. \n \n

    Returns
    ------
    { 'date' (str) :  value (str),  'date' (str):  value (str), ... }
        Dictionary with date strings formatted `YYYY-MM-DD` as keys and the statistic on that date as the corresponding value. \n \n

    .. notes::
        * Most financial statistics are not reported on weekends or holidays, so the `asset_type` for financial statistics is functionally equivalent to equities, at least as far as date calculations are concerned. The dates inputted into this function are validated as if they were labelled as equity `asset_types` for this reason.

    Note: there are probably cases where this function will break because the statistical data isn't reported on a daily basis. In fact, there are tons of cases where this doesn't work...

    """
    try:
        start_date,end_date=errors.validate_dates(start_date=start_date, end_date=end_date, asset_type=static.keys['ASSETS']['EQUITY'])
    except errors.InputValidationError as ive:
        raise ive

    try:
        stats = stat_manager.get_stats(symbol=symbol, start_date=start_date, end_date=end_date)
    except errors.APIResponseError as api:
        raise api
    except errors.InputValidationError as ive:
        raise ive

    return stats

def get_daily_fred_latest(symbol: str) -> Union[float,None]:
    """
    Returns the latest value for the inputted statistic symbol.

    Parameters
    ----------
    1. **symbol**: str
        Symbol representing the statistic whose value it to be retrieved.
    """
    stats_history = get_daily_fred_history(symbol=symbol)
    if stats_history is not None:
        first_element = helper.get_first_json_key(stats_history)
        return stats_history[first_element]
    return None

def get_daily_interest_history(maturity: str, start_date: datetime.date=None, end_date: datetime.date=None) -> list:
    """
    Wrapper around external service request for US Treasury Yield Curve data. Relies on an instance of `StatManager` configured by `settings.STAT_MANAGER` value, which in turn is configured by the `STAT_MANAGER` environment variable, to hydrate with data.
    
    Before deferring to the `StatManager` and letting it call the external service, however, this function checks if response is in local cache. If the response is not in the cache, it will pass the request off to `StatManager` and then save the response in the cache so subsequent calls to the function can bypass the service request. Used to prevent excessive external HTTP requests and improve the performance of the application. Other parts of the program should interface with the external statistics data services through this function to utilize the cache functionality. 

    Parameters
    ----------
    1. **maturity** : ``str``
        Maturity of the US Treasury for which the interest rate will be retrieved. List of allowable values can in `scrilla.stats.keys['SERVICES']['STATISTICS']['QUANDL']['MAP']['YIELD_CURVE']`
    2. **start_date** : ``datetime.date``
        *Optional*. Start date of price history. Defaults to None. If `start_date is None`, the calculation is made as if the `start_date` were set to 100 trading days ago. This excludes weekends and holidays.
    3. **end_date** : ``datetime.date``` 
        *Optional*. End date of price history. Defaults to None. If `end_date is None`, the calculation is made as if the `end_date` were set to today. This excludes weekends and holidays so that `end_date` is set to the last previous business date.
    
    Raises
    ------
    1. **scrilla.errors.InputValidationError**
        If the arguments inputted into the function fail to exist within the domain the function, this error will be thrown.
    2. **scrilla.errors.APIResponseError**
        If the external service rejects the request for price data, whether because of rate limits or some other factor, the function will raise this exception.
    3. **KeyError**
        If the inputted or validated dates do not exist in the price history, a KeyError will be thrown. This could be due to the equity not having enough price history, i.e. it started trading a month ago and doesn't have 100 days worth of prices yet, or some other anomalous event in an equity's history. 
    4. **scrilla.errors.ConfigurationError**
        If one of the settings is improperly configured or one of the environment variables was unable to be parsed from the environment, this error will be thrown.

    Returns
    ------
    ``dict`` : `{ 'date' :  value ,  'date':  value , ... }`
        Dictionary with date strings formatted `YYYY-MM-DD` as keys and the interest on that date as the corresponding value.

    .. notes::
        * Yield rates are not reported on weekends or holidays, so the `asset_type` for interest is functionally equivalent to equities, at least as far as date calculations are concerned. The dates inputted into this function are validated as if they were labelled as equity `asset_types` for this reason.
    """
    try:
        start_date,end_date=errors.validate_dates(start_date=start_date, end_date=end_date, asset_type=static.keys['ASSETS']['EQUITY'])
    except errors.InputValidationError as ive:
        raise ive

    rates = None
    rates = interest_cache.filter_interest_cache(maturity, start_date=start_date, end_date=end_date)

        # TODO: this only works when stats are reported daily and that the latest date in the dataset is actually end_date.
    if rates is not None and helper.date_to_string(end_date) in rates.keys() \
        and (helper.business_days_between(start_date, end_date) + 1) == len(rates): 
        return rates
    if rates is not None:
        logger.debug(f'Cached {maturity} data is out of date, passing request to external service')
    try:
        rates = stat_manager.get_interest_rates(start_date=start_date, end_date=end_date)
    except errors.APIResponseError as api:
        raise api
    except errors.InputValidationError as ive:
        raise ive

    for date in rates:
        interest_cache.save_row(date=date, value=rates[date])

    rates = stat_manager.format_for_maturity(maturity=maturity, results=rates)

    return rates

def get_daily_interest_latest(maturity: str) -> float:
    """
    Returns the latest interest rate for the inputted US Treasury maturity.

    Parameters
    ----------
    1. **maturity**: ``str``
        Maturity of the US Treasury security whose interest rate is to be retrieved. Allowable values accessible through `static.keys['YIELD_CURVE']
    """
    end_date = helper.get_last_trading_date()
    start_date = helper.decrement_date_by_business_days(end_date, 1)
    interest_history = get_daily_interest_history(maturity=maturity, start_date=start_date, end_date=end_date)
    if interest_history is not None:
        first_element = helper.get_first_json_key(interest_history)
        return interest_history[first_element]
    return None

def get_dividend_history(ticker: str) -> dict:
    """
    Wrapper around external service request for dividend payment data. Relies on an instance of `DivManager` configured by `settings.DIV_MANAGER` value, which in turn is configured by the `DIV_MANAGER` environment variable, to hydrate with data.
    
    Note, since dividend payments do not occur every day (if only), dividend amounts do not get cached, as there is no nice way to determine on a given day whether or not a payment should have been made, and thus to determine whether or not the cache is out of date. In other words, you can't look at today's date and the date of the last payment in the cache and determine based solely on the dates whether or not the cache is outdated. 

    Parameters
    ----------
    1. **ticker** : ``str`` 
        Ticker symbol of the equity whose dividend history is to be retrieved.
    
    Returns
    ------
    ``list`` : `{ 'date' (str) :  amount (str),  'date' (str):  amount (str), ... }`
        Dictionary with date strings formatted `YYYY-MM-DD` as keys and the dividend payment amount on that date as the corresponding value. \n \n
    """
    logger.debug(f'Retrieving {ticker} dividends from service')  
    divs = div_manager.get_dividends(ticker=ticker)
    return divs

def get_risk_free_rate() -> float:
    """
    Returns the risk free rate, defined as the annualized yield on a specific US Treasury duration, as a decimal. The US Treasury yield used as a proxy for the risk free rate is defined in the `settings.py` file and is configured through the RISK_FREE environment variable.
    """
    return get_daily_interest_latest(maturity=settings.RISK_FREE_RATE)/100
