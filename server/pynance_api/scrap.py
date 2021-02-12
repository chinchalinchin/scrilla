# Python Imports
import os, datetime

import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

# Server Imports
from data.models import EquityMarket, CryptoMarket, EquityTicker, CryptoTicker, Economy
from core import settings

# Application Imports
import app.services as services
import app.settings as app_settings

# Utility Imports
import util.helper as helper
import util.logger as logger

output = logger.Logger("server.pynance_api.scrap", settings.LOG_LEVEL)

# Must be done after /static/ is initialized!
# TODO: query equitymarket by ticker and sort by date. Find delta between
#       today and last price and only query service for missing dates.
def scrap_equities():
    today = datetime.date.today()

    asset_type = app_settings.ASSET_EQUITY
    symbols = list(services.get_static_data(asset_type))

    for symbol in symbols:

        new_ticker_entry = EquityTicker.objects.get_or_create(ticker=symbol)

        if new_ticker_entry[1]:
            output.debug(f'Saving {symbol} to EquityTicker table in database')
        else:
            output.debug(f'{symbol} already exists in EquityTicker table')

        output.debug(f'Retrieving price history for {symbol}...')
        price_history = services.query_service_for_daily_price_history(symbol, full=True)

        if price_history:
            for date in price_history:
                todays_close_price = services.parse_price_from_date(prices=price_history, date=date, 
                                                                    asset_type=asset_type)
                todays_open_price = services.parse_price_from_date(prices=price_history, date=date, 
                                                                    asset_type=asset_type,which_price=services.OPEN_PRICE)
                todays_date = helper.parse_date_string(date)
                
                new_market_entry = EquityMarket.objects.get_or_create(ticker=new_ticker_entry[0], date=todays_date, 
                                                                        close_price=todays_close_price, open_price=todays_open_price)
                if new_market_entry[1]:
                    output.verbose(f'Saving {symbol} (opening, closing) price of ({todays_open_price}, {todays_close_price}) on {date} to EquityMarket table in database.')
                else: 
                    output.verbose(f'Closing and openiong prices for {symbol} on {date} already exist in EquityMarket table')
        else: 
            output.debug(f'Price history not found for {symbol}.')

    
def scrap_crypto():
    pass

def scrap_stats():
    pass

if __name__ == "__main__": 
    scrap_equities()
    scrap_crypto()
    scrap_stats()