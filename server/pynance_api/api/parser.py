from decimal import Decimal
from core import settings
from data.models import EquityMarket, CryptoMarket, EquityTicker, CryptoTicker, EquityProfileCache,\
                         Dividends, Economy, StatSymbol

import app.util.helper as helper
import app.util.outputter as outputter

import app.analysis.markets as markets
import app.settings as app_settings

logger = outputter.Logger("server.pynance_api.api.parser", settings.LOG_LEVEL)

def verify_method(request, allowed_methods):
    if request.method not in allowed_methods: 
        return False
    return True

def log_secondary_args(parsed_args):
    # Determine if logging needs to be done, i.e. if any arguments are not None
    logging = False
    for arg in parsed_args.values():
        if arg is not None:
            logging = True
            break
    if not logging:
        return

    logger.debug('> Request Parameters')
    if parsed_args['start_date'] is not None:
        logger.debug(f'>> Start : {parsed_args["start_date"]}')

    if parsed_args['end_date'] is not None:
        logger.debug(f'>> End: {parsed_args["end_date"]}')
    
    if parsed_args['target_return'] is not None:
        logger.debug(f'>> Target: {parsed_args["target_return"]}')
    
    if parsed_args['sharpe_ratio'] is not None:
        logger.debug(f'>> Sharpe Ratio: {parsed_args["sharpe_ratio"]}')

    if parsed_args['investment'] is not None:
        logger.debug(f'>> Investment: {parsed_args["investment"]}')
    
    if parsed_args['discount_rate'] is not None:
        logger.debug(f'>> Discount RATE: {parsed_args["discount_rate"]}')

    if parsed_args['jpeg'] is not None:
        logger.debug(f'>> JPEG: {parsed_args["jpeg"]}')

def parse_secondary_args(request):
    if settings.REQUEST_PARAMS['start_date'] in request.GET:
        start_date = str(request.GET.get(settings.REQUEST_PARAMS['start_date']))
        start_date = helper.parse_date_string(start_date)
    else:
        start_date = None

    if settings.REQUEST_PARAMS['end_date'] in request.GET:
        end_date = str(request.GET.get(settings.REQUEST_PARAMS['end_date']))
        end_date = helper.parse_date_string(end_date)
    else:
        end_date = None

    if settings.REQUEST_PARAMS['target_return'] in request.GET:
        target_return = request.GET.get(settings.REQUEST_PARAMS['target_return'])
    else:
        target_return = None

    if settings.REQUEST_PARAMS['sharpe_ratio'] in request.GET:
        sharpe = str(request.GET.get(settings.REQUEST_PARAMS['sharpe_ratio']))
        sharpe = sharpe.lower() == 'true'
    else:
        sharpe = None

    if settings.REQUEST_PARAMS['jpeg'] in request.GET:
        jpeg = str(request.GET.get(settings.REQUEST_PARAMS['jpeg']))
        jpeg = jpeg.lower() == 'true'
    else:
        jpeg = None

    if settings.REQUEST_PARAMS['discount_rate'] in request.GET:
        discount = request.GET.get(settings.REQUEST_PARAMS['discount_rate'])
    else:
        discount = None

    if settings.REQUEST_PARAMS['investment'] in request.GET:
        investment = request.GET.get(settings.REQUEST_PARAMS['investment'])
    else:
        investment = None

    parsed_args = {
        'start_date': start_date,
        'end_date': end_date,
        'target_return': target_return,
        'investment': investment,
        'sharpe_ratio': sharpe,
        'discount_rate': discount,
        'jpeg': jpeg,
    }
    log_secondary_args(parsed_args)

    return parsed_args

def parse_tickers(request):
    if settings.REQUEST_PARAMS['tickers'] in request.GET:
        tickers = request.GET.getlist(settings.REQUEST_PARAMS['tickers'])
        return [ticker.upper() for ticker in tickers]
    return False

# Note: model must implement to_date() and to_dict() methods and have
#       ticker attribute
def market_queryset_to_dict(price_set):
    price_list = {}
    for price in price_set:
        price_list[price.to_date()] = price.to_dict() 
    return price_list

