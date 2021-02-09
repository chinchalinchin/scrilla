# Python Imports
import sys

# Django Imports
from django.shortcuts import render
from django.http import JsonResponse

# Server Imports
from core import settings
from debug import DebugLogger

# Application Imports
import app.statistics as statistics
import app.optimizer as optimizer
import util.helper as helper

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

    parsed_args = {
        'start_date': start_date,
        'end_date': end_date,
        'target_return': target_return
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

def risk_return(request):
    status, parsed_args_or_err_msg = validate_request(request, ["GET"])

    if status == 400 or status == 405:
        return JsonResponse(parsed_args_or_err_msg, status=status, safe=False)

    else:
        tickers = parsed_args_or_err_msg['tickers']
        parsed_args = parsed_args_or_err_msg['parsed_args']

        response = {}
        for ticker in tickers:
            logger.info('Calculating risk-return profile for %s', ticker)
            response[ticker] = statistics.calculate_risk_return(ticker=ticker, 
                                                                start_date=parsed_args['start_date'], 
                                                                end_date=parsed_args['end_date'])

        return JsonResponse(response, status=status, safe=False)
        


def optimize(request):
    logger.info('Verifying request method...')
    status, parsed_args_or_err_msg = validate_request(request, ["GET"])

    if status == 400 or status == 405:
        return JsonResponse(parsed_args_or_err_msg, status=status, safe=False)

    else:
        tickers = parsed_args_or_err_msg['tickers']
        parsed_args = parsed_args_or_err_msg['parsed_args']

        if parsed_args['target_return'] is None:
            # TODO: minimize
            pass
        else:
            # Optimize subject to target return constraint
            pass