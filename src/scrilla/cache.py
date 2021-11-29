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
import sqlite3
import datetime
from typing import Union
from scrilla import settings
from scrilla.static import keys
from scrilla.util import outputter

logger = outputter.Logger("scrilla.cache", settings.LOG_LEVEL)


class Cache():
    """
    Super class for other types of caches. Takes as a parameter in its constructor a **SQLite** `CREATE TABLE` query and executes it against the SQLite database located at `scrilla.settings.CACHE_SQLITE_FILE`, which in turn is configured by the **SQLITE_FILE** environment variable. 
    """

    def __init__(self, table_transaction):
        self.execute_transaction(table_transaction)

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
        con = sqlite3.connect(settings.CACHE_SQLITE_FILE)
        executor = con.cursor()
        if formatter is not None:
            executor.execute(transaction, formatter)
        else:
            executor.execute(transaction)
        con.commit()
        con.close()

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
        con = sqlite3.connect(settings.CACHE_SQLITE_FILE)
        con.row_factory = sqlite3.Row
        executor = con.cursor()
        if formatter is not None:
            return executor.execute(query, formatter).fetchall()
        return executor.execute(query).fetchall()


class PriceCache(Cache):
    """
    Inherits *SQLite* functionality from `scrilla.cache.Cache`. Extends basic functionality to cache correlation calculations in a table with columns `(ticker, date, open, close)`, with a unique constraint on the tuplie `(ticker, date)`, i.e. records in the *PriceCache* are uniquely determined by the the combination of the ticker symbol and the date.

    Attributes
    ----------
    1. **create_table_transaction**: ``str``
        *SQLite* transaction passed to the super class used to create price cache table if it does not already exist.
    2. **insert_row_transaction**: ``str``
        *SQLite* transaction used to insert row into price cache table.
    3. **price_query**: ``str```
        *SQLite* query to retrieve prices from cache.
    """
    create_table_transaction = "CREATE TABLE IF NOT EXISTS prices (ticker text, date text, open real, close real, UNIQUE(ticker, date))"
    insert_row_transaction = "INSERT OR IGNORE INTO prices (ticker, date, open, close) VALUES (:ticker, :date, :open, :close)"
    price_query = "SELECT date, open, close from prices WHERE ticker = :ticker AND date <= date(:end_date) AND date >= date(:start_date) ORDER BY date(date) DESC"

    def __init__(self):
        super().__init__(PriceCache.create_table_transaction)

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

    def save_row(self, ticker, date, open_price, close_price):
        logger.verbose(
            F'Attempting to insert {ticker} prices on {date} to cache')
        formatter = {'ticker': ticker, 'date': date,
                     'open': open_price, 'close': close_price}
        self.execute_transaction(
            transaction=PriceCache.insert_row_transaction, formatter=formatter)

    def filter_price_cache(self, ticker, start_date, end_date):
        logger.debug(
            f'Querying SQLite cache \n\t{PriceCache.price_query}\n\t\t with :ticker={ticker}, :start_date={start_date}, :end_date={end_date}')
        formatter = {'ticker': ticker,
                     'start_date': start_date, 'end_date': end_date}
        results = self.execute_query(
            query=PriceCache.price_query, formatter=formatter)

        if len(results) > 0:
            logger.debug(f'Found {ticker} prices in the cache')
            return self.to_dict(results)
        logger.debug(f'No results found for {ticker} prices in the cache')
        return None


class InterestCache(Cache):
    """
    Inherits *SQLite* functionality from `scrilla.cache.Cache`. Extends basic functionality to cache interest rate data in a table with columns `(maturity, date, value)`.

    Attributes
    ----------
    1. **create_table_transaction**: ``str``
        *SQLite* transaction passed to the super class used to create correlation cache table if it does not already exist.
    2. **insert_row_transaction**: ``str``
        *SQLite* transaction used to insert row into correlation cache table.
    3. **int_query**: ``str```
        *SQLite* query to retrieve an interest from cache.
    """
    create_table_transaction = "CREATE TABLE IF NOT EXISTS interest(maturity text, date text, value real, UNIQUE(maturity, date))"
    insert_row_transaction = "INSERT OR IGNORE INTO interest (maturity, date, value) VALUES (:maturity, :date, :value)"
    int_query = "SELECT date, value FROM interest WHERE maturity=:maturity AND date <=date(:end_date) AND date>=date(:start_date) ORDER BY date(date) DESC"

    def __init__(self):
        super().__init__(InterestCache.create_table_transaction)

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

    def save_row(self, date, value):
        for index, maturity in enumerate(keys.keys['YIELD_CURVE']):
            logger.verbose(f'Saving {maturity} yield on {date} to cache')
            formatter = {'maturity': maturity,
                         'date': date, 'value': value[index]}
            self.execute_transaction(
                transaction=InterestCache.insert_row_transaction, formatter=formatter)

    def filter_interest_cache(self, maturity, start_date, end_date):
        logger.debug(
            f'Querying SQLite cache \n\t{InterestCache.int_query}\n\t\t with :maturity={maturity}, :start_date={start_date}, :end_date={end_date}')
        formatter = {'maturity': maturity,
                     'start_date': start_date, 'end_date': end_date}
        results = self.execute_query(
            query=InterestCache.int_query, formatter=formatter)

        if len(results) > 0:
            logger.debug(f'Found {maturity} yield on in the cache')
            return self.to_dict(results)
        logger.debug(f'No results found for {maturity} yield in cache')
        return None


