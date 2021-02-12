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

output = logger.Logger("server.pynance_api.scrap")

# Must be done after /static/ is initialized!
def scrap():
    today = datetime.date.today()
    asset_type = app_settings.ASSET_EQUITY
    symbols = list(services.get_static_data(app_settings.ASSET_EQUITY))


    for symbol in symbols:
        logger.debug(f'Saving {symbol} to EquityTicker table in database')
        new_ticker_entry = EquityTicker.objects.get_or_create(ticker=symbol)

        logger.debug(f'Retrieving price history for {symbol}...')
        price_history = services.get_daily_price_history(symbol, full=True)
        
        for date in price_history:
            todays_price = services.parse_price_from_date(price_history=price_history, date=date, asset_type=asset_type)
            todays_date = helper.parse_date_string(date)
                
            logger.debug(f'Saving {symbol} closing price of {todays_price} on {date} to EquityMarket table in database.')
            new_market_entry = EquityMarket.objects.get_or_create(ticker=new_ticker_entry, date=date, closing_price=todays_price)
    

if __name__ == "__main__": 
    scrap()