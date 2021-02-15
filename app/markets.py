
import app.statistics as statistics
import app.settings as settings
import app.services as services
import app.files as files
from app.objects.cashflow import Cashflow

import util.logger as logger

MODEL_DDM="ddm"
# TODO: implement dcf model
MODEL_DCF="dcf"

output = logger.Logger('app.markets', settings.LOG_LEVEL)

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
    equities = list(files.get_static_data(settings.ASSET_EQUITY))
    cryptos = list(files.get_static_data(settings.ASSET_CRYPTO))
    overlap = []
    for crypto in cryptos:
        if crypto in equities:
            overlap.append(crypto)
    return overlap

def get_asset_type(symbol):
    symbols = list(files.get_static_data(settings.ASSET_CRYPTO))
    overlap = get_overlapping_symbols()

    # TODO: need to differentiate between GLD etf and GLD crypto somehow!
    if symbol not in overlap:
        if symbol in symbols:
            return settings.ASSET_CRYPTO
            
        else:
                # if other asset types are introduced, then uncomment these lines
                # and add new asset type to conditional. Keep in mind the static
                # equity data is HUGE.
            # symbols = list(files.get_static_data(settings.ASSET_EQUITY))
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

# NOTE: Quandl outputs interest in percentage terms
# NOTE: This function sort of blurs the lines between services.py and markets.py
#       I put it here because I want the markets.py class to be from where the 
#       the risk_free_rate is accessed for now. It may make more sense to have this
#       in services.py since it's basically just a call an external service.
#       Haven't made up my mind yet. 
def get_risk_free_rate():
    if settings.STAT_MANAGER == "quandl":
        risk_free_rate_key = settings.ARG_Q_YIELD_CURVE[settings.RISK_FREE_RATE]
        risk_free_rate = services.get_daily_stats_latest(statistic=risk_free_rate_key)
        return (risk_free_rate)/100

def sharpe_ratio(ticker, start_date=None, end_date=None):
    ticker_profile = statistics.calculate_risk_return(ticker=ticker, start_date=start_date,
                                                        end_date=end_date)
    return (ticker_profile['annual_return'] - get_risk_free_rate())/ticker_profile['annual_volatility']

# if no dates are specified, defaults to last 100 days
def market_premium(start_date=None, end_date=None):
    market_profile = statistics.calculate_risk_return(ticker=settings.MARKET_RATE, 
                                                        start_date=start_date, 
                                                        end_date=end_date)
    return (market_profile['annual_return'] - get_risk_free_rate())

def market_beta(ticker, start_date=None, end_date=None):
    market_profile = statistics.calculate_risk_return(ticker=settings.MARKET_RATE, start_date=start_date, 
                                                        end_date=end_date)
    market_covariance = statistics.calculate_return_covariance(ticker_1=ticker, ticker_2=settings.MARKET_RATE,
                                                            start_date=start_date, end_date=end_date)
    return market_covariance / (market_profile['annual_volatility']**2)

def cost_of_equity(ticker, start_date=None, end_date=None):
    beta = market_beta(ticker=ticker, start_date=start_date, end_date=end_date)
    premium = market_premium(start_date=start_date, end_date=end_date)

    return (premium*beta + get_risk_free_rate())

def screen_for_discount(model=None, discount_rate=None):
    """
    Parameters
    ----------
    model : str \n
        Model used to value the equities saved in the watchlist. If no model is specified, the function will default to MODEL_DDM. Model constants are statically accessible through the variables: MODEL_DDM (Discount Dividend Model), MODEL_DCF (Discounted Cash Flow Model, not yet implemented) \n \n

    Output
    ------
    A list of tickers that trade at a discount relative to the model price, formatted as follows: \n
        { 'ticker' : { \n 
                'spot_price': float, \n
                'model_price': float, \n
                'discount': float \n 
            }\n
        }\n \n 
    """
    if model is None:
        model = MODEL_DDM

    equities = list(files.get_watchlist())
    discounts = {}
    
    output.debug('Using Discount Dividend Model to screen watchlisted equities for discounts.')

    for equity in equities:
        spot_price = services.get_daily_price_latest(ticker=equity)

        if discount_rate is None:
            discount_rate = cost_of_equity(ticker=equity)

        if model == MODEL_DDM:
            dividends = services.get_dividend_history(equity)
            output.debug(f'Passing discount rate = {discount_rate}')
            model_price = Cashflow(sample=dividends, discount_rate=discount_rate).calculate_net_present_value()
        
        if not model_price:
            output.debug(f'Net present value of dividend payments cannot be calculated for {equity}.')
        else:
            output.verbose(f'{equity} spot price = {spot_price}, {equity} {model} price = {model_price}')

            discount = float(model_price) - float(spot_price)
                        
            if discount > 0:
                discount_result = {}
                discount_result['spot_price'] = spot_price
                discount_result['model_price'] = model_price
                discount_result['discount'] = discount
                discounts[equity] = discount_result
                output.debug(f'Discount of {discount} found for {equity}')

    return discounts