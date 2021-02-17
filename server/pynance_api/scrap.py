# Python Imports
import os, datetime

import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

# Server Imports
from data.models import EquityMarket, CryptoMarket, EquityTicker, CryptoTicker, Economy, StatSymbol
from core import settings

# Application Imports
import app.services as services
import app.settings as app_settings
import app.files as files

# Utility Imports
import util.helper as helper
import util.outputter as outputter

logger = outputter.Logger("server.pynance_api.scrap", settings.LOG_LEVEL)

# TODO: register this function as a job in the Redis queue.
#       Run every day.
# Must be done after /static/ is initialized! 
def scrap_prices(asset_type):
    today = datetime.date.today()
    symbols = list(files.get_static_data(asset_type))

    for symbol in symbols:

        if asset_type == app_settings.ASSET_EQUITY:
            new_ticker_entry = EquityTicker.objects.get_or_create(ticker=symbol)
        elif asset_type == app_settings.ASSET_CRYPTO:
            new_ticker_entry = CryptoTicker.objects.get_or_create(ticker=symbol)

        if new_ticker_entry[1] and asset_type == app_settings.ASSET_EQUITY:
            logger.debug(f'Saved new {symbol} to EquityTicker table in database')
        elif new_ticker_entry[1] and asset_type == app_settings.ASSET_CRYPTO:
            logger.debug(f'Saved new {symbol} to CryptoTicker table in database')
        elif not new_ticker_entry[1] and asset_type == app_settings.ASSET_EQUITY:
            logger.debug(f'{symbol} already exists in EquityTicker table')
        else:
            logger.debug(f'{symbol} already exists in CryptoTicker table')

        if new_ticker_entry[1]:
            logger.debug(f'Querying service for entire price history for {symbol}.')
            price_history = services.query_service_for_daily_price_history(symbol, full=True, asset_type=asset_type)
            exists = False

        else:
            logger.debug(f'Determining if saved {symbol} price history is missing dates')
            exists = True        
            if asset_type == app_settings.ASSET_EQUITY:
                last_date = EquityMarket.objects.filter(ticker=symbol).order_by('-date')[:1][0].date

                missing_dates = (today - last_date).days
                if missing_dates > 0:
                    logger.debug(f'{symbol} saved price history missing dates.')
                    next_date = helper.get_next_business_date(last_date + datetime.timedelta(days=1))
                    logger.debug(f'Querying service for {symbol} price history from {next_date} to {today}.')
                    price_history = services.query_service_for_daily_price_history(ticker=symbol, 
                                                                                    start_date=next_date)
                                                                                
                else:
                    price_history = None

            elif asset_type == app_settings.ASSET_CRYPTO:
                last_date = CryptoMarket.objects.filter(ticker=symbol).order_by('-date')[:1][0].date
                
                missing_dates = (today-last_date).days
                if missing_dates > 0:
                    logger.debug(f'{symbol} saved price history missing dates')
                    next_date = helper.get_next_business_date(last_date + datetime.timedelta(days=1))
                    logger.debug(f'Querying service for {symbol} price from {next_date} to {today}')
                    price_history = services.query_service_for_daily_price_history(ticker=symbol,
                                                                                    start_date=next_date)
                else:
                    price_history = None

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
                    logger.verbose(f'Saving {symbol} (opening, closing) price of ({todays_open_price}, {todays_close_price}) on {date} to EquityMarket table in database.')
                elif new_market_entry[1] and asset_type == app_settings.ASSET_CRYPTO:
                    logger.verbose(f'Saving {symbol} (opening, closing) price of ({todays_open_price}, {todays_close_price}) on {date} to CryptoMarket table in database.')
                elif not new_market_entry[1] and asset_type == app_settings.ASSET_EQUITY:
                    logger.verbose(f'Closing and openiong prices for {symbol} on {date} already exist in EquityMarket table')
                else: 
                    logger.verbose(f'Closing and openiong prices for {symbol} on {date} already exist in CryptoMarket table')

        else: 
            if exists:
                logger.debug(f'{symbol} price history up to date.')
            else:
                logger.debug(f'{symbol} price history not found.')

# TODO: register this function as a job in the Redis queue.
#       Run every day.
def scrap_stats(stat_type):
    today = datetime.date.today()
    symbols = list(files.get_static_data(stat_type))

    for symbol in symbols:
        new_symbol_entry = StatSymbol.objects.get_or_create(symbol=symbol)

        if new_symbol_entry[1]:
            logger.debug(f'Saved {symbol} to StatSymbol table in database.')
            exists=False

            logger.debug(f'Querying service for {symbol} statistic history.')
            stat_history = services.query_service_for_daily_stats_history(statistic=symbol, full=True)

        else:
            logger.debug(f'{symbol} already exists in StatSymbol table in database.')
            logger.debug(f'Determining if saved {symbol} statistic history is missing dates')
            exists = True
            
            last_date = Economy.objects.filter(statistic=symbol).order_by('-date')[:1][0].date
            missing_dates = (today - last_date).days

            if missing_dates > 0:
                logger.debug(f'{symbol} saved price history missing dates.')
                next_date = helper.get_next_business_date(last_date + datetime.timedelta(days=1))
                
                logger.debug(f'Querying service for {symbol} statistic history from {next_date} to {today}.')
                stat_history = services.query_service_for_daily_price_history(ticker=symbol, 
                                                                                start_date=next_date)
            else:
                stat_history = None
        
        if stat_history:
            for date in stat_history:
                todays_date = helper.parse_date_string(date)
                value = stat_history[date]
                new_stat_entry = Economy.objects.get_or_create(statistic=new_symbol_entry[0], date = todays_date, value=value)

                if new_stat_entry[1]:
                    logger.verbose(f'Saving {symbol} value of {value} on {todays_date} to Economy table in database.')
                else:
                    logger.verbose(f'Value of {symbol} on {todays_date} already exists within Economy table in database.')
        else:
            if exists:
                logger.debug(f'{symbol} statistic history up to date.')
            else:
                logger.debug(f'{symbol} statistic history not found.')

# TODO: register this function as a job in the Redis queue.
#       Run every day.
def scrap_dividends():
    today = datetime.date.today()
    symbols = list(files.get_static_data(app_settings.ASSET_EQUITY))

    # TODO: scrap IEX dividend histories
    pass

# TODO: Parse and save any prices in the cache.
# TODO: integrate Redis and register this function as a job in the queue.
#       Run every hour.
def scrap_from_cache():
    pass

# TODO: query database and search for missing dates.
# TODO: call helper.business_dates_between('1950-01-01', today) and 
#       query the database to make sure all dates have valid data.
def search_for_missing_dates():
    pass

if __name__ == "__main__": 
    # scrap_prices(asset_type=app_settings.ASSET_EQUITY)
    # scrap_prices(asset_type=app_settings.ASSET_CRYPTO)
    scrap_stats(stat_type=app_settings.STAT_ECON)
    # scrap_dividends()