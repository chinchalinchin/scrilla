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


import sqlite3

from scrilla import settings, static
from scrilla.util import outputter

logger = outputter.Logger("cache", settings.LOG_LEVEL)

class Cache():
    """
    Methods
    -------

    1. execute_transaction

        Parameters
        ----------
        1. transactions: str\n
            Statement to be executed and committed. \n \n
        2. formatter: dict
            Dictionary of parameters used to format statement. Statements are formatted with DB-API's name substitution. See sqlite3 documentation for more information:https://docs.python.org/3/library/sqlite3.html.  \n \n
    
    2. query_database

        Parameters
        ----------
        1. query : str\n
            Query to be exectued.
        2. formatter: dict
            Dictionary of parameters used to format statement. Statements are formatted with DB-API's name substitution. See sqlite3 documentation for more information:https://docs.python.org/3/library/sqlite3.html.  \n \n

    """

    def __init__(self, table_transaction):
        self.execute_transaction(table_transaction)

    @staticmethod
    def execute_transaction(transaction, formatter=None):
        con = sqlite3.connect(settings.CACHE_SQLITE_FILE)
        executor =  con.cursor()
        if formatter is not None:
            executor.execute(transaction, formatter)
        else:
            executor.execute(transaction)
        con.commit()
        con.close()

    @staticmethod
    def execute_query(query, formatter=None):
        con = sqlite3.connect(settings.CACHE_SQLITE_FILE)
        con.row_factory = sqlite3.Row
        executor = con.cursor()
        if formatter is not None:
            return executor.execute(query, formatter).fetchall()
        return executor.execute(query).fetchall()

class PriceCache(Cache):
    create_table_transaction="CREATE TABLE IF NOT EXISTS prices (ticker text, date text, open real, close real, UNIQUE(ticker, date))"
    insert_row_transaction="INSERT OR IGNORE INTO prices (ticker, date, open, close) VALUES (:ticker, :date, :open, :close)"
    price_query="SELECT date, open, close from prices WHERE ticker = :ticker AND date <= date(:end_date) AND date >= date(:start_date) ORDER BY date(date) DESC"

    def __init__(self):
        super().__init__(PriceCache.create_table_transaction)

    @staticmethod
    def to_dict(query_results):
        return { result[0]: { static.keys['PRICES']['OPEN']: result[1], static.keys['PRICES']['CLOSE']: result[2] } for result in query_results }

    def save_row(self, ticker, date, open_price, close_price):
        logger.verbose(F'Attempting to insert {ticker} prices on {date} to cache')
        formatter = { 'ticker': ticker, 'date': date, 'open': open_price, 'close': close_price}
        self.execute_transaction(transaction=PriceCache.insert_row_transaction, formatter=formatter)

    def filter_price_cache(self, ticker, start_date, end_date):
        logger.debug(f'Querying SQLite cache \n\t{PriceCache.price_query}\n\t\t with :ticker={ticker}, :start_date={start_date}, :end_date={end_date}')
        formatter = { 'ticker': ticker, 'start_date': start_date, 'end_date': end_date}
        results = self.execute_query(query=PriceCache.price_query, formatter=formatter)

        if len(results)>0:
            logger.debug(f'Found {ticker} prices in the cache')
            return self.to_dict(results)
        logger.debug(f'No results found for {ticker} prices in the cache')
        return None

