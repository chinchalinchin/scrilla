# Python Imports
import datetime

# Server Imports
from data.models import Market, Crypto, Economy
from core import settings
from debug import DebugLogger as logger

# Application Imports
import app.services as services
import util.helper as helper

output = logger.Logger("server.pynance_api.data")

# Must be done after /static/ is initialized!
def scrap_data():
    today = datetime.date.today()
    asset_type = settings.ASSET_EQUITY
    symbols = list(services.get_static_data(settings.ASSET_EQUITY))


    for symbol in symbols:
        logger.info('Retrieving price history for %s', symbol)
        price_history = services.get_daily_price_history(symbol, full=True)
        
        for date in price_history:
            todays_price = services.parse_price_from_date(price_history=price_history, date=date, asset_type=asset_type)
            todays_date = helper.parse_date_string(date)
                
            logger.info('Saving %s closing price of %s on %s to database...', symbol, todays_price, date)
            new_market_entry = Market.objects.get_or_create(ticker=symbol, date=date, closing_price=todays_price)
    

if __name__ == "__main__": 
    scrap_data()