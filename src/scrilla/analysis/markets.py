# This file is part of scrilla: https://github.com/chinchalinchin/scrilla.

# scrilla is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 3
# as published by the Free Software Foundation.

# scrilla is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with scrilla.  If not, see <https://www.gnu.org/licenses/>
# or <https://github.com/chinchalinchin/scrilla/blob/develop/main/LICENSE>.

from scrilla import settings, services, files, cache, static, errors
from scrilla.analysis.objects.cashflow import Cashflow
import scrilla.analysis.models.geometric.statistics as statistics
import scrilla.util.outputter as outputter

MODEL_DDM="ddm"
# TODO: implement dcf model
MODEL_DCF="dcf"

logger = outputter.Logger('markets', settings.LOG_LEVEL)
profile_cache = cache.ProfileCache()

# NOTE: if ticker_profile is provided, it effectively nullifies start_date and end_date.
# TODO: pass in risk_free_rate=None as optional argument to prevent overusing services
def sharpe_ratio(ticker, start_date=None, end_date=None, risk_free_rate=None, ticker_profile=None, method=settings.ESTIMATION_METHOD):
    """
    Description
    -----------
    Returns the value of the sharpe ratio for the supplied ticker over the specified time range. If no start and end date are supplied, calculation will default to the last 100 days of prices. The risk_free_rate and ticker_profile can be provided to avoid excessive service calls. \n \n 

    Parameters
    ----------
    1. ticker : str \n
        A string of the ticker symbol whose sharpe ratio will be computed. \n \n

    2. start_date : datetime.date \n 
        Start date of the time period for which the sharpe ratio will be computed. \n \n 

    3. end_date : datetime.date \n 
        End_date of the time period for which the sharpe ratio will be computed. \n \n

    4. risk_free_rate : float \n
        Risk free rate used to evaluate excess return. Defaults to settings.RISK_FREE_RATE. \n \n

    5. ticker_profile : dict{ { 'annual_return': float, 'annual_volatility': float } }
        Risk-return profile for the supplied ticker. If provided, start_date and end_date are ignored and the values in ticker_profile are used to calculate the Sharpe ratio.

    """
    try:
        start_date, end_date = errors.validate_dates(start_date=start_date, end_date=end_date, 
                                                        asset_type=static.keys['ASSETS']['EQUITY'])
    except errors.InputValidationError as ive:
        raise ive

    result = profile_cache.filter_profile_cache(ticker=ticker, start_date=start_date, end_date=end_date, method=method)

    if result is not None and result[static.keys['STATISTICS']['SHARPE']] is not None:
        return result[static.keys['STATISTICS']['SHARPE']]

    if ticker_profile is None:  
        ticker_profile = statistics.calculate_risk_return(ticker=ticker, start_date=start_date, end_date=end_date, method=method)

    if risk_free_rate is None:
        risk_free_rate = services.get_risk_free_rate()

    sharpe_ratio = (ticker_profile['annual_return'] - risk_free_rate)/ticker_profile['annual_volatility']

    profile_cache.save_or_update_row(ticker=ticker, start_date=start_date,
                                        end_date=end_date,sharpe_ratio=sharpe_ratio, method=method)

    return sharpe_ratio

