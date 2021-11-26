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

"""
This module interfaces with the external services the program uses to hydrate with financial data. In the case of price and interest history, the functions in this module defer to the cache before making expensive HTTP requests. Statistical data retrieved from FRED and dividment payment histories are not persisted in the cache since most of the data is reported on an irregular basis and it is impossible to tell based on the date alone whether or not the cache is out of date.

This module can be imported and used directly in other Python scripts if the API keys for the services have been set.

```
import os
from scrilla.services import get_daily_price_history

os.environ.setdefault('ALPHA_VANTAGE_KEY')
prices = get_daily_price_history('AAPL')
```
"""
import itertools
import time
import requests
from typing import Dict, List, Union

from datetime import date

from scrilla import settings, errors, cache
from scrilla.static import keys, constants
from scrilla.util import outputter, helper, dater

logger = outputter.Logger("scrilla.services", settings.LOG_LEVEL)


class StatManager():
    """
    StatManager is an interface between the application and the external services that hydrate it with financial statistics data. This class gets instantiated on the level of the `scrilla.services` module with the value defined in `scrilla.settings.STAT_MANAGER`. This value is in turn defined by the value of the `STAT_MANAGER` environment variable. This value determines how the url is constructed, which API credentials get appended to the external query and the keys used to parse the response JSON container the statistical data.

    Attributes
    ----------
    1. **genre**: ``str``
        A string denoting which service will be used for data hydration. Genres can be accessed through the `keys.keys['SERVICES']` dictionary.
    2. **self.service_map**: ``dict``
        A dictionary containing keys unique to the service defined by `genre`, such as endpoints, query parameters, etc. 

    Raises
    ------
    1. **scrilla.errors.ConfigurationError**
        If the **STAT_MANAGER** environment variable has been set to a value the program doesn't understand or hasn't set at all, this error will be thrown when this class is instantiated.

    .. notes ::
        * This class handles retrieval of financial statistics from the [Quandl's FRED dataset](https://data.nasdaq.com/data/FRED-federal-reserve-economic-data) and [Quandl's USTREASURY dataset](https://data.nasdaq.com/data/USTREASURY-us-treasury). In other words, it handles statistics and interest rate service calls. Interest rates are technically prices, not statistics, but...well, I don't have a good explanation why this isn't `scrilla.services.PriceManager`; I suppose I grouped these classes more by service type than data type. Might do to refactor...
    """

    def __init__(self, genre):
        self.genre = genre
        self.service_map = None
        if self._is_quandl():
            self.service_map = keys.keys["SERVICES"]["STATISTICS"]["QUANDL"]["MAP"]
            self.key = settings.Q_KEY
            self.url = settings.Q_URL
        if self.service_map is None:
            raise errors.ConfigurationError(
                'No STAT_MANAGER found in the parsed environment settings')

    def _is_quandl(self):
        """
        Returns
        -------
        `bool`
            `True` if this instace of `StatManager` is a Quandl interface. `False` otherwise.

        .. notes::
            * This is for use within the class and probably won't need to be accessed outside of it. `StatManager` is intended to hide the data implementation from the rest of the library, i.e. it is ultimately agnostic about where the data comes where. It should never need to know `StatManger` is a Quandl interface. Just in case the library ever needs to populate its data from another source.

        """
        if self.genre == keys.keys['SERVICES']['STATISTICS']['QUANDL']['MANAGER']:
            return True
        return False

    def _construct_query(self, start_date: date, end_date: date) -> str:
        """
        Constructs and formats the query parameters for the external statistics service. Note, this method appends the API key to the query. Be careful with the returned value.

        Parameters
        ----------
        1. **start_date** : ``datetime.date``
            Start date of historical sample to be retrieved.
        2. **end_date** : ``datetime.date``
            End date of historical sample to be retrieved.

        Returns
        -------
        ``str``
            The formatted query for the specific service defined by `self.genre`.

        """
        query = ""
        if end_date is not None:
            end_string = dater.to_string(end_date)
            query += f'&{self.service_map["PARAMS"]["END"]}={end_string}'

        if start_date is not None:
            start_string = dater.to_string(start_date)
            query += f'&{self.service_map["PARAMS"]["START"]}={start_string}'

        if query:
            logger.debug(f'StatManager Query (w/o key) = {query}')
            return f'{query}&{self.service_map["PARAMS"]["KEY"]}={self.key}'

        return f'{self.service_map["PARAMS"]["KEY"]}={self.key}'

    def _construct_stat_url(self, symbol: str, start_date: date, end_date: date):
        """
        Constructs the full URL path for the external statistics service. Note, this method will return the URL with an API key appended as a query parameter. Be careful with the returned value.

        Parameters
        ----------
        1. **symbol**: ``str``
            Symbol representing the statistical series to be retrieved. List of allowable symbols can be found [here](https://data.nasdaq.com/data/FRED-federal-reserve-economic-data)
        2. **start_date**: ``datetime.date`` 
            Start date of historical sample to be retrieved.
        3. **end_date**: ``datetime.date``
            End date of historical sample to be retrieved.


        Returns
        -------
        ``str``
            The formatted URL for the specific statistics service defined by `self.genre`.
        """
        url = f'{self.url}/{self.service_map["PATHS"]["FRED"]}/{symbol}?'
        url += self._construct_query(start_date=start_date, end_date=end_date)
        return url

    def _construct_interest_url(self, start_date, end_date):
        """
        Constructs the full URL path for the external interest rate service. Note, this method will return the URL with an API key appended as a query parameter. Be careful with the returned value.

        Parameters
        ----------
        1. **start_date**: ``datetime.date``
            Start date of historical sample to be retrieved.
        2. **end_date**: ``datetime.date`` 
            End date of historical sample to be retrieved.

        Returns
        -------
        ``str``
            The formatted URL for the specific interest rate service defined by `self.genre`.

        .. notes::
            * The URL returned by this method will always contain a query for a historical range of US Treasury Yields, i.e. this method is specifically for queries involving the "Risk-Free" (right? right? *crickets*) Yield Curve. 
        """
        url = f'{self.url}/{self.service_map["PATHS"]["YIELD"]}?'
        url += self._construct_query(start_date=start_date, end_date=end_date)
        return url

    def get_stats(self, symbol, start_date, end_date):
        url = self._construct_stat_url(symbol, start_date, end_date)
        response = requests.get(url).json()

        raw_stat = response[self.service_map["KEYS"]["FIRST_LAYER"]
                            ][self.service_map["KEYS"]["SECOND_LAYER"]]
        formatted_stat = {}

        for stat in raw_stat:
            formatted_stat[stat[0]] = stat[1]
        return formatted_stat

    def get_interest_rates(self, start_date, end_date):
        url = self._construct_interest_url(
            start_date=start_date, end_date=end_date)
        response = requests.get(url).json()

        raw_interest = response[self.service_map["KEYS"]
                                ["FIRST_LAYER"]][self.service_map["KEYS"]["SECOND_LAYER"]]
        formatted_interest = {}
        for rate in raw_interest:
            formatted_interest[rate[0]] = rate[1:]
        return formatted_interest

    @staticmethod
    def format_for_maturity(maturity, results):
        try:
            maturity_key = keys.keys['YIELD_CURVE'].index(maturity)
        except KeyError:
            raise errors.InputValidationError(
                f'{maturity} is not a valid maturity for US Treasury Bonds')

        formatted_interest = {}
        for result in results:
            formatted_interest[result] = results[result][maturity_key]
        return formatted_interest


