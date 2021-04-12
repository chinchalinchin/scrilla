from decimal import Decimal

import api.parser as parser
from core import settings
from data.models import EquityMarket, CryptoMarket, EquityTicker, CryptoTicker, \
                        EquityProfileCache, EquityCorrelationCache, Dividends, Economy, StatSymbol

import util.helper as helper
import util.outputter as outputter

import app.markets as markets
import app.settings as app_settings
import app.services as services
import app.statistics as statistics

logger = outputter.Logger("server.pynance_api.data.cache", settings.LOG_LEVEL)

# Save equity cache to market
# NOTE: The EquityProfileCache object is created when the cache is initially
#        checked for the result.
def save_profile_to_cache(profile):
    ticker = EquityTicker.objects.get(ticker=profile['ticker'])
    result = EquityProfileCache.objects.get(ticker=ticker, date=helper.get_today())

    logger.info(f'Saving {ticker.ticker} profile to database cache')

    result.annual_return = Decimal(profile['annual_return'])
    result.annual_volatility = Decimal(profile['annual_volatility'])
    result.sharpe_ratio = Decimal(profile['sharpe_ratio'])
    result.asset_beta = Decimal(profile['asset_beta'])

    result.save()

# TODO: allow for correlations between asset_types of tickers.
def save_correlation_to_cache(correlation, this_ticker_1, this_ticker_2):
    ticker_1 = EquityTicker.objects.get(ticker=this_ticker_1)
    ticker_2 = EquityTicker.objects.get(ticker=this_ticker_2)

    correl_cache_1 = EquityCorrelationCache.objects.get_or_create(ticker_1=ticker_1, ticker_2=ticker_2, date=helper.get_today())
    correl_cache_2 = EquityCorrelationCache.objects.get_or_create(ticker_1=ticker_2, ticker_2=ticker_1, date=helper.get_today())

    correl_cache_1.correlation = correlation
    correl_cache_2.correlation = correlation

    correl_cache_1.save()
    correl_cache_2.save()
    
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
        logger.info(f'No database cache found for {ticker[0].ticker} on {today}')

        logger.info('Determining if result can be built recursively...')
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
        
        logger.info(f'Database cache found for {ticker[0].ticker} profile.')
        profile = {}
        profile['ticker'] = ticker[0].ticker
        profile['annual_return'] = result[0].annual_return
        profile['annual_volatility'] = result[0].annual_volatility
        profile['sharpe_ratio'] = result[0].sharpe_ratio
        profile['asset_beta'] = result[0].asset_beta
        return profile

def check_cache_for_correlation(this_ticker_1, this_ticker_2):
    ticker_1 = EquityTicker.objects.get(ticker=this_ticker_1)
    ticker_2 = EquityTicker.objects.get(ticker=this_ticker_2)

    correl_cache_1 = EquityCorrelationCache.objects.get_or_create(ticker_1=ticker_1, ticker_2=ticker_2, date=helper.get_today())
    correl_cache_2 = EquityCorrelationCache.objects.get_or_create(ticker_1=ticker_2, ticker_2=ticker_1, date=helper.get_today())