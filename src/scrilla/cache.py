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
This module provides a data access layer for a SQLite database maintained on the local file system at the location set by the environment variable **SQLITE_FILE**. If this environment variable is not set, the file location defaults to the *installation_directory*/data/cache/scrilla.db. The database caches asset prices, statistical calculations and interest rates. This allows the program to avoid excessive API calls to external services for calculations that involve the same quantity. For instance, to calculate correlation, the mean and variance of the individual assets must be calculated over the price history of each before the correlation is calculated over their combined price history; this involves four references to a sample of prices, at different points in the program which do not necessarily share scope with the location of the other calculations, so they can not share the in-memory version of the prices.

In addition to preventing excessive API calls, the cache prevents redundant calculations. For example, calculating the market beta for a series of assets requires the variance of the market proxy for each calculation. Rather than recalculate this quantity each time, the program will defer to the values stored in the cache.
"""
import itertools
import datetime
import sqlite3
from typing import Union
import uuid

from scrilla import files, settings
from scrilla.cloud import aws
from scrilla.static import config, keys
from scrilla.util import dater, errors, outputter

logger = outputter.Logger("scrilla.cache", settings.LOG_LEVEL)


class Singleton(type):

    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(
                Singleton, cls).__call__(*args, **kwargs)
        else:
            cls._instances[cls].__init__(*args, **kwargs)
        return cls._instances[cls]


class Cache():
    """
    Class with static methods all other Caches employ. This class tries to hide as much implementation detail as possible behind its methods, i.e. this class is concerned with executing commits and transactions, whereas the other cache classes are concerned with the data structure that is created with these methods.
    """

    @staticmethod
    def provision(table_configuration, mode=settings.CACHE_MODE):
        if mode == 'dynamodb':
            logger.debug(
                f'Provisioning {table_configuration["TableName"]} DynamoDB Table', 'Cache.provision')
            return aws.dynamo_table(table_configuration)

    @staticmethod
    def execute(query, formatter=None, mode=settings.CACHE_MODE):
        """
        Executes and commits a transaction against the cache.

        Parameters
        ----------
        1. **transaction**: ``str``
            Statement to be executed and committed.
        2. formatter: `Union[dict, List[dict]]``
            Dictionary of parameters used to format statement. Statements are formatted with DB-API's name substitution. See [sqlite3 documentation](https://docs.python.org/3/library/sqlite3.html) for more information. A list of dictionaries can be passed in to perform a batch execute transaction. If nothing is passed in, method will assume the query is unparameterized.
        """
        if mode == 'sqlite':
            con = sqlite3.connect(settings.CACHE_SQLITE_FILE)
            executor = con.cursor()
            if formatter is not None:
                if isinstance(formatter, list):
                    response = executor.executemany(
                        query, formatter).fetchall()
                else:
                    response = executor.execute(query, formatter).fetchall()
            else:
                response = executor.execute(query).fetchall()
            con.commit(), con.close()
        elif mode == 'dynamodb':
            response = aws.dynamo_statement(query, formatter)
        else:
            raise errors.ConfigurationError(
                'CACHE_MODE has not been set in "settings.py"')
        return response


class PriceCache(metaclass=Singleton):
    """
    `scrilla.cache.PriceCache` statically accesses *SQLite* functionality from `scrilla.cache.Cache`. It extends basic functionality to cache interest rate data in a table with columns ``(ticker, date, open, close)``. `scrilla.cache.PriceCache` has a `scrilla.cache.Singleton` for its `metaclass`, meaning `PriceCache` is a singleton; it can only be created once; any subsequent instantiations will return the same instance of `PriceCache`. This is done so that all instances of `PriceCache` share the same `self.internal_cache`, allowing frequently accessed data to be stored in memory.

    Attributes
    ----------
    1. **internal_cache**: ``dict``
        Dictionary used by `PriceCache` to store API responses in memory. Used to quickly access data that is requested frequently.
    2. **inited**: ``bool``
        Flag used to determine if `InterestCache` has been instantiated prior to current instantiation. 
    3. **sqlite_create_table_transaction**: ``str``
        *SQLite* transaction passed to the super class used to create price cache table if it does not already exist.
    4. **sqlite_insert_row_transaction**: ``str``
        *SQLite* transaction used to insert row into price cache table.
    5. **sqlite_price_query**: ``str```
        *SQLite* query to retrieve prices from cache.
    """
    internal_cache = {}
    inited = False
    sqlite_create_table_transaction = "CREATE TABLE IF NOT EXISTS prices (ticker text, date text, open real, close real, UNIQUE(ticker, date))"
    sqlite_insert_row_transaction = "INSERT OR IGNORE INTO prices (ticker, date, open, close) VALUES (:ticker, :date, :open, :close)"
    sqlite_price_query = "SELECT date, open, close FROM prices WHERE ticker = :ticker AND date <= date(:end_date) AND date >= date(:start_date) ORDER BY date(date) DESC"

    dynamodb_table_configuration = config.dynamo_price_table_conf

    dynamodb_insert_transaction = "INSERT INTO \"prices\" VALUE {'ticker': ?, 'date': ?, 'open': ?, 'close': ? }"
    dynamodb_price_query = "SELECT \"date\", \"open\", \"close\" FROM \"prices\" WHERE \"ticker\"=? AND \"date\">=? AND \"date\"<=?"
    # No PartiQL ORDER BY clause yet: https://github.com/partiql/partiql-lang-kotlin/issues/47
    dynamodb_identity_query = "EXISTS(SELECT ticker FROM \"prices\" WHERE ticker=? and date= ?)"

    @staticmethod
    def to_dict(query_results, mode=settings.CACHE_MODE):
        """
        Returns the SQLite query results formatted for the application.

        Parameters
        ----------
        1. **query_results**: ``list``
            Raw SQLite query results.
        """
        if mode == 'sqlite':
            return {
                result[0]: {
                    keys.keys['PRICES']['OPEN']: result[1],
                    keys.keys['PRICES']['CLOSE']: result[2]
                } for result in query_results
            }
        elif mode == 'dynamodb':
            dates = [result['date'] for result in query_results]
            dates.sort(key=dater.parse)
            dates.reverse()
            formatted_results = {
                result['date']: {
                    keys.keys['PRICES']['OPEN']: result[keys.keys['PRICES']['OPEN']],
                    keys.keys['PRICES']['CLOSE']: result[keys.keys['PRICES']['CLOSE']]
                } for result in query_results
            }
            return {key: formatted_results[key] for key in dates}

    @staticmethod
    def _to_params(ticker, prices):
        return [
            {
                'ticker': ticker,
                'date': date,
                'open': prices[date][keys.keys['PRICES']['OPEN']],
                'close': prices[date][keys.keys['PRICES']['CLOSE']]
            } for date in prices
        ]

    def __init__(self, mode=settings.CACHE_MODE):
        """
        Initializes `PriceCache`. A random UUID will be assigned to the `PriceCache` the first time it is created. Since `PriceCache` is a singelton, all subsequent instantiations of `PriceCache` will have the same UUID. 

        Parameters
        ----------
        1. **mode**: ``str``
            Determines the data source that acts as the cache. Defaults to `scrilla.settings.CACHE_MODE`. Can be set to either `sqlite` or `dynamodb`. 
        """
        if not self.inited:
            self.uuid = uuid.uuid4()
            self.inited = True

        self.mode = mode

        if not files.get_memory_json()['cache'][mode]['prices']:
            self._table()

    def _table(self):
        if self.mode == 'sqlite':
            Cache.execute(query=self.sqlite_create_table_transaction,
                          mode=self.mode)
        elif self.mode == 'dynamodb':
            self.dynamodb_table_configuration = aws.dynamo_table_conf(
                self.dynamodb_table_configuration)
            Cache.provision(self.dynamodb_table_configuration, self.mode)

    def _insert(self):
        if self.mode == 'sqlite':
            return self.sqlite_insert_row_transaction
        elif self.mode == 'dynamodb':
            return self.dynamodb_insert_transaction

    def _query(self):
        if self.mode == 'sqlite':
            return self.sqlite_price_query
        elif self.mode == 'dynamodb':
            return self.dynamodb_price_query

    def _update_internal_cache(self, ticker, prices):
        if ticker not in list(self.internal_cache):
            self.internal_cache[ticker] = prices
        else:
            self.internal_cache[ticker].update(prices)

    def _retrieve_from_internal_cache(self, ticker, start_date, end_date):
        dates = list(self.internal_cache[ticker].keys())
        start_string = dater.to_string(start_date)
        end_string = dater.to_string(end_date)

        if start_string in dates and end_string in dates:
            end_index = dates.index(start_string)
            start_index = dates.index(end_string)
            if start_index > end_index:
                # NOTE: DynamoDB respones are not necessarily ordered
                # `to_dict` will take care of ordering
                start_index, end_index = end_index, start_index
            prices = dict(itertools.islice(
                self.internal_cache[ticker].items(), start_index, end_index+1))
            return prices
        return None

    def save_rows(self, ticker, prices):
        self._update_internal_cache(ticker, prices)
        logger.verbose(
            F'Attempting to insert {ticker} prices to cache', 'ProfileCache.save_rows')
        Cache.execute(
            query=self._insert(),
            formatter=self._to_params(ticker, prices),
            mode=self.mode
        )

    def filter(self, ticker, start_date, end_date):
        if ticker in list(self.internal_cache):
            prices = self._retrieve_from_internal_cache(
                ticker, start_date, end_date)
            if prices is not None:
                logger.debug(f'{ticker} prices found in memory',
                             'ProfileCachce.filter')
                return prices

        logger.debug(
            f'Querying {self.mode} cache \n\t{self._query()}\n\t\t with :ticker={ticker}, :start_date={start_date}, :end_date={end_date}', 'ProfileCache.filter')
        formatter = {'ticker': ticker,
                     'start_date': start_date, 'end_date': end_date}
        results = Cache.execute(
            query=self._query(),
            formatter=formatter,
            mode=self.mode)

        if len(results) > 0:
            logger.debug(
                f'Found {ticker} prices in the cache', 'ProfileCache.filter')
            prices = self.to_dict(results)
            self._update_internal_cache(ticker, prices)
            return prices
        logger.debug(
            f'No results found for {ticker} prices in the cache', 'ProfileCache.filter')
        return None


class InterestCache(metaclass=Singleton):
    """
    `scrilla.cache.InterestCache` statically accesses *SQLite* functionality from `scrilla.cache.Cache`. It extends basic functionality to cache interest rate data in a table with columns ``(maturity, date, value)``. `scrilla.cache.InterestCache` has a `scrilla.cache.Singleton` for its `metaclass`, meaning `InterestCache` is a singleton; it can only be created once; any subsequent instantiations will return the same instance of `InterestCache`.This is done so that all instances of `InterestCache` share the same `self.internal_cache`, allowing frequently accessed data to be stored in memory.


    Attributes
    ----------
    1. **internal_cache**: ``dict``
        Dictionary used by `InterestCache` to store API responses in memory. Used to quickly access data that is requested frequently.
    2. **inited**: ``bool``
        Flag used to determine if `InterestCache` has been instantiated prior to current instantiation. 
    2. **sqlite_create_table_transaction**: ``str``
         *SQLite* transaction passed to `scrilla.cache.Cache` used to create interest cache table if it does not already exist.
    3. **sqlite_insert_row_transaction**: ``str``
        *SQLite* transaction used to insert row into correlation cache table.
    4. **sqlite_interest_query**: ``str```
        *SQLite* query to retrieve an interest from cache.
    5. **dynamodb_table_configuration**: ``str``
    6. **dynamo_insert_transaction**: ``str``
    7. **dynamo_query**: ``str``
    8. **dynamo_identity_query**: ``str``
    """
    internal_cache = {}
    inited = False
    sqlite_create_table_transaction = "CREATE TABLE IF NOT EXISTS interest(maturity text, date text, value real, UNIQUE(maturity, date))"
    sqlite_insert_row_transaction = "INSERT OR IGNORE INTO interest (maturity, date, value) VALUES (:maturity, :date, :value)"
    sqlite_interest_query = "SELECT date, value FROM interest WHERE maturity=:maturity AND date <=date(:end_date) AND date>=date(:start_date) ORDER BY date(date) DESC"

    dynamodb_table_configuration = config.dynamo_interest_table_conf
    dynamodb_insert_transaction = "INSERT INTO \"interest\" VALUE {'maturity': ?, 'date': ?, 'value': ? }"
    dynamodb_query = "SELECT \"date\", \"value\" FROM \"interest\" WHERE \"maturity\"=? AND \"date\">=? AND \"date\"<=?"
    # NOTE: No PartiQL ORDER BY clause yet: https://github.com/partiql/partiql-lang-kotlin/issues/47
    dynamodb_identity_query = "EXISTS(SELECT 'maturity' FROM \"interest\" WHERE 'maturity'=? AND 'date'<= ?)"

    @staticmethod
    def to_dict(query_results, mode=settings.CACHE_MODE):
        """
        Returns the SQLite query results formatted for the application.

        Parameters
        ----------
        1. **query_results**: ``list``
            Raw SQLite query results.
        """
        if mode == 'sqlite':
            return {result[0]: result[1] for result in query_results}
        elif mode == 'dynamodb':
            # TODO: need to order by date!
            dates = [result['date'] for result in query_results]
            dates.sort(key=dater.parse)
            dates.reverse()
            formatted_results = {result['date']: result['value']
                                 for result in query_results}
            return {key: formatted_results[key] for key in dates}

    @staticmethod
    def _to_params(rates):
        params = []
        for date in rates:
            for index, maturity in enumerate(keys.keys['YIELD_CURVE']):
                entry = {
                    'maturity': maturity,
                    'date': date,
                    'value': rates[date][index]
                }
                params.append(entry)
        return params

    def __init__(self, mode=settings.CACHE_MODE):
        """
        Initializes `ProfileCache`. A random UUID will be assigned to the `InteretCache` the first time it is created. Since `InterestCache` is a singelton, all subsequent instantiations of `InterestCache` will have the same UUID. 

        Parameters
        ----------
        1. **mode**: ``str``
            Determines the data source that acts as the cache. Defaults to `scrilla.settings.CACHE_MODE`. Can be set to either `sqlite` or `dynamodb`. 
        """
        if not self.inited:
            self.uuid = uuid.uuid4()
            self.inited = True

        self.mode = mode

        if not files.get_memory_json()['cache'][self.mode]['interest']:
            self._table()

    def _table(self):
        if self.mode == 'sqlite':
            Cache.execute(query=self.sqlite_create_table_transaction,
                          mode=self.mode)
        elif self.mode == 'dynamodb':
            self.dynamodb_table_configuration = aws.dynamo_table_conf(
                self.dynamodb_table_configuration)
            Cache.provision(self.dynamodb_table_configuration, self.mode)

    def _insert(self):
        if self.mode == 'sqlite':
            return self.sqlite_insert_row_transaction
        elif self.mode == 'dynamodb':
            return self.dynamodb_insert_transaction

    def _query(self):
        if self.mode == 'sqlite':
            return self.sqlite_interest_query
        elif self.mode == 'dynamodb':
            return self.dynamodb_query

    def _save_internal_cache(self, rates):
        self.internal_cache.update(rates)

    def _update_internal_cache(self, values, maturity):
        for date in values.keys():
            if self.internal_cache.get(date) is None:
                self.internal_cache[date] = [
                    None for _ in keys.keys['YIELD_CURVE']]
            self.internal_cache[date][keys.keys['YIELD_CURVE'].index(
                maturity)] = values[date]

    def _retrieve_from_internal_cache(self, maturity, start_date, end_date):
        dates = list(self.internal_cache.keys())
        start_string = dater.to_string(start_date)
        end_string = dater.to_string(end_date)
        if start_string in dates and end_string in dates:
            start_index = dates.index(start_string)
            end_index = dates.index(end_string)
            if start_index > end_index:
                # NOTE: DynamoDB respones are not necessarily ordered
                # `to_dict` will take care of ordering
                start_index, end_index = end_index, start_index
            rates = dict(itertools.islice(
                self.internal_cache.items(), start_index, end_index+1))
            rates = {key: rates[key][keys.keys['YIELD_CURVE'].index(
                maturity)] for key in rates}
            logger.debug('Found interest in memory',
                         'InterestCache._retrieve_from_internal_cache')
            return rates

    def save_rows(self, rates):
        # NOTE: at this point, rates should look like { 'date': [rates], 'date': [rates], ...}
        self._save_internal_cache(rates)
        logger.verbose(
            'Attempting to insert interest rates into cache', 'InterestCache.save_rows')
        Cache.execute(
            query=self._insert(),
            formatter=self._to_params(rates)
        )

    def filter(self, maturity, start_date, end_date):
        rates = self._retrieve_from_internal_cache(
            maturity, start_date, end_date)
        if rates is not None:
            logger.debug(f'{maturity} interet found in memory',
                         'InterestCache.filter')
            return rates

        logger.debug(
            f'Querying {self.mode} cache \n\t{self._query()}\n\t\t with :maturity={maturity}, :start_date={start_date}, :end_date={end_date}',
            'InterestCache.filter')
        formatter = {'maturity': maturity,
                     'start_date': start_date, 'end_date': end_date}
        results = Cache.execute(
            query=self._query(), formatter=formatter, mode=self.mode)

        if len(results) > 0:
            logger.debug(
                f'Found {maturity} yield on in the cache', 'InterestCache.filter')
            rates = self.to_dict(results)
            self._update_internal_cache(rates, maturity)
            return rates

        logger.debug(
            f'No results found for {maturity} yield in cache', 'InterestCache.filter')
        return None


class CorrelationCache(metaclass=Singleton):
    """
   `scrilla.cache.CorrelationCache` statically accesses *SQLite* functionality from `scrilla.cache.Cache`. It extends basic functionality to cache correlations in a table with columns ``(ticker_1, ticker_2, start_date, end_date, correlation, method, weekends)``. `scrilla.cache.CorrelationCache` has a `scrilla.cache.Singleton` for its `metaclass`, meaning `CorrelationCache` is a singleton; it can only be created once; any subsequent instantiations will return the same instance of `CorrelationCache`.This is done so that all instances of `CorrelationCache` share the same `self.internal_cache`, allowing frequently accessed data to be stored in memory.

    Attributes
    ----------
    1. **internal_cache**: ``dict``
        Dictionary used by `CorrelationCache` to store API responses in memory. Used to quickly access data that is requested frequently.
    2. **inited**: ``bool``
        Flag used to determine if `CorrelationCache` has been instantiated prior to current instantiation.
    3. **sqlite_create_table_transaction**: ``str``
        *SQLite* transaction passed to the super class used to create correlation cache table if it does not already exist.
    4. **sqlite_insert_row_transaction**: ``str``
        *SQLite* transaction used to insert row into correlation cache table.
    5. **sqlite_correlation_query**: ``str```
        *SQLite* query to retrieve correlation from cache.

    .. notes::
        * do not need to order `correlation_query` and `profile_query` because profiles and correlations are uniquely determined by the (`start_date`, `end_date`, 'ticker_1', 'ticker_2')-tuple. More or less. There is a bit of fuzziness, since the permutation of the previous tuple, ('start_date', 'end_date', 'ticker_2', 'ticker_1'), will also be associated with the same correlation value. No other mappings between a date's correlation value and the correlation's tickers are possible though. In other words, the query, for a given (ticker_1, ticker_2)-permutation will only ever return one result.
        * `method` corresponds to the estimation method used by the application to calculate a given statistic. 
        * `weekends` corresponds to a flag representing whether or not the calculation used weekends. This will always be 0 in the case of equities, but for cryptocurrencies, this flag is important and will affect the calculation.
    """
    internal_cache = {}
    inited = False
    sqlite_create_table_transaction = "CREATE TABLE IF NOT EXISTS correlations (ticker_1 TEXT, ticker_2 TEXT, start_date TEXT, end_date TEXT, correlation REAL, method TEXT, weekends INT)"
    sqlite_insert_row_transaction = "INSERT INTO correlations (ticker_1, ticker_2, start_date, end_date, correlation, method, weekends) VALUES (:ticker_1, :ticker_2, :start_date, :end_date, :correlation, :method, :weekends)"
    sqlite_correlation_query = "SELECT correlation FROM correlations WHERE ticker_1=:ticker_1 AND ticker_2=:ticker_2 AND start_date=date(:start_date) AND end_date=date(:end_date) AND method=:method AND weekends=:weekends"

    dynamodb_table_configuration = config.dynamo_correlation_table_conf
    dynamodb_insert_transaction = "INSERT INTO \"correlations\" VALUE { 'ticker_1': ?, 'ticker_2': ?, 'end_date': ?, 'start_date': ?, 'method': ?, 'weekends': ?, 'id': ?, 'correlation': ? }"
    dynamodb_query = "SELECT correlation FROM \"correlations\" WHERE \"ticker_1\"=? AND \"ticker_2\"=? AND \"end_date\"=? AND \"start_date\"=? AND \"method\"=? AND \"weekends\"=?"
    dynamodb_identity_query = "EXISTS(SELECT correlation FROM \"correlations\" WHERE \"ticker_1\"=? AND \"ticker_2\"=? AND \"end_date\"=? AND \"start_date\"=? AND \"method\"=? AND \"weekends\"=?)"

    @staticmethod
    def to_dict(query_results):
        """
        Returns the SQLite query results formatted for the application.

        Parameters
        ----------
        1. **query_results**: ``list``
            Raw SQLite query results.
        """
        return {keys.keys['STATISTICS']['CORRELATION']: query_results[0][0]}

    @staticmethod
    def generate_id(params):
        hashish_key = ''
        for param in params.values():
            if isinstance(param, str):
                hashish_key += param
            elif isinstance(param, (float, int)):
                hashish_key += str(param)
            elif isinstance(param, datetime.date):
                hashish_key += dater.to_string(param)
        return hashish_key

    def __init__(self, mode=settings.CACHE_MODE):
        """
        Initializes `CorrelationCache`. A random UUID will be assigned to the `CorrelationCache` the first time it is created. Since `CorrelationCache` is a singelton, all subsequent instantiations of `CorrelationCache` will have the same UUID. 

        Parameters
        ----------
        1. **mode**: ``str``
            Determines the data source that acts as the cache. Defaults to `scrilla.settings.CACHE_MODE`. Can be set to either `sqlite` or `dynamodb`. 
        """
        if not self.inited:
            self.uuid = uuid.uuid4()
            self.inited = True
        self.mode = mode
        if not files.get_memory_json()['cache'][mode]['correlations']:
            self._table()

    def _table(self):
        if self.mode == 'sqlite':
            Cache.execute(query=self.sqlite_create_table_transaction,
                          mode=self.mode)
        elif self.mode == 'dynamodb':
            self.dynamodb_table_configuration = aws.dynamo_table_conf(
                self.dynamodb_table_configuration)
            Cache.provision(self.dynamodb_table_configuration, self.mode)

    def _insert(self):
        if self.mode == 'sqlite':
            return self.sqlite_insert_row_transaction
        elif self.mode == 'dynamodb':
            return self.dynamodb_insert_transaction

    def _query(self):
        if self.mode == 'sqlite':
            return self.sqlite_correlation_query
        elif self.mode == 'dynamodb':
            return self.dynamodb_query

    def _update_internal_cache(self, params, permuted_params, correlation):
        correl_id = self.generate_id(params)
        permuted_id = self.generate_id(permuted_params)
        self.internal_cache[correl_id] = {'correlation': correlation}
        self.internal_cache[permuted_id] = {'correlation': correlation}
        pass

    def _retrieve_from_internal_cache(self, params, permuted_params):
        first_id = self.generate_id(params)
        second_id = self.generate_id(permuted_params)
        if first_id in list(self.internal_cache.keys()):
            return self.internal_cache[first_id]
        if second_id in list(self.internal_cache.keys()):
            return self.internal_cache[second_id]
        return None

    def save_row(self, ticker_1: str, ticker_2: str, start_date: datetime.date, end_date: datetime.date, correlation: float, weekends: bool, method: str = settings.ESTIMATION_METHOD):
        """
        Uses `self.insert_row_transaction` to save the passed-in information to the SQLite cache.

        Parameters
        ----------
        1. **ticker_1**: ``str``
        2. **ticker_2**: ``str``
        3. **start_date**: ``datetime.date``
        4. **end_date**: ``datetime.date``
        5. **correlation**: ``float``
        6. **weekends**: ``bool``
        7. **method**: ``str``
            *Optional*. Method used to calculate the correlation. Defaults to `scrilla.settings.ESTIMATION_METHOD`, which in turn is configured by the environment variable, *DEFAULT_ESTIMATION_METHOD*.
        """
        # TODO: it would probably make more sense passing in **kwargs...
        logger.verbose(
            f'Saving ({ticker_1}, {ticker_2}) correlation from {start_date} to {end_date} to the cache',
            'CorrelationCache.save_row')
        formatter_1 = {'ticker_1': ticker_1, 'ticker_2': ticker_2,
                       'end_date': end_date, 'start_date': start_date,
                       'method': method, 'weekends': weekends}
        formatter_2 = {'ticker_1': ticker_2, 'ticker_2': ticker_1,
                       'end_date': end_date, 'start_date': start_date,
                       'method': method, 'weekends': weekends}

        # NOTE: if correlation or id are in the dictionary, it screws up this call, so
        # add them after this call. Either that, or add a conditional to the following
        # method.
        self._update_internal_cache(formatter_1, formatter_2, correlation)

        key_1 = self.generate_id(formatter_1)
        key_2 = self.generate_id(formatter_2)

        formatter_1.update({'id': key_1, 'correlation': correlation})
        formatter_2.update({'id': key_2, 'correlation': correlation})

        Cache.execute(
            query=self._insert(), formatter=[formatter_1, formatter_2], mode=self.mode)
        Cache.execute(
            query=self._insert(), formatter=formatter_2, mode=self.mode)

    def filter(self, ticker_1, ticker_2, start_date, end_date, weekends, method=settings.ESTIMATION_METHOD):
        formatter_1 = {'ticker_1': ticker_1, 'ticker_2': ticker_2,
                       'end_date': end_date, 'start_date': start_date,
                       'method': method, 'weekends': weekends}
        formatter_2 = {'ticker_1': ticker_2, 'ticker_2': ticker_1,
                       'end_date': end_date, 'start_date': start_date,
                       'method': method, 'weekends': weekends}

        memory = self._retrieve_from_internal_cache(formatter_1, formatter_2)
        if memory is not None:
            return memory

        logger.debug(
            f'Querying {self.mode} cache \n\t{self._query()}\n\t\t with :ticker_1={ticker_1}, :ticker_2={ticker_2},:start_date={start_date}, :end_date={end_date}', 'CorrelationCache.filter')
        results = Cache.execute(
            query=self._query(), formatter=formatter_1, mode=self.mode)

        if len(results) > 0:
            logger.debug(
                f'Found ({ticker_1},{ticker_2}) correlation in the cache', 'CorrelationCache.filter')
            if self.mode == 'sqlite':
                correl = self.to_dict(results)
            elif self.mode == 'dynamodb':
                correl = results[0]
            self._update_internal_cache(formatter_1, formatter_2, correl)
            return correl

        results = Cache.execute(
            query=self._query(), formatter=formatter_2, mode=self.mode)

        if len(results) > 0:
            logger.debug(
                f'Found ({ticker_1},{ticker_2}) correlation in the cache', 'CorrelationCache.filter')
            if self.mode == 'sqlite':
                correl = self.to_dict(results)
            elif self.mode == 'dynamodb':
                correl = results[0]
            self._update_internal_cache(formatter_1, formatter_2, correl)
            return correl
        logger.debug(
            f'No results found for ({ticker_1}, {ticker_2}) correlation in the cache', 'CorrelationCache.filter')
        return None


class ProfileCache(metaclass=Singleton):
    """
     `scrilla.cache.ProfileCache` statically accesses *SQLite* functionality from `scrilla.cache.Cache`. It extends basic functionality to cache correlations in a table with columns ``(ticker, start_date, end_date, annual_return, annual_volatility, sharpe_ratio, asset_beta, method, weekends)``. `scrilla.cache.ProfileCache` has a `scrilla.cache.Singleton` for its `metaclass`, meaning `CorrelationCache` is a singleton; it can only be created once; any subsequent instantiations will return the same instance of `CorrelationCache`.This is done so that all instances of `CorrelationCache` share the same `self.internal_cache`, allowing frequently accessed data to be stored in memory.

    Attributes
    ----------
    1. **internal_cache**: ``dict``
        Dictionary used by `PriceCache` to store API responses in memory. Used to quickly access data that is requested frequently.
    2. **inited**: ``bool``
        Flag used to determine if `InterestCache` has been instantiated prior to current instantiation.
    3. **sqlite_create_table_transaction**: ``str``
        *SQLite* transaction passed to `scrilla.cache.Cache` used to create profile cache table if it does not already exist.
    4. **sqlite_insert_row_transaction**: ``str``
        *SQLite* transaction used to insert row into correlation cache table.
    5. **sqlite_interest_query**: ``str```
        *SQLite* query to retrieve an interest from cache.
    6. **dynamodb_table_configuration**: ``str``
        Configuration posted to **DynamoDB** when provisioning cache tables.
    7. **dynamo_insert_transaction**: ``str``
        **PartiQL** statement used to insert new value into the **DynamoDB** tables
    8. **dynamo_query**: ``str``
    9. **dynamo_identity_query**: ``str``

    .. notes::
        * do not need to order `correlation_query` and `profile_query` because profiles and correlations are uniquely determined by the (`start_date`, `end_date`, 'ticker_1', 'ticker_2')-tuple. More or less. There is a bit of fuzziness, since the permutation of the previous tuple, ('start_date', 'end_date', 'ticker_2', 'ticker_1'), will also be associated with the same correlation value. No other mappings between a date's correlation value and the correlation's tickers are possible though. In other words, the query, for a given (ticker_1, ticker_2)-permutation will only ever return one result.
        * `method` corresponds to the estimation method used by the application to calculate a given statistic. 
        * `weekends` corresponds to a flag representing whether or not the calculation used weekends. This will always be 0 in the case of equities, but for cryptocurrencies, this flag is important and will affect the calculation.
    """
    internal_cache = {}
    inited = False
    sqlite_create_table_transaction = "CREATE TABLE IF NOT EXISTS profile (id INTEGER PRIMARY KEY, ticker TEXT, start_date TEXT, end_date TEXT, annual_return REAL, annual_volatility REAL, sharpe_ratio REAL, asset_beta REAL, equity_cost REAL, method TEXT, weekends INT)"
    sqlite_filter = "ticker=:ticker AND start_date=date(:start_date) AND end_date=date(:end_date) AND :method=method AND weekends=:weekends"
    sqlite_identity_query = "SELECT id FROM profile WHERE ticker=:ticker AND start_date=:start_date AND end_date=:end_date AND method=:method AND weekends=:weekends"
    sqlite_profile_query = "SELECT ifnull(annual_return, 'empty'), ifnull(annual_volatility, 'empty'), ifnull(sharpe_ratio, 'empty'), ifnull(asset_beta, 'empty'), ifnull(equity_cost, 'empty') FROM profile WHERE {sqlite_filter}".format(
        sqlite_filter=sqlite_filter)

    dynamodb_table_configuration = config.dynamo_profile_table_conf
    dynamodb_profile_query = "SELECT annual_return,annual_volatility,sharpe_ratio,asset_beta,equity_cost FROM \"profile\" WHERE ticker=? AND start_date=? AND end_date=? AND method=? AND weekends=?"
    # dynamodb_identity_query = "EXISTS(SELECT * FROM \"profile\" WHERE ticker=? AND start_date=? AND end_date=? AND method=? AND weekends=?)"
    # See NOTE in save_or_update_row
    dynamodb_identity_query = "SELECT * FROM \"profile\" WHERE ticker=? AND start_date=? AND end_date=? AND method=? AND weekends=?"

    @staticmethod
    def to_dict(query_result, mode=settings.CACHE_MODE):
        """
        Returns the SQLite query results formatted for the application.

        Parameters
        ----------
        1. **query_results**: ``list``
            Raw SQLite query results.
        """
        if mode == 'sqlite':
            return {
                keys.keys['STATISTICS']['RETURN']: query_result[0][0] if query_result[0][0] != 'empty' else None,
                keys.keys['STATISTICS']['VOLATILITY']: query_result[0][1] if query_result[0][1] != 'empty' else None,
                keys.keys['STATISTICS']['SHARPE']: query_result[0][2] if query_result[0][2] != 'empty' else None,
                keys.keys['STATISTICS']['BETA']: query_result[0][3] if query_result[0][3] != 'empty' else None,
                keys.keys['STATISTICS']['EQUITY']: query_result[0][4] if query_result[0][4] != 'empty' else None
            }
        elif mode == 'dynamodb':
            return query_result[0]

    @staticmethod
    def _construct_update(params, mode=settings.CACHE_MODE):
        if mode == 'sqlite':
            update_query = 'UPDATE profile SET '
            for param in params.keys():
                update_query += f'{param}=:{param}'
                if list(params.keys()).index(param) != len(params)-1:
                    update_query += ','
            update_query += " WHERE ticker=:ticker AND start_date=:start_date AND end_date=:end_date AND method=:method AND weekends=:weekends"
            return update_query
        elif mode == 'dynamodb':
            update_query = 'UPDATE profile '
            for param in params.keys():
                update_query += f'SET {param}=? '
            update_query += "WHERE ticker=? AND start_date=? AND end_date=? AND method=? AND weekends=?"
            return update_query

    @staticmethod
    def _construct_insert(params_and_filter, mode=settings.CACHE_MODE):
        if mode == 'sqlite':
            insert_query = 'INSERT INTO profile ('
            for param in params_and_filter.keys():
                insert_query += f'{param}'
                if list(params_and_filter.keys()).index(param) != len(params_and_filter) - 1:
                    insert_query += ","
                else:
                    insert_query += ") VALUES ("
            for param in params_and_filter.keys():
                insert_query += f':{param}'
                if list(params_and_filter.keys()).index(param) != len(params_and_filter) - 1:
                    insert_query += ","
                else:
                    insert_query += ")"
            return insert_query
        elif mode == 'dynamodb':
            insert_query = "INSERT INTO 'profile' VALUE {"
            for param in params_and_filter.keys():
                insert_query += f"'{param}': ?"
                if list(params_and_filter.keys()).index(param) != len(params_and_filter)-1:
                    insert_query += ", "
                else:
                    insert_query += "}"
            return insert_query

    @staticmethod
    def _create_cache_key(filters):
        hashish_key = ''
        for filt in filters.values():
            if isinstance(filt, str):
                hashish_key += filt
            elif isinstance(filt, (int, float)):
                hashish_key += str(filt)
            elif isinstance(filt, datetime.date):
                hashish_key += dater.to_string(filt)
        return hashish_key

    def __init__(self, mode=settings.CACHE_MODE):
        """
        Initializes `ProfileCache`. A random UUID will be assigned to the `ProfileCache` the first time it is created. Since `ProfileCache` is a singelton, all subsequent instantiations of `ProfileCache` will have the same UUID. 

        Parameters
        ----------
        1. **mode**: ``str``
            Determines the data source that acts as the cache. Defaults to `scrilla.settings.CACHE_MODE`. Can be set to either `sqlite` or `dynamodb`. 
        """
        if not self.inited:
            self.uuid = uuid.uuid4()
            self.inited = True

        self.mode = mode

        if not files.get_memory_json()['cache'][mode]['profile']:
            self._table()

    def _table(self):
        if self.mode == 'sqlite':
            Cache.execute(query=self.sqlite_create_table_transaction,
                          mode=self.mode)
        elif self.mode == 'dynamodb':
            self.dynamodb_table_configuration = aws.dynamo_table_conf(
                self.dynamodb_table_configuration)
            Cache.provision(self.dynamodb_table_configuration, self.mode)

    def _query(self):
        if self.mode == 'sqlite':
            return self.sqlite_profile_query
        elif settings.CACHE_MODE == 'dynamodb':
            return self.dynamodb_profile_query

    def _identity(self):
        if self.mode == 'sqlite':
            return self.sqlite_identity_query
        elif self.mode == 'dynamodb':
            return self.dynamodb_identity_query

    def _update_internal_cache(self, profile, keys):
        key = self._create_cache_key(keys)
        self.internal_cache[key] = profile

    def _retrieve_from_internal_cache(self, keys):
        key = self._create_cache_key(keys)
        if key in list(self.internal_cache):
            return self.internal_cache[key]
        return None

    def save_or_update_row(self, ticker: str, start_date: datetime.date, end_date: datetime.date, annual_return: Union[float, None] = None, annual_volatility: Union[float, None] = None, sharpe_ratio: Union[float, None] = None, asset_beta: Union[float, None] = None, equity_cost: Union[float, None] = None, weekends: int = 0, method: str = settings.ESTIMATION_METHOD):
        filters = {'ticker': ticker, 'start_date': start_date,
                   'end_date': end_date, 'method': method, 'weekends': weekends}
        params = {}

        if annual_return is not None:
            params['annual_return'] = annual_return
        if annual_volatility is not None:
            params['annual_volatility'] = annual_volatility
        if sharpe_ratio is not None:
            params['sharpe_ratio'] = sharpe_ratio
        if asset_beta is not None:
            params['asset_beta'] = asset_beta
        if equity_cost is not None:
            params['equity_cost'] = equity_cost

        self._update_internal_cache(params, filters)

        identity = Cache.execute(self._identity(), filters, self.mode)
        # NOTE: in order to uses EXISTS function, need to execute identity query as transaction.
        # will need to differentiate between sqlite and dynamodb mode here since all executes
        # are passed through statement, not transaction...
        # could add a flag to execute method to explicitly perform a transaction.
        # not wild about that idea, though.

        logger.verbose(
            'Attempting to insert/update risk profile into cache', 'ProfileCache.save_or_update_rows')

        if len(identity) == 0:
            return Cache.execute(self._construct_insert({**params, **filters}),
                                 {**params, **filters}, self.mode)
        return Cache.execute(self._construct_update(params),
                             {**params, **filters}, self.mode)

    def filter(self, ticker: str, start_date: datetime.date, end_date: datetime.date, weekends: int = 0, method=settings.ESTIMATION_METHOD):
        filters = {'ticker': ticker, 'start_date': start_date,
                   'end_date': end_date, 'method': method, 'weekends': weekends}

        in_memory = self._retrieve_from_internal_cache(filters)
        if in_memory:
            logger.debug(f'{ticker} profile found in memory',
                         'ProfileCachce.filter')
            return in_memory

        logger.debug(
            f'Querying {self.mode} cache: \n\t{self._query()}\n\t\t with :ticker={ticker}, :start_date={start_date}, :end_date={end_date}', 'ProfileCache.filter')

        result = Cache.execute(
            query=self._query(), formatter=filters, mode=self.mode)

        if len(result) > 0:
            logger.debug(f'{ticker} profile found in cache',
                         'ProfileCache.filter')
            self._update_internal_cache(self.to_dict(result), filters)
            return self.to_dict(result)
        logger.debug(
            f'No results found for {ticker} profile in the cache', 'ProfileCache.filter')
        return None


def init_cache():
    memory = files.get_memory_json()
    if not memory['cache'][settings.CACHE_MODE]['prices']:
        PriceCache()
        memory['cache'][settings.CACHE_MODE]['prices'] = True
    if not memory['cache'][settings.CACHE_MODE]['interest']:
        InterestCache()
        memory['cache'][settings.CACHE_MODE]['interest'] = True
    if not memory['cache'][settings.CACHE_MODE]['profile']:
        ProfileCache()
        memory['cache'][settings.CACHE_MODE]['profile'] = True
    if not memory['cache'][settings.CACHE_MODE]['correlations']:
        CorrelationCache()
        memory['cache'][settings.CACHE_MODE]['correlations'] = True
    files.save_memory_json(memory)
