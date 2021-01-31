
import app.settings as settings
import app.services as services

def get_asset_type(symbol):
    symbols = list(services.get_static_data(settings.ASSET_CRYPTO))

    # TODO: need to differentiate between GLD etf and GLD crypto somehow!
    if symbol in symbols and symbol != 'GLD':
        return settings.ASSET_CRYPTO
        
    else:
        symbols = list(services.get_static_data(settings.ASSET_EQUITY))
        if symbol in symbols:
            return settings.ASSET_EQUITY
        else:
            return None

def get_trading_period(asset_type):
    if asset_type == None:
        return False
    elif asset_type == settings.ASSET_CRYPTO:
        return settings.ONE_TRADING_DAY
    elif asset_type == settings.ASSET_EQUITY:
        return (1/365)
    else:
        return settings.ONE_TRADING_DAY

def get_risk_free_rate():
    # TODO: call Quandl to get 1 year interest rate
    
    pass