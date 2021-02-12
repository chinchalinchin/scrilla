
import app.settings as settings
import app.services as services

# OVERLAP = ['ABT', 'AC', 'GLD']
# TODO: need some way to distinguish between overlap.

def get_overlapping_symbols():
    equities = list(services.get_static_data(settings.ASSET_EQUITY))
    cryptos = list(services.get_static_data(settings.ASSET_CRYPTO))
    overlap = []
    for crypto in cryptos:
        if crypto in equities:
            overlap.append(crypto)
    return overlap

def get_asset_type(symbol):
    symbols = list(services.get_static_data(settings.ASSET_CRYPTO))
    overlap = get_overlapping_symbols()

    # TODO: need to differentiate between GLD etf and GLD crypto somehow!
    if symbol not in overlap and symbol in symbols:
        return settings.ASSET_CRYPTO
        
    else:
        return settings.ASSET_EQUITY
    # if other asset types are introduced, then uncomment these lines
    # and add new asset type to conditional. Keep in mind the static
    # equity data is HUGE.
        # symbols = list(services.get_static_data(settings.ASSET_EQUITY))
        # if symbol in symbols:
            # return settings.ASSET_EQUITY
        # else:
            #return None

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