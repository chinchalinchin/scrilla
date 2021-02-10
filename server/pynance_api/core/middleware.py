from urllib.parse import urlencode
from django.http.request import HttpRequest

from core import settings

from util.logger import Logger, LOG_LEVEL_DEBUG, LOG_LEVEL_VERBOSE

class LogMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.logger=Logger("core.middleware.DebugMiddleware", settings.LOG_LEVEL)
        
    def __call__(self, request: HttpRequest):

        if settings.LOG_LEVEL in [LOG_LEVEL_DEBUG, LOG_LEVEL_VERBOSE]:
            if ('liveness' not in request.path) and ('readiness' not in request.path):
                self.comment(f'> Request Path: {request.path}')
                self.logger.info(f'> Request Host: {request.META["HTTP_HOST"]}')

                if hasattr(request, 'user'):
                    self.logger.info('>> Request User: %s', request.user)
    
                if 'api' in request.path:
                    for key, value in request.GET.items():
                        if key == settings.REQUEST_PARAMS['tickers']:
                            tickers = request.GET.getlist(settings.REQUEST_PARAMS['tickers'])
                            for ticker in tickers:
                                self.logger.info('>>> Request Parameter : %s = %s', settings.REQUEST_PARAMS['tickers'], ticker)
                        else:
                            self.logger.info('>>> Request Paramter : %s = %s', key, value)
                            
        response = self.get_response(request)

        return response