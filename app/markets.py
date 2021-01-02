
import app.settings as settings
import app.services as services

def get_asset_type(symbol):
    symbols = list(services.get_static_data(settings.ASSET_CRYPTO))

    if symbol in symbols:
        return settings.ASSET_CRYPTO
        
    else:
        symbols = list(services.get_static_data(settings.ASSET_EQUITY))
        if symbol in symbols:
            return settings.ASSET_EQUITY
        else:
            return None

def get_risk_free_rate():
    # TODO: call Quandl to get 1 year interest rate
    
    pass