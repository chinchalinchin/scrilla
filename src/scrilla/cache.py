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
from scrilla import settings

if settings.CACHE_MODE == 'sqlite':
    import sqlite3
elif settings.CACHE_MODE == 'dynamodb':
    from scrilla.cloud import aws

import datetime
from typing import Union
from scrilla import errors
from scrilla.static import keys
from scrilla.util import outputter

logger = outputter.Logger("scrilla.cache", settings.LOG_LEVEL)


class Cache():
    """
    Class with static methods all other Caches employ. This class tries to hide as much implementation detail as possible behind its methods, i.e. this class is concerned with executing commits and transactions, whereas the other cache classes are concerned with the data structure that is created with these methods.
    """

    @staticmethod
    def provision_table(table_configuration):
        pass

    @staticmethod
    def execute_transaction(transaction, formatter=None):
        """
        Executes and commits a SQLite transaction.

        Parameters
        ----------
        1. **transaction**: ``str``
            Statement to be executed and committed.
        2. formatter: ``dict``
            Dictionary of parameters used to format statement. Statements are formatted with DB-API's name substitution. See [sqlite3 documentation](https://docs.python.org/3/library/sqlite3.html) for more information.
        """
        if settings.CACHE_MODE == 'sqlite':
            con = sqlite3.connect(settings.CACHE_SQLITE_FILE)
            executor = con.cursor()
            if formatter is not None:
                executor.execute(transaction, formatter)
            else:
                executor.execute(transaction)
            con.commit()
            con.close()
        elif settings.CACHE_MODE == 'dynamodb':
            pass
            # TODO
        else:
            raise errors.ConfigurationError(
                'CACHE_MODE has not been set in "settings.py"')

    @staticmethod
    def execute_query(query, formatter=None):
        """
        Executes a read-write SQLite query. 

        Parameters
        ----------
        1. **query**: ``str``
            Query to be exectued.
        2. **formatter**: ``dict``
            Dictionary of parameters used to format statement. Statements are formatted with DB-API's name substitution. See [sqlite3 documentation](https://docs.python.org/3/library/sqlite3.html) for more information. 

        Returns
        -------
        ``list``
            A list containing the results of the query.
        """
        if settings.CACHE_MODE == 'sqlite':
            con = sqlite3.connect(settings.CACHE_SQLITE_FILE)
            con.row_factory = sqlite3.Row
            executor = con.cursor()
            if formatter is not None:
                return executor.execute(query, formatter).fetchall()
            return executor.execute(query).fetchall()
        elif settings.CACHE_MODE == 'dynamodb':
            pass
            # TODO
        else:
            raise errors.ConfigurationError(
                'CACHE_MODE has not been set in "settings.py"')


