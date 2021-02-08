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
import util.helper as helper

logger = DebugLogger("server.pynance_api.api.views").get_logger()

def verify_method(request, allowed_methods):
    if request.method not in allowed_methods: 
        return False
    else:
        return True

def get_secondary_args(request):
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
    return parsed_args

def risk_return(request):
    logger.info('Verifying request method...')
    if verify_method(request, ["GET"]):
        logger.info('Request method verified!')

        if settings.REQUEST_PARAMS['tickers'] in request.GET:
            tickers = request.GET.getlist(settings.REQUEST_PARAMS['tickers'])

            parsed_args = get_secondary_args(request)
            
            response = {}
            for ticker in tickers:
                logger.info('Calculating risk-return profile for %s', ticker)

                if parsed_args['start_date'] is not None:
                    logger.info('> Start : %s', parsed_args['start_date'])

                if parsed_args['end_date'] is not None:
                    logger.info('> End: %s', parsed_args['end_date'])
                response[ticker] = statistics.calculate_risk_return(ticker=ticker, 
                                                                    start_date=parsed_args['start_date'], 
                                                                    end_date=parsed_args['end_date'])

            return JsonResponse(response, status=200, safe=False)
        
        else:
            logger.info('No query parameters provided')
            error_400 = { 'message': 'Input error' }
            return JsonResponse(error_400, status=400, safe=False)

    else:
        logger.info('Request method rejected')
        error_405 = { 'message' : "Request method not allowed" }
        return JsonResponse(error_405, status=405, safe=False)

def optimize(request):
    return JsonResponse({'message': 'other test successful'}, safe=False) 