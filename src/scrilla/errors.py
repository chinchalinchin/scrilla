from scrilla import settings, files

import util.helper as helper

class InputValidationError(Exception):
    def __init__(self, message):
        super().__init__(message)

class APIResponseError(Exception):
    def __init__(self, message):
        super().__init__(message)

class ConfigurationError(Exception):
    def __init__(self, message):
        super().__init__(message)

def validate_asset_type(ticker, asset_type=None):
    if asset_type is not None:
        asset_type = files.get_asset_type(ticker) 
        if asset_type is None:
            raise InputValidationError(f'{ticker} cannot be mapped to (crypto, equity) asset classes')
        return asset_type
    if asset_type == settings.ASSET_CRYPTO or asset_type == settings.ASSET_EQUITY:
        return asset_type
    raise InputValidationError(f'{ticker} cannot be mapped to (crypto, equity) asset classes')

def validate_dates(start_date, end_date, asset_type):
    # verify dates are in order if they exist
    if end_date is not None and start_date is not None:
        start_date, end_date = helper.validate_order_of_dates(start_date, end_date)

    # if end date exists, make sure it is valid
    if end_date is not None:
        end_date = helper.truncate_future_from_date(end_date)
        if asset_type == settings.ASSET_EQUITY and not helper.is_trading_date(end_date):
            end_date = helper.get_previous_business_date(end_date)
    # else create a sensible end date
    else:
        if asset_type == settings.ASSET_CRYPTO:
            end_date = helper.get_today()
        else:
            end_date = helper.get_last_trading_date()        

    # if start date exists, make sure it is valide
    if start_date is not None:
        if helper.is_future_date(start_date):
            # only invalid user input is if start date doesn't exist yet
            raise InputValidationError(f'Start date of {helper.date_to_string(start_date)} is greater than today')

        if asset_type == settings.ASSET_EQUITY and not helper.is_trading_date(start_date):
            start_date = helper.get_previous_business_date(start_date)

    # else create a sensible start date
    else:
        if asset_type == settings.ASSET_CRYPTO:
            start_date = helper.decrement_date_by_days(end_date, settings.DEFAULT_ANALYSIS_PERIOD)
        else:
            start_date = helper.decrement_date_by_business_days(end_date, settings.DEFAULT_ANALYSIS_PERIOD)

    return start_date, end_date