class PriceCache():
    """
    Statically asseses *SQLite* functionality from `scrilla.cache.Cache`. Extends basic functionality to cache prices in a table with columns `(ticker, date, open, close)`, with a unique constraint on the tuplie `(ticker, date)`, i.e. records in the *PriceCache* are uniquely determined by the the combination of the ticker symbol and the date.

    Attributes
    ----------
    1. **sqlite_create_table_transaction**: ``str``
        *SQLite* transaction passed to the super class used to create price cache table if it does not already exist.
    2. **sqlite_insert_row_transaction**: ``str``
        *SQLite* transaction used to insert row into price cache table.
    3. **sqlite_price_query**: ``str```
        *SQLite* query to retrieve prices from cache.
    """
    sqlite_create_table_transaction = "CREATE TABLE IF NOT EXISTS prices (ticker text, date text, open real, close real, UNIQUE(ticker, date))"
    sqlite_insert_row_transaction = "INSERT OR IGNORE INTO prices (ticker, date, open, close) VALUES (:ticker, :date, :open, :close)"
    sqlite_price_query = "SELECT date, open, close from prices WHERE ticker = :ticker AND date <= date(:end_date) AND date >= date(:start_date) ORDER BY date(date) DESC"

    dynamodb_table_configuration = {
        'AttributeDefinitions': [
            {
                'AttributeName': 'ticker',
                'AttributeType': 'S'
            },
            {
                'AttributeName': 'date',
                'AttributeType': 'S'
            }
        ],
        'TableName': 'prices',
        'KeySchema': [
            {
                'AttributeName': 'ticker',
                'KeyType': 'HASH'
            },
            {
                'AttributeName': 'date',
                'KeyType': 'RANGE'
            }
        ]
    }

    @staticmethod
    def to_dict(query_results):
        """
        Returns the SQLite query results formatted for the application.

        Parameters
        ----------
        1. **query_results**: ``list``
            Raw SQLite query results.
        """
        return {result[0]: {keys.keys['PRICES']['OPEN']: result[1],
                            keys.keys['PRICES']['CLOSE']: result[2]} for result in query_results}

    def __init__(self):
        self._table()

    def _table(self):
        if settings.CACHE_MODE == 'sqlite':
            Cache.execute_transaction(self.sqlite_create_table_transaction)
        elif settings.CACHE_MODE == 'dynamodb':
            Cache.provision_table(self.dynamodb_table_configuration)

    def _insert(self):
        if settings.CACHE_MODE == 'sqlite':
            return self.sqlite_insert_row_transaction
        elif settings.CACHE_MODE == 'dynamodb':
            pass

    def _query(self):
        if settings.CACHE_MODE == 'sqlite':
            return self.sqlite_price_query
        elif settings.CACHE_MODE == 'dynamodb':
            pass

    def save_row(self, ticker, date, open_price, close_price):
        logger.verbose(
            F'Attempting to insert {ticker} prices on {date} to cache')
        formatter = {'ticker': ticker, 'date': date,
                     'open': open_price, 'close': close_price}
        Cache.execute_transaction(
            transaction=self._insert(), formatter=formatter)

    def filter_price_cache(self, ticker, start_date, end_date):
        logger.debug(
            f'Querying {settings.CACHE_MODE} cache \n\t{self._query()}\n\t\t with :ticker={ticker}, :start_date={start_date}, :end_date={end_date}')
        formatter = {'ticker': ticker,
                     'start_date': start_date, 'end_date': end_date}
        results = Cache.execute_query(
            query=self._query(), formatter=formatter)

        if len(results) > 0:
            logger.debug(f'Found {ticker} prices in the cache')
            return self.to_dict(results)
        logger.debug(f'No results found for {ticker} prices in the cache')
        return None


class InterestCache():
    """
    Statically accesses *SQLite* functionality from `scrilla.cache.Cache`. Extends basic functionality to cache interest rate data in a table with columns `(maturity, date, value)`.

    Attributes
    ----------
    1. **create_table_transaction**: ``str``
        *SQLite* transaction passed to the super class used to create correlation cache table if it does not already exist.
    2. **insert_row_transaction**: ``str``
        *SQLite* transaction used to insert row into correlation cache table.
    3. **int_query**: ``str```
        *SQLite* query to retrieve an interest from cache.
    """
    sqlite_create_table_transaction = "CREATE TABLE IF NOT EXISTS interest(maturity text, date text, value real, UNIQUE(maturity, date))"
    sqlite_insert_row_transaction = "INSERT OR IGNORE INTO interest (maturity, date, value) VALUES (:maturity, :date, :value)"
    sqlite_interest_query = "SELECT date, value FROM interest WHERE maturity=:maturity AND date <=date(:end_date) AND date>=date(:start_date) ORDER BY date(date) DESC"

    dynamodb_table_configuration = {
        'AttributeDefinitions': [
            {
                'AttributeName': 'maturity',
                'AttributeType': 'S'
            },
            {
                'AttributeName': 'date',
                'AttributeType': 'S'
            }
        ],
        'TableName': 'interest',
        'KeySchema': [
            {
                'AttributeName': 'maturity',
                'KeyType': 'HASH'
            },
            {
                'AttributeName': 'date',
                'KeyType': 'RANGE'
            }
        ]
    }

    @staticmethod
    def to_dict(query_results):
        """
        Returns the SQLite query results formatted for the application.

        Parameters
        ----------
        1. **query_results**: ``list``
            Raw SQLite query results.
        """
        return {result[0]: result[1] for result in query_results}

    def __init__(self):
        self._table()

    def _table(self):
        if settings.CACHE_MODE == 'sqlite':
            Cache.execute_transaction(self.sqlite_create_table_transaction)
        elif settings.CACHE_MODE == 'dynamodb':
            pass
            # TODO

    def _insert(self):
        if settings.CACHE_MODE == 'sqlite':
            return self.sqlite_insert_row_transaction
        elif settings.CACHE_MODE == 'dynamodb':
            pass
            # TODO

    def _query(self):
        if settings.CACHE_MODE == 'sqlite':
            return self.sqlite_interest_query
        elif settings.CACHE_MODE == 'dynamodb':
            pass
            # TODO

    def save_row(self, date, value):
        for index, maturity in enumerate(keys.keys['YIELD_CURVE']):
            logger.verbose(f'Saving {maturity} yield on {date} to cache')
            formatter = {'maturity': maturity,
                         'date': date, 'value': value[index]}
            Cache.execute_transaction(
                transaction=self._insert(), formatter=formatter)

    def filter_interest_cache(self, maturity, start_date, end_date):
        logger.debug(
            f'Querying {settings.CACHE_MODE} cache \n\t{self._query()}\n\t\t with :maturity={maturity}, :start_date={start_date}, :end_date={end_date}')
        formatter = {'maturity': maturity,
                     'start_date': start_date, 'end_date': end_date}
        results = Cache.execute_query(
            query=self._query(), formatter=formatter)

        if len(results) > 0:
            logger.debug(f'Found {maturity} yield on in the cache')
            return self.to_dict(results)
        logger.debug(f'No results found for {maturity} yield in cache')
        return None