class InterestCache(Cache):
    create_table_transaction="CREATE TABLE IF NOT EXISTS interest(maturity text, date text, value real, UNIQUE(maturity, date))"
    insert_row_transaction="INSERT OR IGNORE INTO interest (maturity, date, value) VALUES (:maturity, :date, :value)"
    stat_query="SELECT date, value FROM interest WHERE maturity=:maturity AND date <=date(:end_date) AND date>=date(:start_date) ORDER BY date(date) DESC"

    def __init__(self):
        super().__init__(InterestCache.create_table_transaction)

    @staticmethod
    def to_dict(query_results):
        return { result[0]: result[1] for result in query_results }

    def save_row(self, date, value):
        for index, maturity in enumerate(static.keys['YIELD_CURVE']):
            logger.verbose(f'Saving {maturity} yield on {date} to cache')
            formatter = { 'maturity': maturity, 'date': date, 'value': value[index] }
            self.execute_transaction(transaction=InterestCache.insert_row_transaction, formatter=formatter)
    
    def filter_interest_cache(self, maturity, start_date, end_date):
        logger.debug(f'Querying SQLite cache \n\t{InterestCache.stat_query}\n\t\t with :maturity={maturity}, :start_date={start_date}, :end_date={end_date}')
        formatter = { 'maturity': maturity, 'start_date': start_date, 'end_date': end_date }
        results = self.execute_query(query=InterestCache.stat_query, formatter=formatter)

        if len(results)>0:
            logger.debug(f'Found {maturity} yield on in the cache')
            return self.to_dict(results)
        logger.debug(f'No results found for {maturity} yield in cache')
        return None

# NOTE: do not need to order `correlation_query` and `profile_query` because profiles and correlations are uniquely 
#       determined by the (`start_date`, `end_date`, 'ticker_1', 'ticker_2')-tuple. More or less. There is a bit of 
#       fuzziness, since the permutation of the previous tuple, ('start_date', 'end_date', 'ticker_2', 'ticker_1'), 
#       will also be associated with the same correlation value. No other mappings between a date's correlation value
#       and the correlation's tickers are possible though. In other words, the query, for a given 
#       (ticker_1, ticker_2)-permutation will only ever return one result.
class CorrelationCache(Cache):
        # TODO: extra save_or_update argument for estimation method, i.e. moments, percentiles or likelihood, need to update tables
    create_table_transaction="CREATE TABLE IF NOT EXISTS correlations (ticker_1 TEXT, ticker_2 TEXT, start_date TEXT, end_date TEXT, correlation REAL, method TEXT)"
    insert_row_transaction="INSERT INTO correlations (ticker_1, ticker_2, start_date, end_date, correlation, method) VALUES (:ticker_1, :ticker_2, :start_date, :end_date, :correlation, :method)"
    correlation_query="SELECT correlation FROM correlations WHERE ticker_1=:ticker_1 AND ticker_2=:ticker_2 AND start_date=date(:start_date) AND end_date=date(:end_date) AND method=:method"

    def __init__(self):
        super().__init__(CorrelationCache.create_table_transaction)
    
    @staticmethod
    def to_dict(query_results):
        return { static.keys['STATISTICS']['CORRELATION']: query_results[0][0] }

    def save_row(self, ticker_1, ticker_2, start_date, end_date, correlation, method = settings.ESTIMATION_METHOD):
        logger.verbose(f'Saving ({ticker_1}, {ticker_2}) correlation from {start_date} to {end_date} to the cacche')
        formatter_1 = { 'ticker_1': ticker_1, 'ticker_2': ticker_2, 'method': method,
                        'start_date': start_date, 'end_date': end_date, 'correlation': correlation}
        formatter_2 = { 'ticker_1': ticker_2, 'ticker_2': ticker_1, 'method': method,
                        'start_date': start_date, 'end_date': end_date, 'correlation': correlation}
        self.execute_transaction(transaction=CorrelationCache.insert_row_transaction, formatter=formatter_1)
        self.execute_transaction(transaction=CorrelationCache.insert_row_transaction, formatter=formatter_2)
    
    def filter_correlation_cache(self, ticker_1, ticker_2, start_date, end_date, method = settings.ESTIMATION_METHOD):
        formatter_1 = { 'ticker_1': ticker_1, 'ticker_2': ticker_2, 'method': method,
                        'start_date': start_date, 'end_date': end_date}
        formatter_2 = { 'ticker_1': ticker_2, 'ticker_2': ticker_1, 'method': method,
                        'start_date': start_date, 'end_date': end_date}
        
        logger.debug(f'Querying SQLite cache \n\t{CorrelationCache.correlation_query}\n\t\t with :ticker_1={ticker_1}, :ticker_2={ticker_2}')
        results = self.execute_query(query=CorrelationCache.correlation_query, formatter=formatter_1)
        if len(results)>0:
            logger.debug(f'Found ({ticker_1},{ticker_2}) correlation in the cache')
            return self.to_dict(results)
        results = self.execute_query(query=CorrelationCache.correlation_query, formatter=formatter_2)
        if len(results)>0:
            logger.debug(f'Found ({ticker_1},{ticker_2}) correlation in the cache')
            return self.to_dict(results)
        logger.debug(f'No results found for ({ticker_1}, {ticker_2}) correlation in the cache')
        return None

