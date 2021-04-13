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

def determine_date_range(start_date=None, end_date=None):
    if start_date is None and end_date is None:
        end_date = helper.get_today()
        start_date = helper.decrement_date_by_business_days(end_date, app_settings.DEFAULT_ANALYSIS_PERIOD)
    elif start_date is None:
        start_date = helper.decrement_date_by_business_days(end_date, app_settings.DEFAULT_ANALYSIS_PERIOD)
    elif end_date is None:
        end_date = helper.get_today()
    return start_date, end_date

# NOTE: The EquityProfileCache object is created when the cache is initially
#        checked for the result.
def save_profile(profile, start_date=None, end_date=None):
    ticker = EquityTicker.objects.get(ticker=profile['ticker'])
    
    start_date, end_date = determine_date_range(start_date=start_date, end_date=end_date)
        
    result = EquityProfileCache.objects.get(ticker=ticker, start_date=start_date, end_date=end_date)

    logger.debug(f'Saving {ticker.ticker} profile({start_date} to {end_date}) to database cache')

    result.annual_return = Decimal(profile['annual_return'])
    result.annual_volatility = Decimal(profile['annual_volatility'])
    result.sharpe_ratio = Decimal(profile['sharpe_ratio'])
    result.asset_beta = Decimal(profile['asset_beta'])

    result.save()

# TODO: allow for correlations between asset_types of tickers.
def save_correlation(correlation, this_ticker_1, this_ticker_2, start_date=None, end_date=None):
    ticker_1 = EquityTicker.objects.get(ticker=this_ticker_1)
    ticker_2 = EquityTicker.objects.get(ticker=this_ticker_2)

    start_date, end_date = determine_date_range(start_date=start_date, end_date=end_date)

    logger.debug(f'Saving {this_ticker_1}_{this_ticker_2} correlation to database cache')
    correl_cache_1 = EquityCorrelationCache.objects.get(ticker_1=ticker_1, 
                                                            ticker_2=ticker_2, 
                                                            start_date=start_date,
                                                            end_date=end_date)
    correl_cache_2 = EquityCorrelationCache.objects.get(ticker_1=ticker_2, 
                                                            ticker_2=ticker_1, 
                                                            start_date=start_date,
                                                            end_date=end_date)

    correl_cache_1.correlation = correlation['correlation']
    correl_cache_2.correlation = correlation['correlation']

    correl_cache_1.save()
    correl_cache_2.save()
    
# NOTE: This creates the EquityProfileCache object if it does not exist. So,
#           when saving, the QuerySet should be filtered and ordered by date.
# TODO: must be careful to verify when testing this that it actually calculates the profile
#        recursively correctly.
def check_for_profile(ticker, start_date=None, end_date=None):
    ticker = EquityTicker.objects.get_or_create(ticker=ticker)
    start_date, end_date = determine_date_range(start_date=start_date, end_date=end_date)
    result = EquityProfileCache.objects.get_or_create(ticker=ticker[0], 
                                                        start_date=start_date,
                                                        end_date=end_date)

    if result[1]:
        logger.info(f'No database cache found for {ticker[0].ticker} over {start_date} to {end_date}')

        if settings.RECURSION:
            logger.info('Determining if result can be built recursively...')
        ###########################
        # TODO: implement recursion
        ###########################

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
        return None
    else:
        if result[0].annual_return is None:
            return None
        if result[0].annual_volatility is None:
            return None
        if result[0].sharpe_ratio is None:
            return None
        if result[0].asset_beta is None:
            return None
        
        logger.info(f'Database cache found for {ticker[0].ticker} profile.')
        profile = {}
        profile['ticker'] = ticker[0].ticker
        profile['annual_return'] = result[0].annual_return
        profile['annual_volatility'] = result[0].annual_volatility
        profile['sharpe_ratio'] = result[0].sharpe_ratio
        profile['asset_beta'] = result[0].asset_beta
        return profile

def check_for_correlation(this_ticker_1, this_ticker_2, start_date=None, end_date=None):
    ticker_1 = EquityTicker.objects.get(ticker=this_ticker_1)
    ticker_2 = EquityTicker.objects.get(ticker=this_ticker_2)

    start_date, end_date = determine_date_range(start_date=start_date, end_date=end_date)

    correl_cache_1 = EquityCorrelationCache.objects.get_or_create(ticker_1=ticker_1, 
                                                                    ticker_2=ticker_2, 
                                                                    start_date=start_date,
                                                                    end_date=end_date)
    correl_cache_2 = EquityCorrelationCache.objects.get_or_create(ticker_1=ticker_2, 
                                                                    ticker_2=ticker_1, 
                                                                    start_date=start_date,
                                                                    end_date=end_date)

    if (correl_cache_1[1] and correl_cache_2):
        logger.info(f'No database cache found for {ticker_1}_{ticker_2} correlation.')

        if settings.RECURSION:
            logger.info(f'Determining if result can be recursively built...')
            ###########################
            # TODO: implement recursion
            ###########################
        return None
    elif (correl_cache_1[1] and not correl_cache_2[1]) or \
         (not correl_cache_1[1] and correl_cache_2[1]):
        if correl_cache_1[1]:
            if correl_cache_1[0].correlation:
                logger.debug('Cached correlation found in 1,2 mapping, passing to 2,1 mapping and returning.')
                correl_cache_1[0].correlation = correl_cache_2[0].correlation
                correl_cache_1[0].save()
                return correl_cache_1[0].correlation
            else:
                logger.debug('Correlation 1,2 exists, but has no value!')
                return None
        else:
            if correl_cache_2[0].correlation:
                logger.debug('Cached correlation found in 2,1 mapping, passing to 1,2 mapping and returning.')
                correl_cache_2[0].correlation = correl_cache_1[0].correlation
                correl_cache_2[0].save()
                return correl_cache_2[0].correlation
            else:
                logger.debug('Correlation 2,1 exists, but has no value!')
                return None
    else:
        if correl_cache_1[0].correlation == correl_cache_2[0].correlation:
            logger.debug('Cached correlations equal, returning result.')
            return correl_cache_1[0].correlation
        else:
            logger.debug('Cached correlations not equal, returning null.')
            return None