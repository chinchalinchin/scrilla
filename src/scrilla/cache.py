import sqlite3

from scrilla import settings, static
from scrilla.files import clear_directory
from scrilla.util import outputter

# TODO: before hooking this into the application, i will need a method that returns a dict formatted in the way the application expects. before doing so, test out current cache methods to see if they still work after refactor (fingers crossed) and then test this class in isolation, i.e. build the latest wheel, install it (so settings import is accurate) and then start a python shell and see if class behaves as expected.

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
    create_table_transaction="CREATE TABLE IF NOT EXISTS prices (ticker text, date text, open real, close real)"
    insert_row_transaction="INSERT INTO prices (ticker, date, open, close) VALUES (:ticker, :date, :open, :close)"
    price_query="SELECT date, open, close from prices WHERE ticker = :ticker AND date <= date(:end_date) AND date >= date(:start_date)"

    def __init__(self):
        super().__init__(PriceCache.create_table_transaction)

    @staticmethod
    def to_dict(query_results):
        return { result[0]: { static.keys['PRICES']['OPEN']: result[1], static.keys['PRICES']['CLOSE']: result[2] } for result in query_results }

    def save_row(self, ticker, date, open_price, close_price):
        logger.verbose(F'Saving {ticker} prices on {date} to cache')
        formatter = { 'ticker': ticker, 'date': date, 'open': open_price, 'close': close_price}
        self.execute_transaction(transaction=PriceCache.insert_row_transaction, formatter=formatter)

    def filter_price_cache(self, ticker, start_date, end_date):
        logger.verbose(f'Querying SQLite cache \n\t{PriceCache.price_query}\n\t\t with :ticker={ticker}, :start_date={start_date}, :end_date={end_date}')
        formatter = { 'ticker': ticker, 'start_date': start_date, 'end_date': end_date}
        results = self.execute_query(query=PriceCache.price_query, formatter=formatter)

        if len(results)>0:
            logger.verbose(f'Found {ticker} prices in the cache')
            return self.to_dict(results)
        return None

class StatCache(Cache):
    create_table_transaction="CREATE TABLE IF NOT EXISTS statistics (symbol text, date text, value real)"
    insert_row_transaction="INSERT INTO statistics (symbol, date, value) VALUES (:symbol, :date, :value)"
    stat_query="SELECT date, value FROM statistics WHERE symbol=:symbol AND date <=date(:end_date) AND date>=date(:start_date)"

    def __init__(self):
        super().__init__(StatCache.create_table_transaction)

    @staticmethod
    def to_dict(query_results):
        return { result[0]: result[1] for result in query_results }

    def save_row(self, symbol, date, value):
        logger.verbose(f'Saving {symbol} statistic on {date} to cache')
        formatter = { 'symbol': symbol, 'date': date, 'value': value }
        self.execute_transaction(transaction=StatCache.insert_row_transaction, formatter=formatter)
    
    def filter_stat_cache(self, symbol, start_date, end_date):
        logger.verbose(f'Querying SQLite cache \n\t{StatCache.stat_query}\n\t\t with :symbol={symbol}, :start_date={start_date}, :end_date={end_date}')
        formatter = { 'symbol': symbol, 'start_date': start_date, 'end_date': end_date }
        results = self.execute_query(query=StatCache.stat_query, formatter=formatter)

        if len(results)>0:
            logger.verbose(f'Found {symbol} statistics in the cache')
            return self.to_dict(results)
        return None

class DividendCache(Cache):
    create_table_transaction="CREATE TABLE IF NOT EXISTS dividends (ticker text, date text, amount real)"
    insert_row_transaction="INSERT INTO dividends (ticker, date, amount) VALUES (:ticker, :date, :amount)"
    dividend_query="SELECT date, amount FROM dividends WHERE ticker=:ticker"

    def __init__(self):
        super().__init__(DividendCache.create_table_transaction)
    
    @staticmethod
    def to_dict(query_results):
        return { result[0]: result[1]  for result in query_results }
    
    def save_row(self, ticker, date, amount):
        logger.verbose(f'Saving {ticker} dividend on {date} to cache')
        formatter = { 'ticker' : ticker, 'date': date, 'amount': amount}
        self.execute_transaction(transaction=DividendCache.insert_row_transaction, formatter=formatter)
    
    def filter_dividend_cache(self, ticker):
        logger.verbose(f'Querying SQLite cache \n\t{DividendCache.dividend_query}\n\t\t with :ticker={ticker}')
        formatter = { 'ticker': ticker }
        results = self.execute_query(query=DividendCache.dividend_query, formatter=formatter)

        if len(results)>0:
            logger.verbose(f'Found {ticker} dividends in the cache')
            # TODO: need to ensure new dividend prices are ALWAYS saved somehow. Can't always defer to the cache as the source of truth.
            return self.to_dict(results)
        return None