class DividendManager():
    """
    Attributes
    ----------
    1. **genre**: ``str``
        A string denoting which service will be used for data hydration. Genres can be accessed through the `keys.keys['SERVICES']` dictionary.
    2. **self.service_map**: ``dict``
        A dictionary containing keys unique to the service defined by `genre`, such as endpoints, query parameters, etc. 
    """

    def __init__(self, genre):
        self.genre = genre
        if self.genre == keys.keys['SERVICES']['DIVIDENDS']['IEX']['MANAGER']:
            self.service_map = keys.keys['SERVICES']['DIVIDENDS']['IEX']['MAP']
            self.key = settings.iex_key()
            self.url = settings.IEX_URL

        if self.service_map is None:
            raise errors.ConfigurationError(
                'No DIV_MANAGER found in the parsed environment settings')

    def _construct_url(self, ticker):
        query = f'{ticker}/{self.service_map["PATHS"]["DIV"]}/{self.service_map["PARAMS"]["FULL"]}'
        url = f'{self.url}/{query}?{self.service_map["PARAMS"]["KEY"]}={self.key}'
        logger.debug(f'DivManager Query (w/o key) = {query}')
        return url

    def get_dividends(self, ticker):
        url = self._construct_url(ticker)
        response = requests.get(url).json()
        formatted_response = {}

        for item in response:
            this_date = str(item[self.service_map['KEYS']['DATE']])
            div = item[self.service_map['KEYS']['AMOUNT']]
            formatted_response[this_date] = div

        return formatted_response


