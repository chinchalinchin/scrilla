import sqlite3

from scrilla import settings, static
from scrilla.util import outputter

# TODO: before hooking this into the application, i will need a method that returns a dict formatted in the way the application expects. before doing so, test out current cache methods to see if they still work after refactor (fingers crossed) and then test this class in isolation, i.e. build the latest wheel, install it (so settings import is accurate) and then start a python shell and see if class behaves as expected.

logger = outputter.Logger("services", settings.LOG_LEVEL)

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

    def execute_transaction(self, transaction, formatter=None):
        con = sqlite3.connect(settings.CACHE_SQLITE_FILE)
        executor =  con.cursor()
        if formatter is not None:
            executor.execute(transaction, formatter)
        else:
            executor.execute(transaction)
        con.commit()
        con.close()

    def execute_query(self, query, formatter=None):
        con = sqlite3.connect(settings.CACHE_SQLITE_FILE)
        con.row_factory = sqlite3.Row
        executor = con.cursor()
        if formatter is not None:
            return executor.execute(query, formatter).fetchall()
        return executor.execute(query).fetchall()

class PriceCache(Cache):
    create_table_transaction="CREATE TABLE IF NOT EXISTS prices (ticker text, date text, open real, close real)"
    insert_row_transaction="INSERT INTO prices VALUES (:ticker, :date, :open, :close)"
    price_query="SELECT date, open, close from prices WHERE ticker = :ticker AND date <= date(:end_date) AND date >= date(:start_date)"

    def __init__(self):
        self.execute_transaction(PriceCache.create_table_transaction)

    @staticmethod
    def to_dict(query_results):
        return { result[0]: { static.keys['PRICES']['OPEN']: result[1], static.keys['PRICES']['CLOSE']: result[2] } for result in query_results }

    def save_row(self, ticker, date, open, close):
        formatter = { 'ticker': ticker, 'date': date, 'open': open, 'close': close}
        self.execute_transaction(transaction=PriceCache.insert_row_transaction, formatter=formatter)

    def filter_price_cache(self, ticker, start_date, end_date):
        formatter = { 'ticker': ticker, 'start_date': start_date, 'end_date': end_date}

        logger.verbose(f'Querying SQLite database: {PriceCache.price_query} with :ticker={ticker}, :start_date={start_date}, :end_date={end_date}')
        results = self.execute_query(query=PriceCache.price_query, formatter=formatter)

        if len(results)>0:
            # TODO: need to check if len(results) = days_between(start_date, end_date)
                # every time the market closes and prices are updated.
                # may need to check outside of this method though. don't want to couple services and models too tightly.
            return self.to_dict(results)
        else:
            return None

