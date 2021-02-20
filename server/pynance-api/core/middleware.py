from django.http.request import HttpRequest

from core import settings

import util.outputter as outputter

class LogMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.logger=outputter.Logger("core.middleware.DebugMiddleware", settings.LOG_LEVEL)
        
    def __call__(self, request: HttpRequest):

        if ('liveness' not in request.path) and ('readiness' not in request.path):
            self.logger.debug(f'> Request Path: {request.path}')
            self.logger.debug(f'> Request Host: {request.META["HTTP_HOST"]}')

            if hasattr(request, 'user'):
                self.logger.debug(f'>> Request User: {request.user}')

            if 'api' in request.path:
                for key, value in request.GET.items():
                    if key == settings.REQUEST_PARAMS['tickers']:
                        tickers = request.GET.getlist(settings.REQUEST_PARAMS['tickers'])
                        for ticker in tickers:
                            self.logger.debug(f'>>> Request Parameter : {settings.REQUEST_PARAMS["tickers"]} = {ticker}')
                    else:
                        self.logger.debug(f'>>> Request Paramter : {key} = {value}')
                            
        response = self.get_response(request)

        return response