class PriceManager():
    """
    PriceManager is an interface between the application and the external services that hydrate it with price data. This class gets instantiated on the level of the `scrilla.services` module with the value defined in `scrilla.settings.PRICE_MANAGER` variable. This value is in turn configured by the value of the **PRICE_MANAGER** environment variable. This value determines how the url is constructed, which API credentials get appended to the external query and the keys used to parse the response JSON containing the price data.

    Raises
    ------
    1. **scrilla.errors.ConfigurationError**
        If the **PRICE_MANAGER** environment variable hasn't been set or set to a value the program doesn't understand, this error will be thrown when this class is instantiated.

    Attributes
    ----------
    1. **genre**: ``str``
        A string denoting which service will be used for data hydration. Genres can be accessed through the `keys.keys['SERVICES']` dictionary.
    2. **self.service_map**: ``dict``
        A dictionary containing keys unique to the service defined by `genre`, such as endpoints, query parameters, etc. 

    """

    def __init__(self, genre):
        self.genre = genre
        if self.genre == keys.keys['SERVICES']['PRICES']['ALPHA_VANTAGE']['MANAGER']:
            self.service_map = keys.keys['SERVICES']['PRICES']['ALPHA_VANTAGE']['MAP']
            self.url = settings.AV_URL
            self.key = settings.av_key()
        if self.service_map is None:
            raise errors.ConfigurationError(
                'No PRICE_MANAGER found in the parsed environment settings')

    def _construct_url(self, ticker, asset_type):
        """
        Constructs the service url with the query and parameters appended. 

        Parameters
        ----------
        1. **ticker**: ``str`
            Ticker symbol of the asset whose prices are being retrieved.
        2. **asset_type**: ``str``
            Asset type of the asset whose prices are being retrieved. Options are statically
            accessible in the `scrillla.static` module dictionary `scrilla.keys.keys['ASSETS']`.

        Returns
        -------
        `str`
            The URL with the authenticated query appended, i.e. with the service's API key injected into the parameters. Be careful not to expose the return value of this function!

        .. notes::
            * this function will probably need substantially refactored if another price service is ever incorporated, unless the price service selected can be abstracted into the same template set by `scrilla.statics.keys['SERVICES']['PRICES']['ALPHA_VANTAGE']['MAP']`.
        """

        query = f'{self.service_map["PARAMS"]["TICKER"]}={ticker}'

        if asset_type == keys.keys['ASSETS']['EQUITY']:
            query += f'&{self.service_map["PARAMS"]["FUNCTION"]}={self.service_map["ARGUMENTS"]["EQUITY_DAILY"]}'
            query += f'&{self.service_map["PARAMS"]["SIZE"]}={self.service_map["ARGUMENTS"]["FULL"]}'

        elif asset_type == keys.keys['ASSETS']['CRYPTO']:
            query += f'&{self.service_map["PARAMS"]["FUNCTION"]}={self.service_map["ARGUMENTS"]["CRYPTO_DAILY"]}'
            query += f'&{self.service_map["PARAMS"]["DENOMINATION"]}={constants.constants["DENOMINATION"]}'

        auth_query = query + f'&{self.service_map["PARAMS"]["KEY"]}={self.key}'
        url = f'{self.url}?{auth_query}'
        logger.debug(f'PriceManager query (w/o key) = {query}')
        return url

    def get_prices(self, ticker: str, start_date: date, end_date: date, asset_type: str):
        """
        Retrieve prices from external service.

        Parameters
        ----------
        1. **ticker** : ``str``
            Ticker symbol of the asset whose prices are being retrieved.
        2. **start_date**; ``str``
        3. **end_date**: ``str``
        4. **asset_type** : ``str``
            Asset type of the asset whose prices are being retrieved. Options are statically
            accessible in the `scrillla.static` module dictionary `scrilla.keys.keys['ASSETS']`.

        Returns
        -------
        ``Dict[str, Dict[str, float]]``
        ```
            prices = { 
                        'date': { 
                            'open': value, 
                            'close': value
                        },  
                        'date': { 
                            'open': value,
                            'close': value
                        }
            }
        ```
         Dictionary of prices with date as key, ordered from latest to earliest.

        Raises
        ------
        1. **scrilla.errors.ConfigurationError**
            If one of the settings is improperly configured or one of the environment variables was unable to be parsed from the environment, this error will be thrown.
        2. **scrilla.errors.APIResponseError**
            If the service from which data is being retrieved is down, the request has been rate limited or some otherwise anomalous event has taken place, this error will be thrown.
        """
        url = self._construct_url(ticker, asset_type)
        response = requests.get(url).json()

        first_element = helper.get_first_json_key(response)
        # end function is daily rate limit is reached
        if first_element == self.service_map['ERRORS']['RATE_LIMIT']:
            raise errors.APIResponseError(
                response[self.service_map['ERRORS']['RATE_LIMIT']])
            # check for bad response
        if first_element == self.service_map['ERRORS']['INVALID']:
            raise errors.APIResponseError(
                response[self.service_map['ERRORS']['INVALID']])

        # check and wait for API rate limit refresh
        first_pass, first_element = True, helper.get_first_json_key(response)

        while first_element == self.service_map['ERRORS']['RATE_THROTTLE']:
            if first_pass:
                logger.comment(
                    f'{self.genre} API rate limit per minute exceeded. Waiting...')
                first_pass = False
            else:
                logger.comment('Waiting...')

            time.sleep(constants.constants['BACKOFF_PERIOD'])
            response = requests.get(url).json()
            first_element = helper.get_first_json_key(response)

            if first_element == self.service_map['ERRORS']['INVALID']:
                raise errors.APIResponseError(
                    response[self.service_map['ERRORS']['INVALID']])

        prices = self._slice_prices(
            start_date=start_date, end_date=end_date, asset_type=asset_type, prices=response)
        format_prices = {}
        for this_date in prices:
            close_price = self._parse_price_from_date(prices=prices, this_date=this_date, asset_type=asset_type,
                                                      which_price=keys.keys['PRICES']['CLOSE'])
            open_price = self._parse_price_from_date(prices=prices, this_date=this_date, asset_type=asset_type,
                                                     which_price=keys.keys['PRICES']['OPEN'])
            format_prices[this_date] = {
                keys.keys['PRICES']['OPEN']: open_price, keys.keys['PRICES']['CLOSE']: close_price}
        return format_prices

    def _slice_prices(self, start_date: date, end_date: date, asset_type: str, prices: dict) -> dict:
        """
        Parses the raw response from the external price service into a format the program will understand.

        Parameters
        ----------
        1. **start_date** : ``datetime.date``
        2. **end_date** : ``datetime.date``
        3. **asset_type** : ``str``
            Required: Asset type of the asset whose prices are being retrieved. Options are statically
            accessible in the `scrillla.static` module dictionary `scrilla.keys.keys['ASSETS']`.
        4. **response** : ``dict``
            The full response from the price manager, i.e. the entire price history returned by the external service in charge of retrieving pricce histories, the result returned from `scrilla.services.PriceManager.get_prices`

        Returns
        -------
        ``dict``: `{ 'date': value, 'date': value, ...}`
            Dictionary of prices with date as key, ordered from latest to earliest.


        Raises
        ------
        1. **KeyError**
            If the inputted or validated dates do not exist in the price history, a KeyError will be thrown. This could be due to the equity not having enough price history, i.e. it started trading a month ago and doesn't have 100 days worth of prices yet, or some other anomalous event in an equity's history. 
        2. **scrilla.errors.ConfigurationError**
            If one of the settings is improperly configured or one of the environment variables was unable to be parsed from the environment, this error will be thrown.
        """

        # NOTE: only really needed for `alpha_vantage` responses so far, due to the fact AlphaVantage either returns everything or 100 days or prices.
        # shouldn't need to verify genre anyway, since using service_map and service_map should abstract the response away.
        if self.genre == keys.keys['SERVICES']['PRICES']['ALPHA_VANTAGE']['MANAGER']:

            # NOTE: Remember AlphaVantage is ordered current to earliest. END_INDEX is
            # actually the beginning of slice and START_INDEX is actually end of slice.
            start_string, end_string = dater.to_string(
                start_date), dater.to_string(end_date)
            if asset_type == keys.keys['ASSETS']['EQUITY']:
                response_map = self.service_map['KEYS']['EQUITY']['FIRST_LAYER']
            elif asset_type == keys.keys['ASSETS']['CRYPTO']:
                response_map = self.service_map['KEYS']['CRYPTO']['FIRST_LAYER']

            start_index = list(prices[response_map].keys()).index(start_string)
            end_index = list(prices[response_map].keys()).index(end_string)
            prices = dict(itertools.islice(
                prices[response_map].items(), end_index, start_index+1))
            return prices

        raise errors.ConfigurationError(
            'No PRICE_MANAGER found in the parsed environment settings')

    def _parse_price_from_date(self, prices: Dict[str, Dict[str, float]], this_date: date, asset_type: str, which_price: str) -> str:
        """
        Parameters
        ----------
        1. **prices** : ``Dict[str, Dict[str, float]]``
            List containing the AlphaVantage response with the first layer peeled off, i.e.
            no metadata, just the date and prices.
        2. **date**: `date``
            String of the date to be parsed. Note: this is not a datetime.date object. String
            must be formatted `YYYY-MM-DD`
        3. **asset_type**: ``str``
            String that specifies what type of asset price is being parsed. Options are statically
            accessible in the `scrillla.static` module dictionary `scrilla.keys.keys['ASSETS']`
        4. **which_price**: ``str``
            String that specifies which price is to be retrieved, the closing price or the opening prices. Options are statically accessible 

        Returns
        ------
        ``str``
            String containing the price on the specified date.

        Raises
        ------
        1. **KeyError**
            If the inputted or validated dates do not exist in the price history, a KeyError will be thrown. This could be due to the equity not having enough price history, i.e. it started trading a month ago and doesn't have 100 days worth of prices yet, or some other anomalous event in an equity's history. 
        2. **scrilla.errors.InputValidationError**
            If prices was unable to be grouped into a (crypto, equity)-asset class or the opening/closing price did not exist for whatever reason, this error will be thrown.
        """
        if asset_type == keys.keys['ASSETS']['EQUITY']:
            if which_price == keys.keys['PRICES']['CLOSE']:
                return prices[this_date][self.service_map['KEYS']['EQUITY']['CLOSE']]
            if which_price == keys.keys['PRICES']['OPEN']:
                return prices[this_date][self.service_map['KEYS']['EQUITY']['CLOSE']]

        elif asset_type == keys.keys['ASSETS']['CRYPTO']:
            if which_price == keys.keys['PRICES']['CLOSE']:
                return prices[this_date][self.service_map['KEYS']['CRYPTO']['CLOSE']]
            if which_price == keys.keys['PRICES']['OPEN']:
                return prices[this_date][self.service_map['KEYS']['CRYPTO']['OPEN']]

        raise errors.InputValidationError(
            f'Verify {asset_type}, {which_price} are allowable values')