class CorrelationCache():
    """
    Inherits *SQLite* functionality from `scrilla.cache.Cache`. Extends basic functionality to cache correlation calculations in a table with columns `(ticker_1, ticker_2, correlation, start_date, end_date, estimation_method, weekends)`.

    Attributes
    ----------
    1. **create_table_transaction**: ``str``
        *SQLite* transaction passed to the super class used to create correlation cache table if it does not already exist.
    2. **insert_row_transaction**: ``str``
        *SQLite* transaction used to insert row into correlation cache table.
    3. **correlation_query**: ``str```
        *SQLite* query to retrieve correlation from cache.

    .. notes::
        * do not need to order `correlation_query` and `profile_query` because profiles and correlations are uniquely determined by the (`start_date`, `end_date`, 'ticker_1', 'ticker_2')-tuple. More or less. There is a bit of fuzziness, since the permutation of the previous tuple, ('start_date', 'end_date', 'ticker_2', 'ticker_1'), will also be associated with the same correlation value. No other mappings between a date's correlation value and the correlation's tickers are possible though. In other words, the query, for a given (ticker_1, ticker_2)-permutation will only ever return one result.
    """
    sqlite_create_table_transaction = "CREATE TABLE IF NOT EXISTS correlations (ticker_1 TEXT, ticker_2 TEXT, start_date TEXT, end_date TEXT, correlation REAL, method TEXT, weekends INT)"
    sqlite_insert_row_transaction = "INSERT INTO correlations (ticker_1, ticker_2, start_date, end_date, correlation, method, weekends) VALUES (:ticker_1, :ticker_2, :start_date, :end_date, :correlation, :method, :weekends)"
    sqlite_correlation_query = "SELECT correlation FROM correlations WHERE ticker_1=:ticker_1 AND ticker_2=:ticker_2 AND start_date=date(:start_date) AND end_date=date(:end_date) AND method=:method AND weekends=:weekends"

    dynamodb_table_configuration = {
        'AttributeDefinitions': [
            {
                'AttributeName': 'ticker_1',
                'AttributeType': 'S'
            },
            {
                'AttributeName': 'ticker_2',
                'AttributeType': 'S'
            },
            {
                'AttributeName': 'start_date',
                'AttributeType': 'S'
            },
            {
                'AttributeName': 'end_date',
                'AttributeType': 'S'
            }
        ],
        'TableName': 'correlation',
        'KeySchema': [
            {
                'AttributeName': 'ticker_1',
                'KeyType': 'HASH'
            },
            {
                'AttributeName': 'ticker_2',
                'KeyType': 'HASH'
            },
            {
                'AttributeName': 'start_date',
                'KeyType': 'RANGE'
            },
            {
                'AttributeName': 'end_date',
                'KeyType': 'RANGE'
            }
        ]
    }

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

    def __init__(self):
        self._table()

    def _table(self):
        if settings.CACHE_MODE == 'sqlite':
            Cache.execute_transaction(self.sqlite_create_table_transaction)
        elif settings.CACHE_MODE == 'dynamodb':
            pass
            # TODO

    def _insert(self):
        if settings.CACHE_MODE == 'sqlite':
            return self.sqlite_insert_row_transaction
        elif settings.CACHE_MODE == 'dynamodb':
            pass
            # TODO

    def _query(self):
        if settings.CACHE_MODE == 'sqlite':
            return self.sqlite_correlation_query
        elif settings.CACHE_MODE == 'dynamodb':
            pass
            # TODO

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
        logger.verbose(
            f'Saving ({ticker_1}, {ticker_2}) correlation from {start_date} to {end_date} to the cacche')
        formatter_1 = {'ticker_1': ticker_1, 'ticker_2': ticker_2, 'method': method,
                       'start_date': start_date, 'end_date': end_date, 'correlation': correlation,
                       'weekends': weekends}
        formatter_2 = {'ticker_1': ticker_2, 'ticker_2': ticker_1, 'method': method,
                       'start_date': start_date, 'end_date': end_date, 'correlation': correlation,
                       'weekends': weekends}
        Cache.execute_transaction(
            transaction=self._insert(), formatter=formatter_1)
        Cache.execute_transaction(
            transaction=self._insert(), formatter=formatter_2)

    def filter_correlation_cache(self, ticker_1, ticker_2, start_date, end_date, weekends, method=settings.ESTIMATION_METHOD):
        formatter_1 = {'ticker_1': ticker_1, 'ticker_2': ticker_2, 'method': method,
                       'start_date': start_date, 'end_date': end_date, 'weekends': weekends}
        formatter_2 = {'ticker_1': ticker_2, 'ticker_2': ticker_1, 'method': method,
                       'start_date': start_date, 'end_date': end_date, 'weekends': weekends}

        logger.debug(
            f'Querying {settings.CACHE_MODE} cache \n\t{self._query()}\n\t\t with :ticker_1={ticker_1}, :ticker_2={ticker_2},:start_date={start_date}, :end_date={end_date}')
        results = Cache.execute_query(
            query=self._query(), formatter=formatter_1)
        if len(results) > 0:
            logger.debug(
                f'Found ({ticker_1},{ticker_2}) correlation in the cache')
            return self.to_dict(results)
        results = Cache.execute_query(
            query=self._query(), formatter=formatter_2)
        if len(results) > 0:
            logger.debug(
                f'Found ({ticker_1},{ticker_2}) correlation in the cache')
            return self.to_dict(results)
        logger.debug(
            f'No results found for ({ticker_1}, {ticker_2}) correlation in the cache')
        return None