class ProfileCache(Cache):
    # TODO: extra save_or_update argument for estimation method, i.e. moments, percentiles or likelihood, need to update tables

    create_table_transaction="CREATE TABLE IF NOT EXISTS profile (id INTEGER PRIMARY KEY, ticker TEXT, start_date TEXT, end_date TEXT, annual_return REAL, annual_volatility REAL, sharpe_ratio REAL, asset_beta REAL, equity_cost REAL, method TEXT)"
    
    query_filter="ticker=:ticker AND start_date=date(:start_date) AND end_date=date(:end_date) AND :method=method"
    identity_query="(SELECT id FROM profile WHERE ticker=:ticker AND start_date=:start_date AND end_date=:end_date AND :method=method)"
    value_args="(id, ticker, start_date, end_date, annual_return, annual_volatility, sharpe_ratio, asset_beta, equity_cost, method)"

    return_query="(SELECT annual_return FROM profile WHERE {query_filter})".format(query_filter=query_filter)
    vol_query="(SELECT annual_volatility FROM profile WHERE {query_filter})".format(query_filter=query_filter)
    sharpe_query="(SELECT sharpe_ratio FROM profile WHERE {query_filter})".format(query_filter=query_filter)
    beta_query="(SELECT asset_beta FROM profile WHERE {query_filter})".format(query_filter=query_filter)
    equity_query="(SELECT equity_cost FROM profile WHERE {query_filter})".format(query_filter=query_filter)

    update_return_transaction="INSERT or REPLACE INTO profile {value_args} VALUES ({identity_query}, :ticker, :start_date, :end_date, :annual_return, {vol_query}, {sharpe_query}, {beta_query}, {equity_query}, :method)".format(
                                identity_query=identity_query, value_args=value_args, vol_query=vol_query, sharpe_query=sharpe_query, beta_query=beta_query, equity_query=equity_query)
    update_vol_transaction="INSERT or REPLACE INTO profile {value_args} VALUES ({identity_query}, :ticker, :start_date, :end_date, {return_query}, :annual_volatility, {sharpe_query}, {beta_query}, {equity_query}, :method)".format(
                                identity_query=identity_query, value_args=value_args, return_query=return_query, sharpe_query=sharpe_query, beta_query=beta_query, equity_query=equity_query)
    update_sharpe_transaction="INSERT or REPLACE INTO profile {value_args} VALUES ({identity_query}, :ticker, :start_date, :end_date, {return_query}, {vol_query}, :sharpe_ratio, {beta_query}, {equity_query}, :method)".format(
                                identity_query=identity_query, value_args=value_args, return_query=return_query, vol_query=vol_query, beta_query=beta_query, equity_query=equity_query)
    update_beta_transaction="INSERT or REPLACE INTO profile {value_args} VALUES ({identity_query}, :ticker, :start_date, :end_date, {return_query}, {vol_query}, {sharpe_query}, :asset_beta, {equity_query}, :method)".format(
                                identity_query=identity_query, value_args=value_args, return_query=return_query, vol_query=vol_query, sharpe_query=sharpe_query, equity_query=equity_query)
    update_equity_tranasction="INSERT or REPLACE INTO profile {value_args} VALUES ({identity_query}, :ticker, :start_date, :end_date, {return_query}, {vol_query}, {sharpe_query}, {beta_query}, :equity_cost, :method)".format(
                                identity_query=identity_query, value_args=value_args, return_query=return_query, vol_query=vol_query, sharpe_query=sharpe_query, beta_query=beta_query)

    profile_query="SELECT ifnull(annual_return, 'empty'), ifnull(annual_volatility, 'empty'), ifnull(sharpe_ratio, 'empty'), ifnull(asset_beta, 'empty'), ifnull(equity_cost, 'empty') FROM profile WHERE {query_filter}".format(query_filter=query_filter)

    def __init__(self):
        super().__init__(ProfileCache.create_table_transaction)

    @staticmethod
    def to_dict(query_result):
        return {  static.keys['STATISTICS']['RETURN'] : query_result[0][0] if query_result[0][0] != 'empty' else None, 
                  static.keys['STATISTICS']['VOLATILITY'] : query_result[0][1] if query_result[0][1] != 'empty' else None,
                  static.keys['STATISTICS']['SHARPE'] : query_result[0][2] if query_result[0][2] != 'empty' else None,
                  static.keys['STATISTICS']['BETA'] : query_result[0][3] if query_result[0][3] != 'empty' else None,
                  static.keys['STATISTICS']['EQUITY'] : query_result[0][4] if query_result[0][4] != 'empty' else None }

    def save_or_update_row(self, ticker, start_date, end_date, annual_return=None, annual_volatility=None, sharpe_ratio=None, asset_beta=None, equity_cost=None, method=settings.ESTIMATION_METHOD):
        formatter = { 'ticker': ticker, 'start_date': start_date, 'end_date': end_date, 'method': method}
        
        if annual_return is not None:
            logger.verbose(f'Updating SQLite cache... \n\t{ProfileCache.update_return_transaction}\n\t\t with :ticker={ticker}, :start_date={start_date}, :end_date={end_date}, :annual_return={annual_return}')
            formatter['annual_return'] = annual_return
            self.execute_transaction(transaction=ProfileCache.update_return_transaction, formatter=formatter)
        if annual_volatility is not None:
            logger.verbose(f'Updating SQLite cache... \n\t{ProfileCache.update_vol_transaction}\n\t\t with :ticker={ticker}, :start_date={start_date}, :end_date={end_date}, :annual_volatility={annual_volatility}')
            formatter['annual_volatility'] = annual_volatility
            self.execute_transaction(transaction=ProfileCache.update_vol_transaction, formatter=formatter)        
        if sharpe_ratio is not None:
            logger.verbose(f'Updating SQLite cache... \n\t{ProfileCache.update_sharpe_transaction}\n\t\t with :ticker={ticker}, :start_date={start_date}, :end_date={end_date}, :sharpe_ratio={sharpe_ratio}')
            formatter['sharpe_ratio'] = sharpe_ratio
            self.execute_transaction(transaction=ProfileCache.update_sharpe_transaction, formatter=formatter)
        if asset_beta is not None:
            logger.verbose(f'Updating SQLite cache \n\t{ProfileCache.update_beta_transaction}\n\t\t with :ticker={ticker}, :start_date={start_date}, :end_date={end_date}, :asset_beta={asset_beta}')
            formatter['asset_beta'] = asset_beta
            self.execute_transaction(transaction=ProfileCache.update_beta_transaction, formatter=formatter)
        if equity_cost is not None:
            logger.verbose(f'Updating SQLite cache \n\t{ProfileCache.update_return_transaction}\n\t\t with :ticker={ticker}, :start_date={start_date}, :end_date={end_date}, :equity_cost={equity_cost}')
            formatter['equity_cost'] = equity_cost
            self.execute_transaction(transaction=ProfileCache.update_equity_tranasction, formatter=formatter)

    def filter_profile_cache(self, ticker, start_date, end_date, method = settings.ESTIMATION_METHOD):
        logger.debug(f'Querying SQLite cache: \n\t{ProfileCache.profile_query}\n\t\t with :ticker={ticker}, :start_date={start_date}, :end_date={end_date}') 
        formatter = { 'ticker': ticker, 'start_date': start_date, 'end_date': end_date, 'method': method }
        result = self.execute_query(query=ProfileCache.profile_query, formatter=formatter)

        if len(result)>0:
            logger.debug(f'{ticker} profile found in cache')
            return self.to_dict(result)
        logger.debug(f'No results found for {ticker} profile in the cache')
        return None
