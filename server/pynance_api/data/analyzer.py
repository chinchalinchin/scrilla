from core import settings
from data.models import EquityMarket, CryptoMarket, EquityTicker, CryptoTicker, Dividends, Economy, StatSymbol

import util.helper as helper
import util.outputter as outputter

import app.markets as markets
import app.settings as app_settings
import app.services as services

logger = outputter.Logger("server.pynance_api.api.anaylzer", settings.LOG_LEVEL)


def market_queryset_gap_analysis(symbol, start_date=None, end_date=None):
    logger.info('Searching for gaps in Market querysets.')

    asset_type = markets.get_asset_type(symbol=symbol)

    if asset_type == app_settings.ASSET_EQUITY:
        if end_date is None: 
            end_date = helper.get_previous_business_date(date=helper.get_today())
        if start_date is None:
            start_date = helper.decrement_date_by_business_days(start_date=end_date, 
                                                                business_days=(app_settings.DEFAULT_ANALYSIS_PERIOD-1))
        
        print('end_date', end_date)
        print('start_date', start_date)
        ticker = EquityTicker.objects.get_or_create(ticker=symbol)
        date_range = helper.business_dates_between(start_date=start_date, end_date=end_date)
        queryset = EquityMarket.objects.filter(ticker=ticker[0], date__gt=start_date, date__lte=end_date)
        
    elif asset_type == app_settings.ASSET_CRYPTO:
        if end_date is None:
            end_date = helper.get_today()
        if start_date is None:
            start_date = helper.decrement_date_by_days(start_date=end_date, 
                                                        days=(app_settings.DEFAULT_ANALYSIS_PERIOD-1))
        
        ticker = CryptoTicker.objects.get_or_create(ticker=symbol)
        date_range = helper.dates_between(start_date=start_date, end_date=end_date)
        queryset = CryptoMarket.objects.filer(ticker=ticker[0], date__gt=start_date, date__lte=end_date)
    
    print('count', queryset.count())
    print('date_range', len(date_range))
    print('date_first', date_range[0])
    print('date_last', date_range[-1])
    if queryset.count() != len(date_range): 
            logger.info('Gaps detected.')
            price_history = services.query_service_for_daily_price_history(ticker=symbol, start_date=start_date, 
                                                                            end_date=end_date)
            for date in price_history:
                logger.debug(f'Checking {date} for gaps.')
                close_price = services.parse_price_from_date(prices=price_history, date=date, asset_type=asset_type, 
                                                                which_price=services.CLOSE_PRICE)
                open_price = services.parse_price_from_date(prices=price_history, date=date, asset_type=asset_type, 
                                                                which_price=services.OPEN_PRICE)
                if asset_type == app_settings.ASSET_EQUITY:
                    entry = EquityMarket.objects.get_or_create(ticker=ticker[0], date=date, open_price=open_price, close_price=close_price)
                elif asset_type == app_settings.ASSET_CRYPTO:
                    entry = CryptoMarket.objects.get_or_create(ticker=ticker[0], date=date, open_price=open_price, close_price=close_price)

                if entry[1]:
                    logger.debug(f'Gap filled on {date} for {symbol} with price open={open_price} - close={close_price}.')
                else:
                    logger.debug(f'No gap detected on {date} for {symbol}.')