# If end_date and start_date are not provided, defaults to last 100 prices.
# If either end_date and start_date are provided, will return ALL records
# that match the criteria, i.e. less than or equal to end_date and greater_than
# or equal to start_date. Note, if only one is specified, the result will 
# contain all left-hand or right-hand records that match the criteria, i.e.
# if only start date is specified in, then it will return ALL records greater
# than or equal to the start_date
def parse_args_into_market_queryset(ticker, parsed_args=None):
    asset_type = markets.get_asset_type(ticker)

    if parsed_args is None or (parsed_args['start_date'] is None and parsed_args['end_date'] is None):
        if asset_type == app_settings.ASSET_EQUITY:
            queryset = EquityMarket.objects.filter(ticker=ticker).order_by('-date')[:app_settings.DEFAULT_ANALYSIS_PERIOD]
            return market_queryset_to_dict(price_set=queryset)
        if asset_type == app_settings.ASSET_CRYPTO:
            queryset = CryptoMarket.objects.filter(ticker=ticker).order_by('-date')[:app_settings.DEFAULT_ANALYSIS_PERIOD]
            return market_queryset_to_dict(price_set=queryset)

    elif parsed_args['start_date'] is None and parsed_args['end_date'] is not None:
        if asset_type == app_settings.ASSET_EQUITY:
            queryset= EquityMarket.objects.filter(ticker=ticker,
                                                    date__lte=parsed_args['end_date']).order_by('-date')
            return market_queryset_to_dict(price_set=queryset)

        if asset_type == app_settings.ASSET_CRYPTO:
            queryset = CryptoMarket.objects.filter(ticker=ticker,
                                                    date__lte=parsed_args['end_date']).order_by('-date')
            return market_queryset_to_dict(price_set=queryset)
        
    elif parsed_args['start_date'] is not None and parsed_args['end_date'] is not None:
        if asset_type == app_settings.ASSET_EQUITY:
            queryset = EquityMarket.objects.filter(ticker=ticker, date__gte=parsed_args['start_date'], 
                                                    date__lte=parsed_args['end_date']).order_by('-date')
            return market_queryset_to_dict(price_set=queryset)

        if asset_type == app_settings.ASSET_CRYPTO:
            queryset = CryptoMarket.objects.filter(ticker=ticker, date__gte=parsed_args['start_date'],
                                                    date_lte=parsed_args['end_date']).order_by('-date')
            return market_queryset_to_dict(price_set=queryset)

    elif parsed_args['start_date'] is not None and parsed_args['end_date'] is None:
        if asset_type == app_settings.ASSET_EQUITY:
            queryset = EquityMarket.objects.filter(ticker=ticker,
                                                    date__gte=parsed_args['start_date']).order_by('-date')
            return market_queryset_to_dict(price_set=queryset)

        if asset_type == app_settings.ASSET_CRYPTO:
            queryset = CryptoMarket.objects.filter(ticker=ticker,
                                                    date_gte=parsed_args['start_date']).order_by('-date')
            return market_queryset_to_dict(price_set=queryset)

    # TODO: raise exception instead of returning False
    return False

# Note: model must implement to_list() methods.
def dividend_queryset_to_dict(dividend_set):
    div_list = {}
    for dividend in dividend_set:
        div_list[dividend.to_date()] = dividend.to_dict()
    return div_list

def parse_args_into_dividend_queryset(ticker, parsed_args):
    if parsed_args['start_date'] is None and parsed_args['end_date'] is None:
        queryset = Dividends.objects.filter(ticker=ticker).order_by('-date')
        return dividend_queryset_to_dict(dividend_set=queryset)

    if parsed_args['start_date'] is None and parsed_args['end_date'] is not None:
        queryset = Dividends.objects.filter(ticker=ticker, date__lte=parsed_args['end_date']).order_by('-date')
        return dividend_queryset_to_dict(dividend_set=queryset)

    if parsed_args['start_date'] is not None and parsed_args['end_date'] is None:
        queryset = Dividends.objects.filter(ticker=ticker, date__gte=parsed_args['start_date']).order_by('-date')
        return dividend_queryset_to_dict(dividend_set=queryset)

    # start_date is not None and end_date is not None
    queryset = Dividends.objects.filter(ticker=ticker, date__gte=parsed_args['start_date'],
                                        date__lte=parsed_args['end_date']).order_by('-date')
    return dividend_queryset_to_dict(dividend_set=queryset)

def validate_request(request, allowed_methods=["GET"]):
    logger.debug('Verifying request method.')
    
    if verify_method(request, allowed_methods):
        logger.debug('Request method verified!')

        arg_err_or_tickers = parse_tickers(request)
        if arg_err_or_tickers:
            tickers = arg_err_or_tickers
            parsed_args = parse_secondary_args(request)

            return 200, { 'tickers': tickers, 'parsed_args': parsed_args }

        
        logger.debug('No ticker query parameters provided')    
        return 400, { 'message': 'Input error' }

    
    logger.debug('Request method rejected')
    return 405, { 'message' : "Request method not allowed" }