
import app.statistics as statistics
import app.settings as settings
import app.services as services
import app.files as files
from app.objects.cashflow import Cashflow

import util.outputter as outputter

MODEL_DDM="ddm"
# TODO: implement dcf model
MODEL_DCF="dcf"

logger = outputter.Logger('app.markets', settings.LOG_LEVEL)

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
    """
    Description
    -----------
    Returns an array of symbols which are contained in both the STATIC_TICKERS_FILE and STATIC_CRYPTO_FILE, i.e. ticker symbols which have both a tradeable equtiy and a tradeable crypto asset. 
    """
    equities = list(files.get_static_data(settings.ASSET_EQUITY))
    cryptos = list(files.get_static_data(settings.ASSET_CRYPTO))
    overlap = []
    for crypto in cryptos:
        if crypto in equities:
            overlap.append(crypto)
    return overlap

def get_asset_type(symbol):
    """"
    Description
    -----------
    Returns the asset type of the supplied ticker symbol. \n \n

    Output
    ------
    A string representing the type of asset of the symbol. Types are statically accessible through the `app.settings` variables: ASSET_EQUITY and ASSET_CRYPTO. \n \n 
    """
    symbols = list(files.get_static_data(settings.ASSET_CRYPTO))
    overlap = get_overlapping_symbols()

    if symbol not in overlap:
        if symbol in symbols:
            return settings.ASSET_CRYPTO
            
                # if other asset types are introduced, then uncomment these lines
                # and add new asset type to conditional. Keep in mind the static
                # equity data is HUGE.
        # symbols = list(files.get_static_data(settings.ASSET_EQUITY))
        # if symbol in symbols:
            # return settings.ASSET_EQUITY
        #return None
        return settings.ASSET_EQUITY
    # default to equity for overlap until a better method is determined. 
    return settings.ASSET_EQUITY

def get_trading_period(asset_type):
    """
    Description
    -----------
    Returns the value of one trading day measured in years of the asset_type passed in as an argument.

    Parameters
    ----------
    1. asset_type : str\n
    
    A string that represents a type of tradeable asset. Types are statically accessible through the `app.settings` variables: ASSET_EQUITY and ASSET_CRYPTO.
    """
    if asset_type is None:
        return False
    if asset_type == settings.ASSET_CRYPTO:
        return settings.ONE_TRADING_DAY
    if asset_type == settings.ASSET_EQUITY:
        return (1/365)
    return settings.ONE_TRADING_DAY

# NOTE: Quandl outputs interest in percentage terms
# NOTE: This function sort of blurs the lines between services.py and markets.py
#       I put it here because I want the markets.py class to be from where the 
#       the risk_free_rate is accessed for now. It may make more sense to have this
#       in services.py since it's basically just a call an external service.
#       Haven't made up my mind yet. 
def get_risk_free_rate():
    """
    Description
    -----------
    Returns as a decimal the risk free rate defined by the RISK_FREE environment variable (and passed into `app.settings` as the variable RISK_FREE_RATE). \n \n 
    """
    if settings.STAT_MANAGER == "quandl":
        risk_free_rate_key = settings.ARG_Q_YIELD_CURVE[settings.RISK_FREE_RATE]
        risk_free_rate = services.get_daily_stats_latest(statistic=risk_free_rate_key)
        return (risk_free_rate)/100

# NOTE: if ticker_profile is provided, it effectively nullifies start_date and end_date.
# TODO: pass in risk_free_rate=None as optional argument to prevent overusing services
def sharpe_ratio(ticker, start_date=None, end_date=None, ticker_profile=None):
    """
    Description
    -----------
    Returns the value of the sharpe ratio for the supplied ticker over the specified time range. If no start and end date are supplied, calculation will default to the last 100 days of prices. \n \n 

    Parameters
    ----------
    1. ticker : str \n
        A string of the ticker symbol whose sharpe ratio will be computed. \n \n

    2. start_date : datetime.date \n 
        Start date of the time period for which the sharpe ratio will be computed. \n \n 

    3. end_date : datetime.date \n 
        End_date of the time period for which the sharpe ratio will be computed. \n \n 

    """
    if ticker_profile is None:
        ticker_profile = statistics.calculate_risk_return(ticker=ticker, start_date=start_date,
                                                        end_date=end_date)

    return (ticker_profile['annual_return'] - get_risk_free_rate())/ticker_profile['annual_volatility']

