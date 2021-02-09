# Python Imports
import sys

# Django Imports
from django.shortcuts import render
from django.http import JsonResponse, HttpResponse

# Server Imports
from core import settings
from debug import DebugLogger

# Application Imports
from app.portfolio import Portfolio
import app.settings as app_settings
import app.statistics as statistics
import app.optimizer as optimizer
import util.helper as helper
import util.plotter as plotter

logger = DebugLogger("server.pynance_api.api.views").get_logger()

def verify_method(request, allowed_methods):
    if request.method not in allowed_methods: 
        return False
    else:
        return True

def log_secondary_args(parsed_args):
    if parsed_args['start_date'] is not None:
        logger.info('> Start : %s', parsed_args['start_date'])

    if parsed_args['end_date'] is not None:
        logger.info('> End: %s', parsed_args['end_date'])
    
    if parsed_args['target_return'] is not None:
        logger.info('> Target: %s', parsed_args['target_return'])
    
    if parsed_args['jpeg'] is not None:
        logger.info('> JPEG: %s', parsed_args['jpeg'])

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
        jpeg = True if jpeg.lower() == 'true' else False
    else:
        jpeg = None

    parsed_args = {
        'start_date': start_date,
        'end_date': end_date,
        'target_return': target_return,
        'jpeg': jpeg
    }
    log_secondary_args(parsed_args)

    return parsed_args

def validate_request(request, allowed_methods=["GET"]):
    logger.info('Verifying request method...')
    if verify_method(request, allowed_methods):
        logger.info('Request method verified!')

        if settings.REQUEST_PARAMS['tickers'] in request.GET:
            tickers = request.GET.getlist(settings.REQUEST_PARAMS['tickers'])
            parsed_args = parse_secondary_args(request)

            return 200, {
                'tickers': tickers,
                'parsed_args': parsed_args
            }

        else:
            logger.info('No ticker query parameters provided')    
            return 400, { 'message': 'Input error' }

    else:
        logger.info('Request method rejected')
        return 405, { 'message' : "Request method not allowed" }

def optimize(request):
    status, parsed_args_or_err_msg = validate_request(request, ["GET"])

    if status == 400 or status == 405:
        return JsonResponse(data=parsed_args_or_err_msg, status=status, safe=False)

    else:
        tickers = parsed_args_or_err_msg['tickers']
        parsed_args = parsed_args_or_err_msg['parsed_args']

        portfolio = Portfolio(tickers=tickers, start_date=parsed_args['start_date'], end_date=parsed_args['end_date'])
        allocation = optimizer.optimize_portfolio_variance(portfolio=portfolio, target_return=parsed_args['target_return'])

        response = {
            'portfolio_return' : portfolio.return_function(allocation),
            'portfolio_volatility': portfolio.volatility_function(allocation)
        }
        for i in range(len(tickers)):
            allocation_string = f'{tickers[i]}_allocation'
            response[allocation_string] = allocation[i]
        
        return JsonResponse(data=response, status=status, safe=False)

def risk_return(request):
    status, parsed_args_or_err_msg = validate_request(request, ["GET"])

    if status == 400 or status == 405:
        return JsonResponse(data=parsed_args_or_err_msg, status=status, safe=False)

    else:
        tickers = parsed_args_or_err_msg['tickers']
        parsed_args = parsed_args_or_err_msg['parsed_args']

        response = {}
        profiles = []
        for i in range(len(tickers)):
            ticker_str = f'tickers[i]'
            logger.info('Calculating risk-return profile for %s', tickers[i])
            response[ticker_str] = statistics.calculate_risk_return(ticker=tickers[i], 
                                                                start_date=parsed_args['start_date'], 
                                                                end_date=parsed_args['end_date'])
            if parsed_args['jpeg']:
                profiles += response[ticker_str]

        if parsed_args['jpeg']:
            graph = plotter.plot_profiles(symbols=tickers, profiles=profiles, show=False)
            with open(graph, "rb") as f:
                return HttpResponse(f.read(), content_type="image/jpeg")

        else:
            return JsonResponse(data=response, status=status, safe=False)

