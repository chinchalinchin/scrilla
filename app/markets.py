
import app.settings as settings
import app.services as services
from app.objects.cashflow import Cashflow

MODEL_DDM="ddm"
# TODO: implement dcf model
MODEL_DCF="dcf"

# NOTE: output from get_overlapping_symbols:
# OVERLAP = ['ABT', 'AC', 'ADT', 'ADX', 'AE', 'AGI', 'AI', 'AIR', 'AMP', 'AVT', 'BCC', 'BCD', 'BCH', 'BCX', 'BDL', 'BFT', 'BIS', 'BLK', 'BQ', 'BRX', 
# 'BTA', 'BTG', 'CAT', 'CMP', 'CMT', 'CNX', 'CTR', 'CURE', 'DAR', 'DASH', 'DBC', 'DCT', 'DDF', 'DFS', 'DTB', 'DYN', 'EBTC', 'ECC', 'EFL', 'ELA', 'ELF',
# 'EMB', 'ENG', 'ENJ', 'EOS', 'EOT', 'EQT', 'ERC', 'ETH', 'ETN', 'EVX', 'EXP', 'FCT', 'FLO', 'FLT', 'FTC', 'FUN', 'GAM', 'GBX', 'GEO', 'GLD', 'GNT', 
# 'GRC', 'GTO', 'INF', 'INS', 'INT', 'IXC', 'KIN', 'LBC', 'LEND', 'LTC', 'MAX', 'MCO', 'MEC', 'MED', 'MGC', 'MINT', 'MLN', 'MNE', 'MOD', 'MSP', 'MTH', 
# 'MTN', 'MUE', 'NAV', 'NEO', 'NEOS', 'NET', 'NMR', 'NOBL', 'NXC', 'OCN', 'OPT', 'PBT', 'PING', 'PPC', 'PPT', 'PRG', 'PRO', 'PST', 'PTC', 'QLC', 'QTUM',
# 'R', 'RDN', 'REC', 'RVT', 'SALT', 'SAN', 'SC', 'SKY', 'SLS', 'SPR', 'SNX', 'STK', 'STX', 'SUB', 'SWT', 'THC', 'TKR', 'TRC', 'TRST', 'TRUE', 'TRX', 
# 'TX', 'UNB', 'VERI', 'VIVO', 'VOX', 'VPN', 'VRM', 'VRS', 'VSL', 'VTC', 'VTR', 'WDC', 'WGO', 'WTT', 'XEL', 'NEM', 'ZEN']

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
    if symbol not in overlap:
        if symbol in symbols:
            return settings.ASSET_CRYPTO
            
        else:
                # if other asset types are introduced, then uncomment these lines
                # and add new asset type to conditional. Keep in mind the static
                # equity data is HUGE.
            # symbols = list(services.get_static_data(settings.ASSET_EQUITY))
            # if symbol in symbols:
                # return settings.ASSET_EQUITY
            # else:
                #return None
            return settings.ASSET_EQUITY
    else:
        # default to equity for overlap until a better method is determined. 
        return settings.ASSET_EQUITY

def get_trading_period(asset_type):
    if asset_type == None:
        return False
    elif asset_type == settings.ASSET_CRYPTO:
        return settings.ONE_TRADING_DAY
    elif asset_type == settings.ASSET_EQUITY:
        return (1/365)
    else:
        return settings.ONE_TRADING_DAY

def screen_for_discount(model=MODEL_DDM):
    risk_free_rate = services.get_risk_free_rate()
    equities = list(services.get_watchlist())
    for equity in equities:
        dividends = services.get_dividend_history(equity)
        div_npv = Cashflow(dividends).calculate_net_present_value(discount_rate=risk_free_rate)