class ProfileCache(Cache):
    """
    Inherits *SQLite* functionality from `scrilla.cache.Cache`. Extends basic functionality to cache risk profile calculations in a table with columns `(ticker, start_date, end_date, annual_return, annual_volatility, sharpe_ration, asset_beta, equity_cost, estimation_method)`.

    Attributes
    ----------
    1. **create_table_transaction**: ``str``
        *SQLite* transaction passed to the super class used to create correlation cache table if it does not already exist.
    """
    sqlite_create_table_transaction = "CREATE TABLE IF NOT EXISTS profile (id INTEGER PRIMARY KEY, ticker TEXT, start_date TEXT, end_date TEXT, annual_return REAL, annual_volatility REAL, sharpe_ratio REAL, asset_beta REAL, equity_cost REAL, method TEXT, weekends INT)"

    sqlite_filter = "ticker=:ticker AND start_date=date(:start_date) AND end_date=date(:end_date) AND :method=method AND weekends=:weekends"
    identity_query = "(SELECT id FROM profile WHERE ticker=:ticker AND start_date=:start_date AND end_date=:end_date AND method=:method AND weekends=:weekends)"
    value_args = "(id, ticker, start_date, end_date, annual_return, annual_volatility, sharpe_ratio, asset_beta, equity_cost, method, weekends)"

    sqlite_return_query = "(SELECT annual_return FROM profile WHERE {sqlite_filter})".format(
        sqlite_filter=sqlite_filter)
    sqlite_vol_query = "(SELECT annual_volatility FROM profile WHERE {sqlite_filter})".format(
        sqlite_filter=sqlite_filter)
    sqlite_sharpe_query = "(SELECT sharpe_ratio FROM profile WHERE {sqlite_filter})".format(
        sqlite_filter=sqlite_filter)
    sqlite_beta_query = "(SELECT asset_beta FROM profile WHERE {sqlite_filter})".format(
        sqlite_filter=sqlite_filter)
    sqlite_equity_query = "(SELECT equity_cost FROM profile WHERE {sqlite_filter})".format(
        sqlite_filter=sqlite_filter)

    sqlite_update_return_transaction = "INSERT or REPLACE INTO profile {value_args} VALUES ({identity_query}, :ticker, :start_date, :end_date, :annual_return, {sqlite_vol_query}, {sqlite_sharpe_query}, {sqlite_beta_query}, {sqlite_equity_query}, :method, :weekends)".format(
        identity_query=identity_query, value_args=value_args, sqlite_vol_query=sqlite_vol_query, sqlite_sharpe_query=sqlite_sharpe_query, sqlite_beta_query=sqlite_beta_query, sqlite_equity_query=sqlite_equity_query)
    sqlite_update_vol_transaction = "INSERT or REPLACE INTO profile {value_args} VALUES ({identity_query}, :ticker, :start_date, :end_date, {sqlite_return_query}, :annual_volatility, {sqlite_sharpe_query}, {sqlite_beta_query}, {sqlite_equity_query}, :method, :weekends)".format(
        identity_query=identity_query, value_args=value_args, sqlite_return_query=sqlite_return_query, sqlite_sharpe_query=sqlite_sharpe_query, sqlite_beta_query=sqlite_beta_query, sqlite_equity_query=sqlite_equity_query)
    sqlite_update_sharpe_transaction = "INSERT or REPLACE INTO profile {value_args} VALUES ({identity_query}, :ticker, :start_date, :end_date, {sqlite_return_query}, {sqlite_vol_query}, :sharpe_ratio, {sqlite_beta_query}, {sqlite_equity_query}, :method, :weekends)".format(
        identity_query=identity_query, value_args=value_args, sqlite_return_query=sqlite_return_query, sqlite_vol_query=sqlite_vol_query, sqlite_beta_query=sqlite_beta_query, sqlite_equity_query=sqlite_equity_query)
    sqlite_update_beta_transaction = "INSERT or REPLACE INTO profile {value_args} VALUES ({identity_query}, :ticker, :start_date, :end_date, {sqlite_return_query}, {sqlite_vol_query}, {sqlite_sharpe_query}, :asset_beta, {sqlite_equity_query}, :method, :weekends)".format(
        identity_query=identity_query, value_args=value_args, sqlite_return_query=sqlite_return_query, sqlite_vol_query=sqlite_vol_query, sqlite_sharpe_query=sqlite_sharpe_query, sqlite_equity_query=sqlite_equity_query)
    sqlite_update_equity_tranasction = "INSERT or REPLACE INTO profile {value_args} VALUES ({identity_query}, :ticker, :start_date, :end_date, {sqlite_return_query}, {sqlite_vol_query}, {sqlite_sharpe_query}, {sqlite_beta_query}, :equity_cost, :method, :weekends)".format(
        identity_query=identity_query, value_args=value_args, sqlite_return_query=sqlite_return_query, sqlite_vol_query=sqlite_vol_query, sqlite_sharpe_query=sqlite_sharpe_query, sqlite_beta_query=sqlite_beta_query)

    sqlite_profile_query = "SELECT ifnull(annual_return, 'empty'), ifnull(annual_volatility, 'empty'), ifnull(sharpe_ratio, 'empty'), ifnull(asset_beta, 'empty'), ifnull(equity_cost, 'empty') FROM profile WHERE {sqlite_filter}".format(
        sqlite_filter=sqlite_filter)

    dynamodb_table_configuration = {
        'AttributeDefinitions': [
            {
                'AttributeName': 'ticker',
                'AttributeType': 'S'
            },
            {
                'AttributeName': 'start_date',
                'AttributeType': 'S'
            },
            {
                'AttributeName': 'end_date',
                'AttributeType': 'S'
            }
        ],
        'TableName': 'profile',
        'KeySchema': [
            {
                'AttributeName': 'ticker',
                'KeyType': 'HASH'
            },
            {
                'AttributeName': 'start_date',
                'KeyType': 'RANGE'
            },
            {
                'AttributeName': 'end_date',
                'KeyType': 'RANGE'
            }
        ]
    }

    @staticmethod
    def to_dict(query_result):
        """
        Returns the SQLite query results formatted for the application.

        Parameters
        ----------
        1. **query_results**: ``list``
            Raw SQLite query results.
        """
        return {keys.keys['STATISTICS']['RETURN']: query_result[0][0] if query_result[0][0] != 'empty' else None,
                keys.keys['STATISTICS']['VOLATILITY']: query_result[0][1] if query_result[0][1] != 'empty' else None,
                keys.keys['STATISTICS']['SHARPE']: query_result[0][2] if query_result[0][2] != 'empty' else None,
                keys.keys['STATISTICS']['BETA']: query_result[0][3] if query_result[0][3] != 'empty' else None,
                keys.keys['STATISTICS']['EQUITY']: query_result[0][4] if query_result[0][4] != 'empty' else None}

    def __init__(self):
        self._table()

    def _table(self):
        if settings.CACHE_MODE == 'sqlite':
            Cache.execute_transaction(self.sqlite_create_table_transaction)
        elif settings.CACHE_MODE == 'dynamodb':
            pass
            # TODO

    def _update(self, query_type):
        if settings.CACHE_MODE == 'sqlite':
            if query_type == 'return':
                return self.sqlite_update_return_transaction
            elif query_type == 'volatility':
                return self.sqlite_update_vol_transaction
            elif query_type == 'sharpe':
                return self.sqlite_update_sharpe_transaction
            elif query_type == 'beta':
                return self.sqlite_update_beta_transaction
            elif query_type == 'equity':
                return self.sqlite_update_equity_tranasction
        elif settings.CACHE_MODE == 'dynamodb':
            pass
            # TODO

    def _query(self):
        if settings.CACHE_MODE == 'sqlite':
            return self.sqlite_profile_query
        elif settings.CACHE_MODE == 'dynamodb':
            pass
            # TODO

    def save_or_update_row(self, ticker: str, start_date: datetime.date, end_date: datetime.date, annual_return: Union[float, None] = None, annual_volatility: Union[float, None] = None, sharpe_ratio: Union[float, None] = None, asset_beta: Union[float, None] = None, equity_cost: Union[float, None] = None, weekends: int = 0, method: str = settings.ESTIMATION_METHOD):
        formatter = {'ticker': ticker, 'start_date': start_date,
                     'end_date': end_date, 'method': method, 'weekends': weekends}

        if annual_return is not None:
            logger.verbose(
                f'Updating {settings.CACHE_MODE} cache... \n\t{self._update("return")}\n\t\t with :ticker={ticker}, :start_date={start_date}, :end_date={end_date}, :annual_return={annual_return}')
            formatter['annual_return'] = annual_return
            Cache.execute_transaction(
                transaction=self._update('return'), formatter=formatter)
        if annual_volatility is not None:
            logger.verbose(
                f'Updating {settings.CACHE_MODE} cache... \n\t{self._update("volatility")}\n\t\t with :ticker={ticker}, :start_date={start_date}, :end_date={end_date}, :annual_volatility={annual_volatility}')
            formatter['annual_volatility'] = annual_volatility
            Cache.execute_transaction(
                transaction=self._update('volatility'), formatter=formatter)
        if sharpe_ratio is not None:
            logger.verbose(
                f'Updating {settings.CACHE_MODE} cache... \n\t{self._update("sharpe")}\n\t\t with :ticker={ticker}, :start_date={start_date}, :end_date={end_date}, :sharpe_ratio={sharpe_ratio}')
            formatter['sharpe_ratio'] = sharpe_ratio
            Cache.execute_transaction(
                transaction=self._update("sharpe"), formatter=formatter)
        if asset_beta is not None:
            logger.verbose(
                f'Updating {settings.CACHE_MODE} cache \n\t{self._update("beta")}\n\t\t with :ticker={ticker}, :start_date={start_date}, :end_date={end_date}, :asset_beta={asset_beta}')
            formatter['asset_beta'] = asset_beta
            Cache.execute_transaction(
                transaction=self._update('beta'), formatter=formatter)
        if equity_cost is not None:
            logger.verbose(
                f'Updating {settings.CACHE_MODE} cache \n\t{self._update("return")}\n\t\t with :ticker={ticker}, :start_date={start_date}, :end_date={end_date}, :equity_cost={equity_cost}')
            formatter['equity_cost'] = equity_cost
            Cache.execute_transaction(
                transaction=self._update('return'), formatter=formatter)

    def filter_profile_cache(self, ticker: str, start_date: datetime.date, end_date: datetime.date, weekends: int = 0, method=settings.ESTIMATION_METHOD):
        logger.debug(
            f'Querying {settings.CACHE_MODE} cache: \n\t{self._query()}\n\t\t with :ticker={ticker}, :start_date={start_date}, :end_date={end_date}')
        formatter = {'ticker': ticker, 'start_date': start_date,
                     'end_date': end_date, 'method': method, 'weekends': weekends}
        result = self.execute_query(
            query=self._query(), formatter=formatter)

        if len(result) > 0:
            logger.debug(f'{ticker} profile found in cache')
            return self.to_dict(result)
        logger.debug(f'No results found for {ticker} profile in the cache')
        return None
