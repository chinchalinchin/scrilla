from decimal import Decimal

import api.parser as parser
from core import settings
from data import models, cache

import util.helper as helper
import util.outputter as outputter

import app.markets as markets
import app.settings as app_settings
import app.services as services
import app.statistics as statistics

logger = outputter.Logger("server.pynance_api.data.anaylzer", settings.LOG_LEVEL)

def market_queryset_gap_analysis(symbol, start_date=None, end_date=None):
    logger.info(f'Searching for gaps in {symbol} Market queryset.')

    asset_type = markets.get_asset_type(symbol=symbol)

    if asset_type == app_settings.ASSET_EQUITY:
        if end_date is None: 
            end_date = helper.get_previous_business_date(date=helper.get_today())
        if start_date is None:
            start_date = helper.decrement_date_by_business_days(start_date=end_date, 
                                                                business_days=app_settings.DEFAULT_ANALYSIS_PERIOD)
        # TODO: valid order of dates if not None

        ticker = models.EquityTicker.objects.get_or_create(ticker=symbol)
        date_range = helper.business_dates_between(start_date=start_date, end_date=end_date)
        queryset = models.EquityMarket.objects.filter(ticker=ticker[0], date__gte=start_date, date__lte=end_date).order_by('-date')
        
    elif asset_type == app_settings.ASSET_CRYPTO:
        if end_date is None:
            end_date = helper.decrement_date_by_days(start_date=helper.get_today(),
                                                                days=1)
        if start_date is None:
            start_date = helper.decrement_date_by_days(start_date=end_date, 
                                                        days=app_settings.DEFAULT_ANALYSIS_PERIOD)
        # TODO: valid order of dates if not None

        ticker = models.CryptoTicker.objects.get_or_create(ticker=symbol)
        date_range = helper.dates_between(start_date=start_date, end_date=end_date)
        queryset = models.CryptoMarket.objects.filer(ticker=ticker[0], date__gte=start_date, date__lte=end_date).order_by('-date')

    gaps = len(date_range) - queryset.count()
    if gaps != 0: 
        logger.info(f'{gaps} gaps detected.')
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
                entry = models.EquityMarket.objects.get_or_create(ticker=ticker[0], date=date, open_price=open_price, close_price=close_price)
            elif asset_type == app_settings.ASSET_CRYPTO:
                entry = models.CryptoMarket.objects.get_or_create(ticker=ticker[0], date=date, open_price=open_price, close_price=close_price)

            if entry[1]:
                logger.debug(f'Gap filled on {date} for {symbol} with price open={open_price} - close={close_price}.')
                count += 1
                logger.debug(f'{count} gaps filled.')
            else:
                logger.debug(f'No gap detected on {date} for {symbol}.')
            
            if count == gaps:
                logger.debug(f'All gaps filled, breaking loop.')
                break

# returns market_profile
def market_proxy_gap_analysis(start_date=None, end_date=None):
    market_queryset_gap_analysis(symbol=app_settings.MARKET_PROXY, start_date=start_date, end_date=end_date)

    market_profile = cache.check_for_profile(ticker=app_settings.MARKET_PROXY, start_date=start_date,
                                                    end_date=end_date)
    if not market_profile:
        market_prices = parser.parse_args_into_market_queryset(ticker=app_settings.MARKET_PROXY,
                                                                parsed_args={ 'start_date': start_date, 'end_date': end_date})
        market_profile = statistics.calculate_risk_return(ticker=app_settings.MARKET_PROXY, 
                                                            sample_prices=market_prices)
        market_profile['ticker'], market_profile['asset_beta']=app_settings.MARKET_PROXY, 1
        market_profile['sharpe_ratio'] = markets.sharpe_ratio(ticker=app_settings.MARKET_PROXY, 
                                                                ticker_profile=market_profile,
                                                                start_date=start_date,
                                                                end_date=end_date)
        cache.save_profile(profile=market_profile)
    else:
        for stat in market_profile:
            if stat != 'ticker':
                market_profile[stat] = float(market_profile[stat])
    return market_profile

# Returns latest dividend amount for provided symbol
def dividend_queryset_gap_analysis(symbol):
    logger.info(f'Searching for gaps in {symbol} Dividend queryset.')

    ticker = models.EquityTicker.objects.get_or_create(ticker=symbol)
    queryset = models.Dividends.objects.filter(ticker=ticker[0])

    if queryset.count() == 0:
        logger.info('Gaps detected.')
        dividends = services.get_dividend_history(ticker=symbol)
        for date in dividends:
            logger.debug(f'Checking {date} for gaps.')
            entry = models.Dividends.objects.get_or_create(ticker=ticker[0], date=date, amount=dividends[date])
            if entry[1]:
                logger.debug(f'Gap filled on {date} for {symbol} with amount {dividends[date]}.')
            else:
                logger.debug(f'No gap detected on {date} for {symbol}.')
    return queryset.first().amount

# NOTE: Returns latest value of Economy model for the provided symbol.
# TODO: analyzes the date range for gaps when all I really need is the latest value of
#       the interest rate.
def economy_queryset_gap_analysis(symbol, start_date=None, end_date=None):
    logger.info(f'Searching for gaps in {symbol} Economy queryset.')

    if end_date is None: 
        end_date = helper.get_previous_business_date(date=helper.get_today())
    if start_date is None:
        start_date = helper.decrement_date_by_business_days(start_date=end_date, 
                                                            business_days=app_settings.DEFAULT_ANALYSIS_PERIOD)
    # TODO: valid order of dates if not None

    stat_symbol = models.StatSymbol.objects.get_or_create(symbol=symbol)
    date_range = helper.business_dates_between(start_date=start_date,end_date=end_date)
    queryset = models.Economy.objects.filter(statistic=stat_symbol[0],date__gte=start_date,date__lte=end_date).order_by('-date')

    gaps = len(date_range) - queryset.count()
    if gaps != 0: 
        logger.info(f'{gaps} gaps detected.')
        stat_history = services.get_daily_stats_history(statistic=stat_symbol[0], start_date=start_date,
                                                            end_date=end_date)
        count = 0
        for date in stat_history:
            logger.debug(f'Checking {date} for gaps.')
            value = stat_history[date]
            if stat_symbol[0].symbol in services.get_percent_stat_symbols():
                value = value / 100
            entry = models.Economy.objects.get_or_create(statistic=stat_symbol[0],date=date,value=value)
            if entry[1]:
                logger.debug(f'Gap filled on {date} for {stat_symbol[0]} with value={value}')
                count += 1
                logger.debug(f'{count} gaps filled.')
            else:
                logger.debug(f'No gap detected on {date} for {stat_symbol[0]}.')
            
            if count == gaps:
                logger.debug(f'All gaps filled, breaking loop.')
                break
    
    return queryset.first().value


def initialize_market_info(parsed_args):
    market_profile = market_proxy_gap_analysis(start_date=parsed_args['start_date'], 
                                                            end_date=parsed_args['end_date'])
    risk_free_rate = economy_queryset_gap_analysis(symbol=app_settings.RISK_FREE_RATE,
                                                        start_date=parsed_args['start_date'], 
                                                        end_date=parsed_args['end_date'])
    return market_profile, risk_free_rate