def efficient_frontier(request):
    status, parsed_args_or_err_msg = validate_request(request, ["GET"])

    if status == 400 or status == 405:
        return JsonResponse(data=parsed_args_or_err_msg, status=status, safe=False)
    
    else:
        tickers = parsed_args_or_err_msg['tickers']
        parsed_args = parsed_args_or_err_msg['parsed_args']

        portfolio = Portfolio(tickers=tickers, start_date=parsed_args['start_date'], end_date=parsed_args['end_date'])
        frontier = optimizer.calculate_efficient_frontier(portfolio=portfolio)
    
        response = {}
        for i in range(len(frontier)):
            subresponse = {}
            allocation = frontier[i]

            ret_string, vol_string, port_string = f'portfoli_{i}_return', f'portfolio_{i}_volatility', f'portfolio_{i}'

            subresponse[return_string] = portfolio.return_function(allocation)
            subresponse[volatility_string] = portfolio.volatility_function(allocation)

            for j in range(len(tickers)):
                allocation_string = f'{tickers[j]}_allocation_{i}'
                subresponse[allocation_string] = allocation[j]
                
            response[portfolio_string] = subresponse
        
        if parsed_args['jpeg']:
            graph = plotter.plot_frontier(portfolio=portfolio, frontier=frontier, show=False)
            with open(graph, "rb") as f:
                return HttpResponse(f.read(), content_type="image/jpeg")
        else:
            return JsonResponse(data=response, status=status, safe=False) 

# TODO: in future allow user to specify moving average periods through query parameters! 
def moving_averages(request, jpeg=False):
    status, parsed_args_or_err_msg = validate_request(request, ["GET"])

    if status == 400 or status == 405:
        return JsonResponse(data=parsed_args_or_err_msg, status=status, safe=False)

    else:
        tickers = parsed_args_or_err_msg['tickers']
        parsed_args = parsed_args_or_err_msg['parsed_args']
        averages_output = statistics.calculate_moving_averages(tickers=tickers, start_date=parsed_args['start_date'], 
                                                                        end_date=parsed_args['end_date'])
        moving_averages, dates = averages_output

        response = {}
        for i in range(len(tickers)):
            ticker_str=f'{tickers[i]}'
            MA_1_str, MA_2_str, MA_3_str = f'{ticker_str}_MA_1', f'{ticker_str}_MA_2', f'{ticker_str}_MA_3'    

            if parsed_args['start_date'] is None and parsed_args['end_date']:
                response[ticker_str][MA_1_str] = moving_averages[i][0]
                response[ticker_str][MA_2_str] = moving_averages[i][1]
                response[ticker_str][MA_3_str] = moving_averages[i][2]

            else:
                subres_1, subres_2, subres_3 = {}, {}, {}
        
                for j in range(len(dates)):
                    date_str=dates[j]
                    subres_1[date_str] = moving_averages[i][0][j]
                    subres_2[date_str] = moving_averages[i][1][j]
                    subres_3[date_str] = moving_averages[i][2][j]
 
                response[ticker_str][MA_1_str] = subres_1
                response[ticker_str][MA_2_str] = subres_2
                response[ticker_str][MA_3_str] = subres_3
                        
        if parsed_args['jpeg']:
            periods = [settings.MA_1_PERIOD, settings.MA_2_PERIOD, settings.MA_3_PERIOD]
            graph = plotter.plot_moving_averages(symbols=tickers, averages_output=averages_output, periods=periods,
                                                    show=False)
            with open(graph, 'rb') as f:
                return HttpResponse(f.read(), content_type="image/jpeg")
            pass
        else:
            return JsonResponse(data = response, status=status, safe=False)