# if no dates are specified, defaults to last 100 days
def market_premium(start_date=None, end_date=None, market_profile = None):
    """
    Description
    -----------
    Returns the excess of the market return defined by the environment variable MARKET_PROXY and the risk free rate defined by the RISK_FREE rate. \n \n 

    Parameters
    ----------
    1. start_date : datetime.date \n 
        Start date of the time period for which the market premium will be computed. \n \n 

    2. end_date : datetime.date \n 
        End_date of the time period for which the market premium will be computed. \n \n 

    """
    if market_profile is None:
        market_profile = statistics.calculate_risk_return(ticker=settings.MARKET_PROXY, 
                                                            start_date=start_date, 
                                                            end_date=end_date)

    return (market_profile['annual_return'] - get_risk_free_rate())

def market_beta(ticker, start_date=None, end_date=None, market_profile=None, market_correlation=None, ticker_profile=None):
    """
    Description
    -----------
    Returns the beta of an asset with the market return defined by the environment variable MARKET_PROXY.

    Parameters
    ----------
    1. ticker : str \n
        A string of the ticker symbol whose asset beta will be computed. \n \n

    2. start_date : datetime.date \n 
        Start date of the time period for which the asset beta will be computed. \n \n 

    3. end_date : datetime.date \n 
        End_date of the time period for which the asset beta will be computed. \n \n 

    """
    if market_profile is None:
        market_profile = statistics.calculate_risk_return(ticker=settings.MARKET_PROXY, start_date=start_date, 
                                                            end_date=end_date)
    if ticker_profile is None:
        ticker_profile = statistics.calculate_risk_return(ticker=ticker,start_date=start_date,end_date=end_date)

    market_covariance = statistics.calculate_return_covariance(ticker_1=ticker, ticker_2=settings.MARKET_PROXY,
                                                                profile_1=ticker_profile, profile_2=market_profile,
                                                                correlation = market_correlation,
                                                                start_date=start_date, end_date=end_date)
    return market_covariance / (market_profile['annual_volatility']**2)

def cost_of_equity(ticker, start_date=None, end_date=None, market_profile=None, market_correlation=None):
    """
    Description
    -----------
    Returns the cost of equity of an asset as estimated by the Capital Asset Pricing Model, i.e. the product of the market premium and asset beta increased by the risk free rate. \n \n 
    Parameters
    ----------
    1. ticker : str \n
        A string of the ticker symbol whose cost of equity ratio will be computed. \n \n

    2. start_date : datetime.date \n 
        Start date of the time period for which the cost of equity ratio will be computed. \n \n 

    3. end_date : datetime.date \n 
        End_date of the time period for which the cost of equity ratio will be computed. \n \n 

    """
    beta = market_beta(ticker=ticker, start_date=start_date, end_date=end_date,
                        market_profile=market_profile, market_correlation=market_correlation)
    premium = market_premium(start_date=start_date, end_date=end_date, market_profile=market_profile)

    return (premium*beta + get_risk_free_rate())

def screen_for_discount(model=None, discount_rate=None):
    """
    Parameters
    ----------
    model : str \n
        Model used to value the equities saved in the watchlist. If no model is specified, the function will default to MODEL_DDM. Model constants are statically accessible through the `app.settings` variables: MODEL_DDM (Discount Dividend Model), MODEL_DCF (Discounted Cash Flow Model, not yet implemented) \n \n

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
    
    logger.debug('Using Discount Dividend Model to screen watchlisted equities for discounts.')

    user_discount_rate = discount_rate

    for equity in equities:
        spot_price = services.get_daily_price_latest(ticker=equity)

        if user_discount_rate is None:
            discount_rate = cost_of_equity(ticker=equity)
        else:
            discount_rate = user_discount_rate

        if model == MODEL_DDM:
            dividends = services.get_dividend_history(equity)
            logger.debug(f'Passing discount rate = {discount_rate}')
            model_price = Cashflow(sample=dividends, discount_rate=discount_rate).calculate_net_present_value()
        
        if not model_price:
            logger.info(f'Net present value of dividend payments cannot be calculated for {equity}.')
        else:
            logger.verbose(f'{equity} spot price = {spot_price}, {equity} {model} price = {model_price}')

            discount = float(model_price) - float(spot_price)
                        
            if discount > 0:
                discount_result = {}
                discount_result['spot_price'] = spot_price
                discount_result['model_price'] = model_price
                discount_result['discount'] = discount
                discounts[equity] = discount_result
                logger.debug(f'Discount of {discount} found for {equity}')

    return discounts