price_manager = PriceManager(settings.PRICE_MANAGER)
stat_manager = StatManager(settings.STAT_MANAGER)
div_manager = DividendManager(settings.DIV_MANAGER)
price_cache = cache.PriceCache()
interest_cache = cache.InterestCache()


def get_daily_price_history(ticker: str, start_date: Union[None, date] = None, end_date: Union[None, date] = None, asset_type: Union[None, str] = None) -> Dict[str, Dict[str, float]]:
    """
    Wrapper around external service request for price data. Relies on an instance of `PriceManager` configured by `settings.PRICE_MANAGER` value, which in turn is configured by the `PRICE_MANAGER` environment variable, to hydrate with data. 

    Before deferring to the `PriceManager` and letting it call the external service, however, this function checks if response is in local cache. If the response is not in the cache, it will pass the request off to `PriceManager` and then save the response in the cache so subsequent calls to the function can bypass the service request. Used to prevent excessive external HTTP requests and improve the performance of the application. Other parts of the program should interface with the external price data services through this function to utilize the cache functionality.

    Parameters
    ----------
    1. **ticker** :  ``str``
        Ticker symbol corresponding to the price history to be retrieved.
    2. **start_date** : ``datetime.date`` 
        *Optional*. Start date of price history. Defaults to None. If `start_date is None`, the calculation is made as if the `start_date` were set to 100 trading days ago. If `scrilla.files.get_asset_type(ticker)==scrill.keys.keys['ASSETS']['CRYPTO']`, this includes weekends and holidays. If `scrilla.files.get_asset_type(ticker)==scrilla.keys.keys['ASSETS']['EQUITY']`, this excludes weekends and holidays.
    3. **end_date** : ``datetime.date``
        Optional End date of price history. Defaults to None. If `end_date is None`, the calculation is made as if the `end_date` were set to today. If `scrilla.files.get_asset_type(ticker)==scrill.keys.keys['ASSETS']['CRYPTO']`, this means today regardless. If `scrilla.files.get_asset_type(ticker)==scrilla.keys.keys['ASSETS']['EQUITY']`, this excludes weekends and holidays so that `end_date` is set to the previous business date. 
    4. **asset_type** : ``string``
        *Optional*. Asset type of the ticker whose history is to be retrieved. Used to prevent excessive calls to IO and list searching. `asset_type` is determined by comparing the ticker symbol `ticker` to a large static list of ticker symbols maintained in installation directory's /data/static/ subdirectory, which can slow the program down if the file is constantly accessed and lots of comparison are made against it. Once an `asset_type` is calculated, it is best to preserve it in the process environment somehow, so this function allows the value to be passed in. If no value is detected, it will make a call to the aforementioned directory and parse the file to determine to the `asset_type`. Asset types are statically accessible through the `scrilla.keys.keys['ASSETS']` dictionary.

    Returns
    ------
    ``Dict[str, Dict[str, float]]`` : Dictionary with date strings formatted `YYYY-MM-DD` as keys and a nested dictionary containing the 'open' and 'close' price as values. Ordered from latest to earliest, e.g., 
    ```
        { 
            'date' : 
                { 
                    'open': value, 
                    'close': value  
                }, 
            'date': 
                { 
                    'open' : value, 
                    'close' : value 
                }, 
            ... 
        }
    ```

    Raises
    ------
    1. **scrilla.errors.PriceError**
        If no sample prices can be retrieved, this error is thrown. 

    .. notes::
        * The default analysis period, if no `start_date` and `end_date` are specified, is determined by the *DEFAULT_ANALYSIS_PERIOD** variable in the `settings,py` file. The default value of this variable is 100.
    """
    asset_type = errors.validate_asset_type(ticker, asset_type)
    start_date, end_date = errors.validate_dates(
        start_date, end_date, asset_type)

    cached_prices = price_cache.filter_price_cache(
        ticker=ticker, start_date=start_date, end_date=end_date)

    if cached_prices is not None:
        if asset_type == keys.keys['ASSETS']['EQUITY']:
            logger.debug(
                f'Comparing {len(cached_prices)} = {dater.business_days_between(start_date, end_date)}')
        elif asset_type == keys.keys['ASSETS']['CRYPTO']:
            logger.debug(
                f'Comparing {len(cached_prices)} = {dater.days_between(start_date, end_date)}')

    # make sure the length of cache is equal to the length of the requested sample
    if cached_prices is not None and dater.to_string(end_date) in cached_prices.keys() and (
        (asset_type == keys.keys['ASSETS']['EQUITY']
            and (dater.business_days_between(start_date, end_date)) == len(cached_prices))
        or
        (asset_type == keys.keys['ASSETS']['CRYPTO']
            and (dater.days_between(start_date, end_date)) == len(cached_prices))
    ):
        # TODO: debug the crypto out of date check.
        return cached_prices

    if cached_prices is not None:
        logger.debug(
            f'Cached {ticker} prices are out of date, passing request off to external service')

    prices = price_manager.get_prices(
        ticker=ticker, start_date=start_date, end_date=end_date, asset_type=asset_type)

    if cached_prices is not None:
        new_prices = helper.complement_dict_keys(prices, cached_prices)
    else:
        new_prices = prices

    for this_date in new_prices:
        open_price = new_prices[this_date][keys.keys['PRICES']['OPEN']]
        close_price = new_prices[this_date][keys.keys['PRICES']['CLOSE']]
        price_cache.save_row(ticker=ticker, date=this_date,
                             open_price=open_price, close_price=close_price)

    if not prices:
        raise errors.PriceError(
            f'Prices could not be retrieved for {ticker}')

    return prices