# if no dates are specified, defaults to last 100 days
def market_premium(start_date=None, end_date=None, market_profile = None, method=settings.ESTIMATION_METHOD):
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

    Raises
    ------
    1. errors.InputValidationError \n
    2. errors.SampleSizeError \n
    3. errors.PriceError \n
    4. errors.APIResponseError \n
    """
    try:
        start_date, end_date = errors.validate_dates(start_date=start_date, end_date=end_date, 
                                                        asset_type=static.keys['ASSETS']['EQUITY'])
    except errors.InputValidationError as ive:
        raise ive

    if market_profile is None:
        try:
            market_profile = statistics.calculate_risk_return(ticker=settings.MARKET_PROXY, start_date=start_date, end_date=end_date, method=method)
        except errors.SampleSizeError as se:
            raise se
        except errors.PriceError as pe:
            raise pe
        except errors.APIResponseError as api:
            raise api
    
    market_premium = (market_profile['annual_return'] - services.get_risk_free_rate())
    return market_premium
        

def market_beta(ticker, start_date=None, end_date=None, market_profile=None, market_correlation=None, ticker_profile=None, sample_prices=None, method=settings.ESTIMATION_METHOD):
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

    Raises  
    ------
    1. errors.InputValidationError \n
    2. errors.SampleSizeError \n
    3. errors.PriceError \n
    4. errors.APIResponseError \n
    """
    try:
        start_date, end_date = errors.validate_dates(start_date=start_date, end_date=end_date, 
                                                        asset_type=static.keys['ASSETS']['EQUITY'])
    except errors.InputValidationError as ive:
        raise ive

    result = profile_cache.filter_profile_cache(ticker=ticker, start_date=start_date, end_date=end_date, method=method)

    if result is not None and result[static.keys['STATISTICS']['BETA']] is not None:
        return result[static.keys['STATISTICS']['BETA']]

    try:
        if market_profile is None:
            if sample_prices is None:
                market_profile = statistics.calculate_risk_return(ticker=settings.MARKET_PROXY, start_date=start_date, 
                                                        end_date=end_date, method=method)
            else:   
                market_profile = statistics.calculate_risk_return(ticker=settings.MARKET_PROXY, method=method,
                                                                sample_prices=sample_prices[settings.MARKET_PROXY])
        if ticker_profile is None:
            if sample_prices is None:
                ticker_profile = statistics.calculate_risk_return(ticker=ticker,start_date=start_date,
                                                        end_date=end_date, method=method)
            else:
                ticker_profile = statistics.calculate_risk_return(ticker=ticker, method=method,
                                                        sample_prices=sample_prices[ticker])

        market_covariance = statistics.calculate_return_covariance(ticker_1=ticker, ticker_2=settings.MARKET_PROXY,
                                                                    profile_1=ticker_profile, profile_2=market_profile,
                                                                    correlation = market_correlation,
                                                                    sample_prices=sample_prices,
                                                                    start_date=start_date, end_date=end_date)
    except errors.SampleSizeError as se:
        raise se
    except errors.PriceError as pe:
        raise pe
    except errors.APIResponseError as api:
        raise api

    beta = market_covariance / (market_profile['annual_volatility']**2)

    profile_cache.save_or_update_row(ticker=ticker, start_date=start_date, end_date=end_date, asset_beta=beta, method=method)

    return beta

def cost_of_equity(ticker, start_date=None, end_date=None, market_profile=None, market_correlation=None, method=settings.ESTIMATION_METHOD):
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
    try:
        start_date, end_date = errors.validate_dates(start_date=start_date, end_date=end_date, 
                                                        asset_type=static.keys['ASSETS']['EQUITY'])
    except errors.InputValidationError as ive:
        raise ive

    result = profile_cache.filter_profile_cache(ticker=ticker, start_date=start_date, end_date=end_date, method=method)

    if result is not None and result[static.keys['STATISTICS']['EQUITY']] is not None:
        return result[static.keys['STATISTICS']['EQUITY']]

    try:
        beta = market_beta(ticker=ticker, start_date=start_date, end_date=end_date,
                            market_profile=market_profile, market_correlation=market_correlation,
                            method=method)
        premium = market_premium(start_date=start_date, end_date=end_date, market_profile=market_profile, method=method)
    except errors.SampleSizeError as se:
        raise se
    except errors.PriceError as pe:
        raise pe
    except errors.APIResponseError as api:
        raise api

    equity_cost = (premium*beta + services.get_risk_free_rate())

    profile_cache.save_or_update_row(ticker=ticker, start_date=start_date, end_date=end_date, equity_cost=equity_cost, method=method)
    return equity_cost

def screen_for_discount(model=None, discount_rate=None):
    """
    Parameters
    ----------
    model : str \n
        Model used to value the equities saved in the watchlist. If no model is specified, the function will default to MODEL_DDM. Model constants are statically accessible through the ` settings` variables: MODEL_DDM (Discount Dividend Model), MODEL_DCF (Discounted Cash Flow Model, not yet implemented) \n \n

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