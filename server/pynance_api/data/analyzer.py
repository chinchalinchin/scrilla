from decimal import Decimal
from core import settings
from data.models import EquityMarket, CryptoMarket, EquityTicker, CryptoTicker, \
                        EquityProfileCache, Dividends, Economy, StatSymbol

import util.helper as helper
import util.outputter as outputter

import app.markets as markets
import app.settings as app_settings
import app.services as services

logger = outputter.Logger("server.pynance_api.api.anaylzer", settings.LOG_LEVEL)

# Save equity cache to market
# NOTE: The EquityProfileCache object is created when the cache is initially
#        checked for the result.
def save_profile_to_cache(profile):
    ticker = EquityTicker.objects.get(ticker=profile['ticker'])
    result = EquityProfileCache.objects.get(ticker=ticker, date=helper.get_today())

    logger.info(f'Saving {ticker.ticker} profile to cache')

    result.annual_return = Decimal(profile['annual_return'])
    result.annual_volatility = Decimal(profile['annual_volatility'])
    result.sharpe_ratio = Decimal(profile['sharpe_ratio'])
    result.asset_beta = Decimal(profile['asset_beta'])

    result.save()
    
# If no start and end date are provided, since the default time period is 100
#   prices, stash equity profile statistics for quick retrieval instead of 
#   calculating from scratch each time the profile is requested for the default
#   time period. 
# NOTE: This creates the EquityProfileCache object if it does not exist. So,
#           when saving, the QuerySet should be filtered and ordered by date.
# TODO: must be careful to verify when testing this that it actually calculates the profile
#        recursively correctly.
def check_cache_for_profile(ticker):
    ticker = EquityTicker.objects.get_or_create(ticker=ticker)
    today = helper.get_today()
    result = EquityProfileCache.objects.get_or_create(ticker=ticker[0], date=today)

    if result[1]:
        logger.info(f'No cache found for {ticker[0].ticker}')
        # check for any dates and recursively build profiles
        # cache = EquityProfileCache.objects.filter(date__lte=today).order_by('-date')
        # if cache.count() > 0:
            #  last_dated_profile = cache[0]
            #  date = last_dated_profile.date
            #  dates_missing = helper.business_dates_between(start_date=today, end_date=date)
            #  missing_prices = EquityMarket.objects.filter(ticker=ticker[0], date__lte=today, date__gte=date).order_by('-date')
            #  trading_period = markets.get_trading_period(settings.EQUITY_ASSET_TYPE)
            #   for this_date in dates_missing:
            #       missing_price = missing_prices.get(date=this_date)
            #       missing_price_less_one = EquityMarket.objects.get(ticker=ticker[0], 
            #                                                           date=helper.decrement_by_business_days(date=this_date, days=1))
            #       lost_date = helper.decrement_by_business_days(date=this_date, business_days=settings.DEFAULT_ANALYSIS_PERIOD)
            #       lost_price = EquityMarket.objects.get(ticker=ticker[0], date=lost_date)
            #       lost_price_less_one = EquityMarkets.objects.get(ticker=ticker[0],
            #                                                           date=helper.decrement_by_business_days(date=this_date, days=1))
        return False
    else:
        if result[0].annual_return is None:
            return False
        if result[0].annual_volatility is None:
            return False
        if result[0].sharpe_ratio is None:
            return False
        if result[0].asset_beta is None:
            return False
        
        logger.info(f'Cache found for {ticker[0].ticker}')
        profile = {}
        profile['ticker'] = ticker[0].ticker
        profile['annual_return'] = result[0].annual_return
        profile['annual_volatility'] = result[0].annual_volatility
        profile['sharpe_ratio'] = result[0].sharpe_ratio
        profile['asset_beta'] = result[0].asset_beta
        return profile

def market_queryset_gap_analysis(symbol, start_date=None, end_date=None):
    logger.info(f'Searching for gaps in {symbol} Market queryset.')

    asset_type = markets.get_asset_type(symbol=symbol)

    if asset_type == app_settings.ASSET_EQUITY:
        if end_date is None: 
            end_date = helper.get_previous_business_date(date=helper.get_today())
        if start_date is None:
            start_date = helper.decrement_date_by_business_days(start_date=end_date, 
                                                                business_days=app_settings.DEFAULT_ANALYSIS_PERIOD)
        
        ticker = EquityTicker.objects.get_or_create(ticker=symbol)
        date_range = helper.business_dates_between(start_date=start_date, end_date=end_date)
        queryset = EquityMarket.objects.filter(ticker=ticker[0], date__gt=start_date, date__lte=end_date).order_by('-date')
        
    elif asset_type == app_settings.ASSET_CRYPTO:
        if end_date is None:
            end_date = helper.decrement_date_by_business_days(start_date=helper.get_today(),
                                                                business_days=1)
        if start_date is None:
            start_date = helper.decrement_date_by_days(start_date=end_date, 
                                                        days=app_settings.DEFAULT_ANALYSIS_PERIOD)
        
        ticker = CryptoTicker.objects.get_or_create(ticker=symbol)
        date_range = helper.dates_between(start_date=start_date, end_date=end_date)
        queryset = CryptoMarket.objects.filer(ticker=ticker[0], date__gt=start_date, date__lte=end_date).order_by('-date')
    
    gaps = len(date_range) - queryset.count()  + 1
    if gaps != 0: 
            logger.info(f'{len(date_range) - queryset.count() + 1} gaps detected.')
            price_history = services.get_daily_price_history(ticker=symbol, start_date=start_date, 
                                                                            end_date=end_date)
            count = 0
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
                    count += 1
                    logger.debug(f'{count} gaps filled.')
                else:
                    logger.debug(f'No gap detected on {date} for {symbol}.')
                
                if count == gaps:
                    logger.debug(f'All gaps filled, breaking loop.')
                    break

def dividend_queryset_gap_analysis(symbol):
    logger.info(f'Searching for gaps in {symbol} Dividend queryset.')

    ticker = EquityTicker.objects.get_or_create(ticker=symbol)
    queryset = Dividends.objects.filter(ticker=ticker[0])

    if queryset.count() == 0:
        logger.info('Gaps detected.')
        dividends = services.get_dividend_history(ticker=symbol)
        for date in dividends:
            logger.debug(f'Checking {date} for gaps.')
            entry =Dividends.objects.get_or_create(ticker=ticker[0], date=date, amount=dividends[date])
            if entry[1]:
                logger.debug(f'Gap filled on {date} for {symbol} with amount {dividends[date]}.')
            else:
                logger.debug(f'No gap detected on {date} for {symbol}.')

def economy_queryset_gap_analysis(symbol, start_date=None, end_date=None):
    # TODO:
    pass