def get_daily_price_latest(ticker: str, asset_type: Union[None, str] = None) -> float:
    """
    Returns the latest closing price for a given ticker symbol.

    Parameters
    ----------
    1. **ticker**: ``str``
        ticker symbol whose latest closing price is to be retrieved. \n \n
    2. **asset_type**: str``
        *Optional*. Asset type of the ticker whose history is to be retrieved. Will be calculated from the `ticker` symbol if not provided.
    """
    last_date = dater.this_date_or_last_trading_date()
    prices = get_daily_price_history(
        ticker=ticker, asset_type=asset_type, start_date=last_date, end_date=last_date)
    first_element = helper.get_first_json_key(prices)
    return prices[first_element][keys.keys['PRICES']['OPEN']]


def get_daily_prices_latest(tickers: List[str], asset_types: Union[None, List[str]] = None):
    return {ticker: get_daily_price_latest(ticker, asset_types[i]) for i, ticker in enumerate(tickers)}


def get_daily_fred_history(symbol: str, start_date: Union[date, None] = None, end_date: Union[date, None] = None) -> list:
    """
    Wrapper around external service request for financial statistics data constructed by the Federal Reserve Economic Data. Relies on an instance of `StatManager` configured by `settings.STAT_MANAGER` value, which in turn is configured by the `STAT_MANAGER` environment variable, to hydrate with data.

    Parameters
    ----------
    1. **symbol**: ``str`` 
        Symbol representing the statistic whose history is to be retrieved. List of allowable values can be found [here](https://www.quandl.com/data/FRED-Federal-Reserve-Economic-Data/documentation)
    2. **start_date**: ``Union[date, None]`` 
        *Optional*. Start date of price history. Defaults to None. If `start_date is None`, the calculation is made as if the `start_date` were set to 100 trading days ago. This excludes weekends and holidays.
    3. **end_date**: ``Union[date, None]``
        *Optional*. End date of price history. Defaults to None. If `end_date is None`, the calculation is made as if the `end_date` were set to today. This excludes weekends and holidays so that `end_date` is set to the last previous business date.

    Returns
    ------
    ``list``: `{ 'date' (str) :  value (str),  'date' (str):  value (str), ... }`
        Dictionary with date strings formatted `YYYY-MM-DD` as keys and the statistic on that date as the corresponding value.

    Raises
    ------
    1. **scrilla.errors.PriceError**
        If no sample prices can be retrieved, this error is thrown. 

    .. notes::
        * Most financial statistics are not reported on weekends or holidays, so the `asset_type` for financial statistics is functionally equivalent to equities, at least as far as date calculations are concerned. The dates inputted into this function are validated as if they were labelled as equity `asset_types` for this reason.

    """

    start_date, end_date = errors.validate_dates(
        start_date=start_date, end_date=end_date, asset_type=keys.keys['ASSETS']['EQUITY'])

    stats = stat_manager.get_stats(
        symbol=symbol, start_date=start_date, end_date=end_date)

    if not stats:
        raise errors.PriceError(
            f'Prices could not be retrieved for {symbol}')

    return stats


