from django.http.request import HttpRequest
from django.contrib.auth.models import User
from django.contrib.auth import authenticate

import app.settings as app_settings
import util.outputter as outputter

# TODO: use django user's password as API key
class APIKeyMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.logger=outputter.Logger("auth.middleware.APIKeyMiddleware", app_settings.LOG_LEVEL)

    def __call__(self, request: HttpRequest):
        # TODO: check request param for api_key
        #       check authorization header for api_key
        #       if api_key exists
        #           request.is_authenticated = True to request
        #       else: 
        #           request.is_authenticated = False
        response = self.get_response
        return response