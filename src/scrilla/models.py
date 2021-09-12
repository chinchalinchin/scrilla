import sqlite3

from scrilla import settings

# TODO: before hooking this into the application, i will need a method that returns a dict formatted in the way the application expects. before doing so, test out current cache methods to see if they still work after refactor (fingers crossed) and then test this class in isolation, i.e. build the latest wheel, install it (so settings import is accurate) and then start a python shell and see if class behaves as expected.

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

    def query_database(self, query, formatter=None):
        con = sqlite3.connect(settings.CACHE_SQLITE_FILE)
        con.row_factory = sqlite3.Row
        executor = con.cursor()
        if formatter is not None:
            return executor.execute(query, formatter).fetchall()
        return executor.execute(query).fetchall()

class PriceCache(Cache):

    create_table_transaction="CREATE TABLE IF NOT EXISTS prices (ticker text, date text, open real, close real)"
    insert_row_query="INSERT INTO prices VALUES (:ticker, :date, :open, :close)"
    date_lte_query="SELECT * from (:date_lte_subquery) WHERE date <= date(:end_date)"
    date_gte_query="SELECT * from (:date_gte_subquery) WHERE date >= date(:start_date)"
    ticker_query="SELECT date, open, close from prices WHERE ticker = :ticker"

    def __init__(self):
        self.execute_transaction((PriceCache.create_table_transaction, None))

    @staticmethod
    def to_dict(query_results):
        return { result[0]: { 'open': result[1], 'close': result[2] } for result in query_results }

    def save_row(self, ticker, date, open, close):
        formatter = { ticker: 'ticker', date: 'date', open: 'open', close: 'close'}
        self.execute_transaction((PriceCache.insert_row_query, formatter))

    def filter_price_cache(self, ticker, start_date=None, end_date=None):
        args = { "ticker" : ticker }

        if end_date is not None and start_date is not None:
            query = PriceCache.date_gte_query
            args['start_date'] = start_date
            args['end_date'] = end_date
            args['date_gte_subquery'] = PriceCache.date_lte_query
            args['date_lte_subquery'] = PriceCache.ticker_query

        elif end_date is not None and start_date is None:
            query = PriceCache.date_gte_query
            args['end_date'] = end_date
            args['date_gte_subquery'] = PriceCache.ticker_query

        elif end_date is None and start_date is not None:
            query = PriceCache.date_lte_query
            args['start_date'] = start_date
            args['date_lte_subquery'] = PriceCache.ticker_query

        else:
            query = PriceCache.ticker_query

        results = self.query_database(query=query, formatter=args)

        return self.to_dict(results)