class CorrelationCache(Cache):
    create_table_transaction="CREATE TABLE IF NOT EXISTS correlations (ticker_1 text, ticker_2 text, start_date text, end_date text, correlation real)"
    insert_row_transaction="INSERT INTO correlations (ticker_1, ticker_2, start_date, end_date, correlation) VALUES (:ticker_1, :ticker_2, :start_date, :end_date, :correlation)"
    correlation_query="SELECT correlation FROM correlations WHERE ticker_1=:ticker_1 AND ticker_2=:ticker_2 AND start_date=date(:start_date) AND end_date=date(:end_date)"

    def __init__(self):
        super().__init__(CorrelationCache.create_table_transaction)
    
    @staticmethod
    def to_dict(query_results):
        return { static.keys['STATISTICS']['CORRELATION']: query_results[0][0] }

    def save_row(self, ticker_1, ticker_2, start_date, end_date, correlation):
        logger.verbose(f'Saving ({ticker_1}, {ticker_2}) correlation from {start_date} to {end_date} to the cacche')
        formatter_1 = { 'ticker_1': ticker_1, 'ticker_2': ticker_2, 
                        'start_date': start_date, 'end_date': end_date, 'correlation': correlation}
        formatter_2 = { 'ticker_1': ticker_2, 'ticker_2': ticker_1, 
                        'start_date': start_date, 'end_date': end_date, 'correlation': correlation}
        self.execute_transaction(transaction=CorrelationCache.insert_row_transaction, formatter=formatter_1)
        self.execute_transaction(transaction=CorrelationCache.insert_row_transaction, formatter=formatter_2)
    
    def filter_correlation_cache(self, ticker_1, ticker_2, start_date, end_date):
        formatter_1 = { 'ticker_1': ticker_1, 'ticker_2': ticker_2, 
                        'start_date': start_date, 'end_date': end_date}
        formatter_2 = { 'ticker_1': ticker_2, 'ticker_2': ticker_1, 
                        'start_date': start_date, 'end_date': end_date}
        
        logger.verbose(f'Querying SQLite cache \n\t{CorrelationCache.correlation_query}\n\t\t with :ticker_1={ticker_1}, :ticker_2={ticker_2}')
        results = self.execute_query(query=CorrelationCache.correlation_query, formatter=formatter_1)
        if len(results)>0:
            logger.verbose(f'Found ({ticker_1},{ticker_2}) correlation in the cache')
            return self.to_dict(results)
        results = self.execute_query(query=CorrelationCache.correlation_query, formatter=formatter_2)
        if len(results)>0:
            logger.verbose(f'Found ({ticker_1},{ticker_2}) correlation in the cache')
            return self.to_dict(results)
        return None

class ProfileCache(Cache):
    create_table_transaction="CREATE TABLE IF NOT EXISTS profile (id INTEGER PRIMARY KEY, ticker TEXT, start_date TEXT, end_date TEXT, annual_return REAL, annual_volatility REAL, sharpe_ratio REAL, asset_beta REAL, equity_cost REAL)"
    
    query_filter="ticker=:ticker AND start_date=date(:start_date) AND end_date=date(:end_date)"
    identity_query="(SELECT id FROM profile WHERE ticker=:ticker AND start_date=:start_date AND end_date=:end_date)"
    value_args="(id, ticker, start_date, end_date, annual_return, annual_volatility, sharpe_ratio, asset_beta, equity_cost)"

    return_query="(SELECT annual_return FROM profile WHERE {query_filter})".format(query_filter=query_filter)
    vol_query="(SELECT annual_volatility FROM profile WHERE {query_filter})".format(query_filter=query_filter)
    sharpe_query="(SELECT sharpe_ratio FROM profile WHERE {query_filter})".format(query_filter=query_filter)
    beta_query="(SELECT asset_beta FROM profile WHERE {query_filter})".format(query_filter=query_filter)
    equity_query="(SELECT equity_cost FROM profile WHERE {query_filter})".format(query_filter=query_filter)

    update_return_transaction="INSERT or REPLACE INTO profile {value_args} VALUES ({identity_query}, :ticker, :start_date, :end_date, :annual_return, {vol_query}, {sharpe_query}, {beta_query}, {equity_query})".format(
                                identity_query=identity_query, value_args=value_args, vol_query=vol_query, sharpe_query=sharpe_query, beta_query=beta_query, equity_query=equity_query)
    update_vol_transaction="INSERT or REPLACE INTO profile {value_args} VALUES ({identity_query}, :ticker, :start_date, :end_date, {return_query}, :annual_volatility, {sharpe_query}, {beta_query}, {equity_query})".format(
                                identity_query=identity_query, value_args=value_args, return_query=return_query, sharpe_query=sharpe_query, beta_query=beta_query, equity_query=equity_query)
    update_sharpe_transaction="INSERT or REPLACE INTO profile {value_args} VALUES ({identity_query}, :ticker, :start_date, :end_date, {return_query}, {vol_query}, :sharpe_ratio, {beta_query}, {equity_query})".format(
                                identity_query=identity_query, value_args=value_args, return_query=return_query, vol_query=vol_query, beta_query=beta_query, equity_query=equity_query)
    update_beta_transaction="INSERT or REPLACE INTO profile {value_args} VALUES ({identity_query}, :ticker, :start_date, :end_date, {return_query}, {vol_query}, {sharpe_query}, :asset_beta, {equity_query})".format(
                                identity_query=identity_query, value_args=value_args, return_query=return_query, vol_query=vol_query, sharpe_query=sharpe_query, equity_query=equity_query)
    update_equity_tranasction="INSERT or REPLACE INTO profile {value_args} VALUES ({identity_query}, :ticker, :start_date, :end_date, {return_query}, {vol_query}, {sharpe_query}, {beta_query}, :equity_cost)".format(
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

    def save_or_update_row(self, ticker, start_date, end_date, annual_return=None, annual_volatility=None, sharpe_ratio=None, asset_beta=None, equity_cost=None):
        formatter = { 'ticker': ticker, 'start_date': start_date, 'end_date': end_date}
        
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

    def filter_profile_cache(self, ticker, start_date, end_date):
        logger.verbose(f'Querying SQLite cache: \n\t{ProfileCache.profile_query}\n\t\t with :ticker={ticker}, :start_date={start_date}, :end_date={end_date}') 
        formatter = { 'ticker': ticker, 'start_date': start_date, 'end_date': end_date}
        result = self.execute_query(query=ProfileCache.profile_query, formatter=formatter)

        if len(result)>0:
            return self.to_dict(result)
        return None