def get_daily_fred_latest(symbol: str) -> float:
    """
    Returns the latest value for the inputted statistic symbol.

    Parameters
    ----------
    1. **symbol**: str
        Symbol representing the statistic whose value it to be retrieved.
    """
    stats_history = get_daily_fred_history(symbol=symbol)
    first_element = helper.get_first_json_key(stats_history)
    return stats_history[first_element]


def get_daily_interest_history(maturity: str, start_date: Union[date, None] = None, end_date: Union[date, None] = None) -> list:
    """
    Wrapper around external service request for US Treasury Yield Curve data. Relies on an instance of `StatManager` configured by `settings.STAT_MANAGER` value, which in turn is configured by the `STAT_MANAGER` environment variable, to hydrate with data.

    Before deferring to the `StatManager` and letting it call the external service, however, this function checks if response is in local cache. If the response is not in the cache, it will pass the request off to `StatManager` and then save the response in the cache so subsequent calls to the function can bypass the service request. Used to prevent excessive external HTTP requests and improve the performance of the application. Other parts of the program should interface with the external statistics data services through this function to utilize the cache functionality. 

    Parameters
    ----------
    1. **maturity** : ``str``
        Maturity of the US Treasury for which the interest rate will be retrieved. List of allowable values can in `scrilla.stats.keys['SERVICES']['STATISTICS']['QUANDL']['MAP']['YIELD_CURVE']`
    2. **start_date** : ``datetime.date``
        *Optional*. Start date of price history. Defaults to None. If `start_date is None`, the calculation is made as if the `start_date` were set to 100 trading days ago. This excludes weekends and holidays.
    3. **end_date** : ``datetime.date``
        *Optional*. End date of price history. Defaults to None. If `end_date is None`, the calculation is made as if the `end_date` were set to today. This excludes weekends and holidays so that `end_date` is set to the last previous business date.

    Returns
    ------
    ``dict`` : `{ 'date' :  value ,  'date':  value , ... }`
        Dictionary with date strings formatted `YYYY-MM-DD` as keys and the interest on that date as the corresponding value.

    .. notes::
        * Yield rates are not reported on weekends or holidays, so the `asset_type` for interest is functionally equivalent to equities, at least as far as date calculations are concerned. The dates inputted into this function are validated as if they were labelled as equity `asset_types` for this reason.
    """
    start_date, end_date = errors.validate_dates(
        start_date=start_date, end_date=end_date, asset_type=keys.keys['ASSETS']['EQUITY'])

    rates = None
    rates = interest_cache.filter_interest_cache(
        maturity, start_date=start_date, end_date=end_date)

    if rates is not None:
        logger.debug(
            f'Comparing {len(rates)} = {dater.business_days_between(start_date, end_date)}')

    # TODO: this only works when stats are reported daily and that the latest date in the dataset is actually end_date.
    if rates is not None and \
            dater.to_string(end_date) in rates.keys() and \
            dater.business_days_between(start_date, end_date) == len(rates):
        return rates

    logger.debug(
        f'Cached {maturity} data is out of date, passing request to external service')
    rates = stat_manager.get_interest_rates(
        start_date=start_date, end_date=end_date)

    for this_date in rates:
        interest_cache.save_row(date=this_date, value=rates[this_date])

    rates = stat_manager.format_for_maturity(maturity=maturity, results=rates)

    return rates


