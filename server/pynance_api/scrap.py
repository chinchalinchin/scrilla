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
def scrap():
    today = datetime.date.today()
    asset_type = app_settings.ASSET_EQUITY
    symbols = list(services.get_static_data(asset_type))

    for symbol in symbols:
        new_ticker_entry = EquityTicker.objects.get_or_create(ticker=symbol)
        if new_ticker_entry[1]:
            output.debug(f'Saving {symbol} to EquityTicker table in database')

        output.debug(f'Retrieving price history for {symbol}...')
        price_history = services.query_service_for_daily_price_history(symbol, full=True)
        
        for date in price_history:
            todays_price = services.parse_price_from_date(prices=price_history, date=date, asset_type=asset_type)
            todays_date = helper.parse_date_string(date)
                
            new_market_entry = EquityMarket.objects.get_or_create(ticker=new_ticker_entry[0], date=date, closing_price=todays_price)
            if new_market_entry[1]:
                output.debug(f'Saving {symbol} closing price of {todays_price} on {date} to EquityMarket table in database.')

    

if __name__ == "__main__": 
    scrap()