class ProfileCache(Cache):
    create_table_transaction="CREATE TABLE IF NOT EXISTS profile (ticker text, start_date text, end_date text, annual_return real, annual_volatility real, sharpe_ratio real, asset_beta real, equity_cost real)"
    
    value_args="(ticker, start_date, end_date, annual_return, annual_volatility, sharpe_ratio, asset_beta, equity_cost)"
    query_filter="ticker=:ticker AND start_date=date(:start_date) AND end_date=date(:end_date)"

    return_query="(SELECT annual_return FROM profile WHERE {query_filter}".format(query_filter=query_filter)
    vol_query="(SELECT annual_volatility FROM profile WHERE {query_filter})".format(query_filter=query_filter)
    sharpe_query="(SELECT sharpe_ratio FROM profile WHERE {query_filter})".format(query_filter=query_filter)
    beta_query="(SELECT asset_beta FROM profile WHERE {query_filter})".format(query_filter=query_filter)
    equity_query="(SELECCT equity_cost FROM profile WHERE {query_filter}".format(query_filter=query_filter)

    update_return_transaction="INSERT or REPLACE INTO profile {value_args} \
                            VALUES (:ticker, :start_date, :end_date, :annual_return, {vol_query}, {sharpe_query}, {beta_query}, {equity_query}".format(
                                value_args=value_args, vol_query=vol_query, sharpe_query=sharpe_query, beta_query=beta_query, equity_query=equity_query
                            )
    update_vol_transaction="INSERT or REPLACE INTO profile {value_args} \
                            VALUES (:ticker, :start_date, :end_date, {return_query}, :annual_volatility, {sharpe_query}, {beta_query}, {equity_query}".format(
                                value_args=value_args, return_query=return_query, sharpe_query=sharpe_query, beta_query=beta_query, equity_query=equity_query
                            )
    update_sharpe_transaction="INSERT or REPLACE INTO profile {value_args} \
                            VALUES (:ticker, :start_date, :end_date, {return_query}, {vol_query}, :sharpe_ratio, {beta_query}, {equity_query}".format(
                                value_args=value_args, return_query=return_query, vol_query=vol_query, beta_query=beta_query, equity_query=equity_query
                            )
    update_beta_transaction="INSERT or REPLACE INTO profile {value_args} \
                            VALUES (:ticker, :start_date, :end_date, {return_query}, {vol_query}, {sharpe_query}, :asset_beta, {equity_query}".format(
                                value_args=value_args, return_query=return_query, vol_query=vol_query, sharpe_query=sharpe_query, equity_query=equity_query
                            )
    update_equity_tranasction="INSERT or REPLACE INTO profile {value_args} \
                            VALUES (:ticker, :start_date, :end_date, {return_query}, {vol_query}, {sharpe_query}, {beta_query}, :equity_cost".format(
                                value_args=value_args, return_query=return_query, vol_query=vol_query, sharpe_query=sharpe_query, beta_query=beta_query
                            )
    profile_query="SELECT annual_return, annual_volatility, sharpe_ratio, asset_beta, equity_cost from profile WHERE ticker = :ticker AND end_date=date(:end_date) AND start_date=date(:start_date)"

    def __init__(self):
        self.execute_transaction(ProfileCache.create_table_transaction)

    @staticmethod
    def to_dict(self, query_result):
        return {  static.keys['STATISTICS']['RETURN'] : query_result[0], 
                  static.keys['STATISTICS']['VOLATILITY'] : query_result[1],
                  static.keys['STATISTICS']['SHARPE'] : query_result[2],
                  static.keys['STATISTICS']['BETA'] : query_result[3],
                  static.keys['STATISTICS']['EQUITY'] : query_result[4] }

    def save_or_update_row(self, ticker, start_date, end_date, annual_return=None, annual_volatility=None, sharpe_ratio=None, asset_beta=None, equity_cost=None):
        formatter = { 'ticker': ticker, 'start_date': start_date, 'end_date': end_date}
        
        if annual_return is not None:
            logger.verbose(f'Updating SQLite database {ProfileCache.update_return_transaction} with :ticker={ticker}, :start_date={start_date}, :end_date={end_date}')
            self.execute_transaction(transaction=ProfileCache.update_return_transaction, formatter=formatter)
        if annual_volatility is not None:
            logger.verbose(f'Updating SQLite database {ProfileCache.update_vol_transaction} with :ticker={ticker}, :start_date={start_date}, :end_date={end_date}')
            self.execute_transaction(transaction=ProfileCache.update_vol_transaction, formatter=formatter)        
        if sharpe_ratio is not None:
            logger.verbose(f'Updating SQLite database {ProfileCache.update_sharpe_transaction} with :ticker={ticker}, :start_date={start_date}, :end_date={end_date}')
            self.execute_transaction(transaction=ProfileCache.update_sharpe_transaction, formatter=formatter)
        if asset_beta is not None:
            logger.verbose(f'Updating SQLite database {ProfileCache.update_beta_transaction} with :ticker={ticker}, :start_date={start_date}, :end_date={end_date}')
            self.execute_transaction(transaction=ProfileCache.update_beta_transaction, formatter=formatter)
        if equity_cost is not None:
            logger.verbose(f'Updating SQLite database {ProfileCache.update_return_transaction} with :ticker={ticker}, :start_date={start_date}, :end_date={end_date}')
            self.execute_transaction(transaction=ProfileCache.update_equity_tranasction, formatter=formatter)

    def filter_profile_cache(self, ticker, start_date, end_date):
        formatter = { 'ticker': ticker, 'start_date': start_date, 'end_date': end_date}

        result = self.execute_query(query=ProfileCache.profile_query, formatter=formatter)

        if len(result)>0:
            return self.to_dict(result)
        else: 
            return None