class CorrelationCache(Cache):
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
    create_table_transaction = "CREATE TABLE IF NOT EXISTS correlations (ticker_1 TEXT, ticker_2 TEXT, start_date TEXT, end_date TEXT, correlation REAL, method TEXT, weekends INT)"
    insert_row_transaction = "INSERT INTO correlations (ticker_1, ticker_2, start_date, end_date, correlation, method, weekends) VALUES (:ticker_1, :ticker_2, :start_date, :end_date, :correlation, :method, :weekends)"
    correlation_query = "SELECT correlation FROM correlations WHERE ticker_1=:ticker_1 AND ticker_2=:ticker_2 AND start_date=date(:start_date) AND end_date=date(:end_date) AND method=:method AND weekends=:weekends"

    def __init__(self):
        super().__init__(CorrelationCache.create_table_transaction)

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
        self.execute_transaction(
            transaction=CorrelationCache.insert_row_transaction, formatter=formatter_1)
        self.execute_transaction(
            transaction=CorrelationCache.insert_row_transaction, formatter=formatter_2)

    def filter_correlation_cache(self, ticker_1, ticker_2, start_date, end_date, weekends, method=settings.ESTIMATION_METHOD):
        formatter_1 = {'ticker_1': ticker_1, 'ticker_2': ticker_2, 'method': method,
                       'start_date': start_date, 'end_date': end_date, 'weekends': weekends}
        formatter_2 = {'ticker_1': ticker_2, 'ticker_2': ticker_1, 'method': method,
                       'start_date': start_date, 'end_date': end_date, 'weekends': weekends}

        logger.debug(
            f'Querying SQLite cache \n\t{CorrelationCache.correlation_query}\n\t\t with :ticker_1={ticker_1}, :ticker_2={ticker_2},:start_date={start_date}, :end_date={end_date}')
        results = self.execute_query(
            query=CorrelationCache.correlation_query, formatter=formatter_1)
        if len(results) > 0:
            logger.debug(
                f'Found ({ticker_1},{ticker_2}) correlation in the cache')
            return self.to_dict(results)
        results = self.execute_query(
            query=CorrelationCache.correlation_query, formatter=formatter_2)
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
    create_table_transaction = "CREATE TABLE IF NOT EXISTS profile (id INTEGER PRIMARY KEY, ticker TEXT, start_date TEXT, end_date TEXT, annual_return REAL, annual_volatility REAL, sharpe_ratio REAL, asset_beta REAL, equity_cost REAL, method TEXT, weekends INT)"

    query_filter = "ticker=:ticker AND start_date=date(:start_date) AND end_date=date(:end_date) AND :method=method AND weekends=:weekends"
    identity_query = "(SELECT id FROM profile WHERE ticker=:ticker AND start_date=:start_date AND end_date=:end_date AND method=:method AND weekends=:weekends)"
    value_args = "(id, ticker, start_date, end_date, annual_return, annual_volatility, sharpe_ratio, asset_beta, equity_cost, method, weekends)"

    return_query = "(SELECT annual_return FROM profile WHERE {query_filter})".format(
        query_filter=query_filter)
    vol_query = "(SELECT annual_volatility FROM profile WHERE {query_filter})".format(
        query_filter=query_filter)
    sharpe_query = "(SELECT sharpe_ratio FROM profile WHERE {query_filter})".format(
        query_filter=query_filter)
    beta_query = "(SELECT asset_beta FROM profile WHERE {query_filter})".format(
        query_filter=query_filter)
    equity_query = "(SELECT equity_cost FROM profile WHERE {query_filter})".format(
        query_filter=query_filter)

    update_return_transaction = "INSERT or REPLACE INTO profile {value_args} VALUES ({identity_query}, :ticker, :start_date, :end_date, :annual_return, {vol_query}, {sharpe_query}, {beta_query}, {equity_query}, :method, :weekends)".format(
        identity_query=identity_query, value_args=value_args, vol_query=vol_query, sharpe_query=sharpe_query, beta_query=beta_query, equity_query=equity_query)
    update_vol_transaction = "INSERT or REPLACE INTO profile {value_args} VALUES ({identity_query}, :ticker, :start_date, :end_date, {return_query}, :annual_volatility, {sharpe_query}, {beta_query}, {equity_query}, :method, :weekends)".format(
        identity_query=identity_query, value_args=value_args, return_query=return_query, sharpe_query=sharpe_query, beta_query=beta_query, equity_query=equity_query)
    update_sharpe_transaction = "INSERT or REPLACE INTO profile {value_args} VALUES ({identity_query}, :ticker, :start_date, :end_date, {return_query}, {vol_query}, :sharpe_ratio, {beta_query}, {equity_query}, :method, :weekends)".format(
        identity_query=identity_query, value_args=value_args, return_query=return_query, vol_query=vol_query, beta_query=beta_query, equity_query=equity_query)
    update_beta_transaction = "INSERT or REPLACE INTO profile {value_args} VALUES ({identity_query}, :ticker, :start_date, :end_date, {return_query}, {vol_query}, {sharpe_query}, :asset_beta, {equity_query}, :method, :weekends)".format(
        identity_query=identity_query, value_args=value_args, return_query=return_query, vol_query=vol_query, sharpe_query=sharpe_query, equity_query=equity_query)
    update_equity_tranasction = "INSERT or REPLACE INTO profile {value_args} VALUES ({identity_query}, :ticker, :start_date, :end_date, {return_query}, {vol_query}, {sharpe_query}, {beta_query}, :equity_cost, :method, :weekends)".format(
        identity_query=identity_query, value_args=value_args, return_query=return_query, vol_query=vol_query, sharpe_query=sharpe_query, beta_query=beta_query)

    profile_query = "SELECT ifnull(annual_return, 'empty'), ifnull(annual_volatility, 'empty'), ifnull(sharpe_ratio, 'empty'), ifnull(asset_beta, 'empty'), ifnull(equity_cost, 'empty') FROM profile WHERE {query_filter}".format(
        query_filter=query_filter)

    def __init__(self):
        super().__init__(ProfileCache.create_table_transaction)

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

    def save_or_update_row(self, ticker: str, start_date: datetime.date, end_date: datetime.date, annual_return: Union[float, None] = None, annual_volatility: Union[float, None] = None, sharpe_ratio: Union[float, None] = None, asset_beta: Union[float, None] = None, equity_cost: Union[float, None] = None, weekends: int = 0, method: str = settings.ESTIMATION_METHOD):
        formatter = {'ticker': ticker, 'start_date': start_date,
                     'end_date': end_date, 'method': method, 'weekends': weekends}

        if annual_return is not None:
            logger.verbose(
                f'Updating SQLite cache... \n\t{ProfileCache.update_return_transaction}\n\t\t with :ticker={ticker}, :start_date={start_date}, :end_date={end_date}, :annual_return={annual_return}')
            formatter['annual_return'] = annual_return
            self.execute_transaction(
                transaction=ProfileCache.update_return_transaction, formatter=formatter)
        if annual_volatility is not None:
            logger.verbose(
                f'Updating SQLite cache... \n\t{ProfileCache.update_vol_transaction}\n\t\t with :ticker={ticker}, :start_date={start_date}, :end_date={end_date}, :annual_volatility={annual_volatility}')
            formatter['annual_volatility'] = annual_volatility
            self.execute_transaction(
                transaction=ProfileCache.update_vol_transaction, formatter=formatter)
        if sharpe_ratio is not None:
            logger.verbose(
                f'Updating SQLite cache... \n\t{ProfileCache.update_sharpe_transaction}\n\t\t with :ticker={ticker}, :start_date={start_date}, :end_date={end_date}, :sharpe_ratio={sharpe_ratio}')
            formatter['sharpe_ratio'] = sharpe_ratio
            self.execute_transaction(
                transaction=ProfileCache.update_sharpe_transaction, formatter=formatter)
        if asset_beta is not None:
            logger.verbose(
                f'Updating SQLite cache \n\t{ProfileCache.update_beta_transaction}\n\t\t with :ticker={ticker}, :start_date={start_date}, :end_date={end_date}, :asset_beta={asset_beta}')
            formatter['asset_beta'] = asset_beta
            self.execute_transaction(
                transaction=ProfileCache.update_beta_transaction, formatter=formatter)
        if equity_cost is not None:
            logger.verbose(
                f'Updating SQLite cache \n\t{ProfileCache.update_return_transaction}\n\t\t with :ticker={ticker}, :start_date={start_date}, :end_date={end_date}, :equity_cost={equity_cost}')
            formatter['equity_cost'] = equity_cost
            self.execute_transaction(
                transaction=ProfileCache.update_equity_tranasction, formatter=formatter)

    def filter_profile_cache(self, ticker: str, start_date: datetime.date, end_date: datetime.date, weekends: int = 0, method=settings.ESTIMATION_METHOD):
        logger.debug(
            f'Querying SQLite cache: \n\t{ProfileCache.profile_query}\n\t\t with :ticker={ticker}, :start_date={start_date}, :end_date={end_date}')
        formatter = {'ticker': ticker, 'start_date': start_date,
                     'end_date': end_date, 'method': method, 'weekends': weekends}
        result = self.execute_query(
            query=ProfileCache.profile_query, formatter=formatter)

        if len(result) > 0:
            logger.debug(f'{ticker} profile found in cache')
            return self.to_dict(result)
        logger.debug(f'No results found for {ticker} profile in the cache')
        return None
