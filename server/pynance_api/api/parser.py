from core import settings
from data.models import EquityMarket, CryptoMarket, EquityTicker, CryptoTicker, Dividends, Economy, StatSymbol

import util.helper as helper
import util.logger as logger

import app.markets as markets
import app.settings as app_settings

output = logger.Logger("server.pynance_api.api.parser", settings.LOG_LEVEL)

def verify_method(request, allowed_methods):
    if request.method not in allowed_methods: 
        return False
    else:
        return True

def log_secondary_args(parsed_args):
    output.debug('> Request Parameters')
    if parsed_args['start_date'] is not None:
        output.debug(f'>> Start : {parsed_args["start_date"]}')

    if parsed_args['end_date'] is not None:
        output.debug(f'>> End: {parsed_args["end_date"]}')
    
    if parsed_args['target_return'] is not None:
        output.debug(f'>> Target: {parsed_args["target_return"]}')
    
    if parsed_args['jpeg'] is not None:
        output.debug(f'>> JPEG: {parsed_args["jpeg"]}')

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

    if settings.REQUEST_PARAMS['jpeg'] in request.GET:
        jpeg = str(request.GET.get(settings.REQUEST_PARAMS['jpeg']))
        jpeg = jpeg.lower() == 'true'
    else:
        jpeg = None

    if settings.REQUEST_PARAMS['discount_rate'] in request.GET:
        discount = request.GET.get(settings.REQUEST_PARAMS['discount_rate'])
    else:
        discount = None

    parsed_args = {
        'start_date': start_date,
        'end_date': end_date,
        'target_return': target_return,
        'jpeg': jpeg,
        'discount_rate': discount
    }
    log_secondary_args(parsed_args)

    return parsed_args

def parse_tickers(request):
    if settings.REQUEST_PARAMS['tickers'] in request.GET:
        tickers = request.GET.getlist(settings.REQUEST_PARAMS['tickers'])
        return [ticker.upper() for ticker in tickers]
    else:
        return False

# If end_date and start_date are not provided, defaults to last 100 prices.
# If either end_date and start_date are provided, will return ALL records
# that match the criteria, i.e. less than or equal to end_date and greater_than
# or equal to start_date. Note, if only one is specified, the result will 
# contain all left-hand or right-hand records that match the criteria, i.e.
# if only start date is specified in, then it will return ALL records greater
# than or equal to the start_date
def parse_args_into_market_queryset(ticker, parsed_args):
    asset_type = markets.get_asset_type(ticker)

    if parsed_args['start_date'] is None and parsed_args['end_date'] is None:
        if asset_type == app_settings.ASSET_EQUITY:
            return EquityMarket.objects.filter(ticker=ticker).order_by('-date')[:100]
        elif asset_type == app_settings.ASSET_CRYPTO:
            return CryptoMarket.objects.filter(ticker=ticker).order_by('-date')[:100]
        else:
            return False

    elif parsed_args['start_date'] is None and parsed_args['end_date'] is not None:
        if asset_type == app_settings.ASSET_EQUITY:
            return EquityMarket.objects.filter(ticker=ticker,
                                                date__lte=parsed_args['end_date']).order_by('-date')
        elif asset_type == app_settings.ASSET_CRYPTO:
            return CryptoMarket.objects.filter(ticker=ticker,
                                                date__lte=parsed_args['end_date']).order_by('-date')
        else:
            return False
        
    elif parsed_args['start_date'] is not None and parsed_args['end_date'] is not None:
        if asset_type == app_settings.ASSET_EQUITY:
            return EquityMarket.objects.filter(ticker=ticker, date__gte=parsed_args['start_date'], 
                                                date__lte=parsed_args['end_date']).order_by('-date')
        elif asset_type == app_settings.ASSET_CRYPTO:
            return CryptoMarket.objects.filter(ticker=ticker, date__gte=parsed_args['start_date'],
                                                date_lte=parsed_args['end_date']).order_by('-date')
        else:
            return False

    # start_date is not None and end_date is None
    else:
        if asset_type == app_settings.ASSET_EQUITY:
            return EquityMarket.objects.filter(ticker=ticker,
                                                date__gte=parsed_args['start_date']).order_by('-date')
        elif asset_type == app_settings.ASSET_CRYPTO:
            return CryptoMarket.objects.filter(ticker=ticker,
                                                date_gte=parsed_args['start_date']).order_by('-date')
        else:
            return False

def parse_args_into_dividend_queryset(ticker, parsed_args):
    if parsed_args['start_date'] is None and parsed_args['end_date'] is None:
        return Dividends.objects.filter(ticker=ticker).order_by('-date')

    elif parsed_args['start_date'] is None and parsed_args['end_date'] is not None:
        return Dividends.objects.filter(ticker=ticker, date__lte=parsed_args['end_date']).order_by('-date')

    elif parsed_args['start_date'] is not None and parsed_args['end_date'] is None:
        return Dividends.objects.filter(ticker=ticker, date__gte=parsed_args['start_date']).order_by('-date')
    
    # start_date is not None and end_date is not None
    else:
        return Dividends.objects.filter(ticker=ticker, date__gte=parsed_args['start_date'],
                                            date__lte=parsed_args['end_date']).order_by('-date')

# Note: model must implement to_date() and to_list() methods and have
#       ticker attribute
def market_queryset_to_list(price_set):
    set_list, price_list = {}, {}
    for price in price_set:
        price_list[price.to_date()] = price.to_list() 
    set_list[price_models.ticker] = price_list
    return set_list

# Note: model must implement to_list() methods.
def dividend_queryset_to_list(dividend_set):
    div_list = {}
    for dividend in dividend_set:
        div_list.append(dividend.to_list())
    return div_list

def validate_request(request, allowed_methods=["GET"]):
    output.debug('Verifying request method.')
    if verify_method(request, allowed_methods):
        output.debug('Request method verified!')

        arg_err_or_tickers = parse_tickers(request)
        if arg_err_or_tickers:
            tickers = arg_err_or_tickers
            parsed_args = parse_secondary_args(request)

            return 200, { 'tickers': tickers, 'parsed_args': parsed_args }

        else:
            output.debug('No ticker query parameters provided')    
            return 400, { 'message': 'Input error' }

    else:
        output.debug('Request method rejected')
        return 405, { 'message' : "Request method not allowed" }