def get_daily_interest_latest(maturity: str) -> float:
    """
    Returns the latest interest rate for the inputted US Treasury maturity.

    Parameters
    ----------
    1. **maturity**: ``str``
        Maturity of the US Treasury security whose interest rate is to be retrieved. Allowable values accessible through `keys.keys['YIELD_CURVE']
    """
    end_date = dater.get_last_trading_date()
    start_date = dater.decrement_date_by_business_days(end_date, 1)
    interest_history = get_daily_interest_history(
        maturity=maturity, start_date=start_date, end_date=end_date)
    first_element = helper.get_first_json_key(interest_history)
    return interest_history[first_element]


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
        Dictionary with date strings formatted `YYYY-MM-DD` as keys and the dividend payment amount on that date as the corresponding value.
    """
    logger.debug(f'Retrieving {ticker} dividends from service')
    divs = div_manager.get_dividends(ticker=ticker)
    return divs


def get_risk_free_rate() -> float:
    """
    Returns the risk free rate, defined as the annualized yield on a specific US Treasury duration, as a decimal. The US Treasury yield used as a proxy for the risk free rate is defined in the `settings.py` file and is configured through the RISK_FREE environment variable.
    """
    return get_daily_interest_latest(maturity=settings.RISK_FREE_RATE)/100
