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
def scrap_prices(asset_type):
    today = datetime.date.today()

    symbols = list(services.get_static_data(asset_type))

    for symbol in symbols:

        if asset_type == app_settings.ASSET_EQUITY:
            new_ticker_entry = EquityTicker.objects.get_or_create(ticker=symbol)
        elif asset_type == app_settings.ASSET_CRYPTO:
            new_ticker_entry = CryptoTicker.objects.get_or_create(ticker=symbol)

        if new_ticker_entry[1] and asset_type == app_settings.ASSET_EQUITY:
            output.debug(f'Saving {symbol} to EquityTicker table in database')
        elif new_ticker_entry[1] and asset_type == app_settings.ASSET_CRYPTO:
            output.debug(f'Saving {symbol} to CryptoTicker table in database')
        elif not new_ticker_entry[1] and asset_type == app_settings.ASSET_EQUITY:
            output.debug(f'{symbol} already exists in EquityTicker table')
        else:
            output.debug(f'{symbol} already exists in CryptoTicker table')

        output.debug(f'Retrieving price history for {symbol}...')

        if new_ticker_entry[1]:
            price_history = services.query_service_for_daily_price_history(symbol, full=True, asset_type=asset_type)
        else:
            if asset_type == app_settings.ASSET_EQUITY:
                # TODO: determine if last date in table is today
                #       if not, query missing dates
                pass
            elif asset_type == app_settings.ASSET_CRYPTO:
                # TODO: determine if last date in table is today
                #       if not, query missing dates
                pass

        if price_history:
            for date in price_history:
                todays_close_price = services.parse_price_from_date(prices=price_history, date=date, 
                                                                    asset_type=asset_type, which_price=services.CLOSE_PRICE)
                todays_open_price = services.parse_price_from_date(prices=price_history, date=date, 
                                                                    asset_type=asset_type, which_price=services.OPEN_PRICE)
                todays_date = helper.parse_date_string(date)
                
                if asset_type == app_settings.ASSET_EQUITY:
                    new_market_entry = EquityMarket.objects.get_or_create(ticker=new_ticker_entry[0], date=todays_date, 
                                                                            close_price=todays_close_price, open_price=todays_open_price)
                elif asset_type == app_settings.ASSET_CRYPTO:
                    new_market_entry = CryptoMarket.objects.get_or_create(ticker=new_ticker_entry[0], date=todays_date,
                                                                            close_price=todays_open_price, open_price=todays_open_price)

                if new_market_entry[1] and asset_type == app_settings.ASSET_EQUITY:
                    output.verbose(f'Saving {symbol} (opening, closing) price of ({todays_open_price}, {todays_close_price}) on {date} to EquityMarket table in database.')
                elif new_market_entry[1] and asset_type == app_settings.ASSET_CRYPTO:
                    output.verbose(f'Saving {symbol} (opening, closing) price of ({todays_open_price}, {todays_close_price}) on {date} to CryptoMarket table in database.')
                elif not new_market_entry[1] and asset_type == app_settings.ASSET_EQUITY:
                    output.verbose(f'Closing and openiong prices for {symbol} on {date} already exist in EquityMarket table')
                else: 
                    output.verbose(f'Closing and openiong prices for {symbol} on {date} already exist in CryptoMarket table')
        else: 
            output.debug(f'Price history not found for {symbol}.')


def scrap_stats():
    today = datetime.date.today()

    stat_type = app_settings.STAT_ECON
    symbols = list(services.get_static_data(stat_type))

    pass

if __name__ == "__main__": 
    scrap_prices(asset_type=app_settings.ASSET_EQUITY)
    scrap_prices(asset_type=app_settings.ASSET_CRYPTO)
    scrap_stats()