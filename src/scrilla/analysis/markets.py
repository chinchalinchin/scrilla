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
"""
A module of functions that calculate financial statistics.
"""
import datetime
from typing import Dict, Union
from datetime import date
from scrilla import settings, services, files, cache, errors
from scrilla.static import keys
from scrilla.analysis.objects.cashflow import Cashflow
import scrilla.analysis.models.geometric.statistics as statistics
import scrilla.util.outputter as outputter

logger = outputter.Logger('scrilla.analysis.markets', settings.LOG_LEVEL)
profile_cache = cache.ProfileCache()


def sharpe_ratio(ticker: str, start_date: Union[date, None] = None, end_date: Union[date, None] = None, risk_free_rate: Union[float, None] = None, ticker_profile: Union[dict, None] = None, method: str = settings.ESTIMATION_METHOD) -> float:
    """
    Calculates the sharpe ratio for the supplied ticker over the specified time range. If no start and end date are supplied, calculation will default to the last 100 days of prices. The risk free rate and ticker risk profile can be passed in to force calculations without historical data.

    Parameters
    ----------
    1. **ticker**: ``str``
        A string of the ticker symbol whose sharpe ratio will be computed.
    2. **start_date**: ``datetime.date``
        Start date of the time period for which the sharpe ratio will be computed.
    3. **end_date**: ``datetime.date``
        End_date of the time period for which the sharpe ratio will be computed.
    4. **risk_free_rate**: ``float``
        Risk free rate used to evaluate excess return. Defaults to settings.RISK_FREE_RATE.
    5. **ticker_profile**: ``dict`` 
        Risk-return profile for the supplied ticker. Formatted as follows: `{ 'annual_return': float, 'annual_volatility': float } `
    6. **method** : ``str``
        Estimation method used to calculate financial statistics. Defaults to the value set by `scrilla.settings.ESTIMATION_METHOD`. Allowable value are accessible through the `scrilla.keys.keys` dictionary.

    .. notes:: 
        * if ``ticker_profile`` is provided, this function will skip both an external data service call and the calculation of the ticker's risk profile. The calculation will proceed as if the supplied profile were the true profile. If ``ticker_profile`` is not provided, all statistics will be estimated from historical data.
    """
    start_date, end_date = errors.validate_dates(start_date=start_date, end_date=end_date,
                                                 asset_type=keys.keys['ASSETS']['EQUITY'])

    if ticker_profile is None:
        result = profile_cache.filter_profile_cache(
            ticker=ticker, start_date=start_date, end_date=end_date, method=method)

        if result is not None and result[keys.keys['STATISTICS']['SHARPE']] is not None:
            return result[keys.keys['STATISTICS']['SHARPE']]

        ticker_profile = statistics.calculate_risk_return(
            ticker=ticker, start_date=start_date, end_date=end_date, method=method)

    if risk_free_rate is None:
        risk_free_rate = services.get_risk_free_rate()

    sh_ratio = (ticker_profile['annual_return'] -
                risk_free_rate)/ticker_profile['annual_volatility']

    profile_cache.save_or_update_row(ticker=ticker, start_date=start_date,
                                     end_date=end_date, sharpe_ratio=sh_ratio, method=method)

    return sh_ratio

# if no dates are specified, defaults to last 100 days


def market_premium(start_date: Union[date, None] = None, end_date: Union[date, None] = None, market_profile: Union[dict, None] = None, method: str = settings.ESTIMATION_METHOD) -> float:
    """
    Returns the excess of the market return defined by the environment variable `MARKET_PROXY` over the risk free rate defined by the `RISK_FREE` environment variable.

    Parameters
    ----------
    1. **start_date**: ``datetime.date``
        Start date of the time period for which the market premium will be computed.
    2. **end_date**: ``datetime.date``
        End_date of the time period for which the market premium will be computed.
    3. **market_profile**: ``dict``
    4. **method** : ``str``
        Estimation method used to calculate financial statistics. Defaults to the value set by `scrilla.settings.ESTIMATION_METHOD`. Allowable value are accessible through the `scrilla.keys.keys` dictionary.

    """
    start_date, end_date = errors.validate_dates(start_date=start_date, end_date=end_date,
                                                 asset_type=keys.keys['ASSETS']['EQUITY'])

    if market_profile is None:
        market_profile = statistics.calculate_risk_return(
            ticker=settings.MARKET_PROXY, start_date=start_date, end_date=end_date, method=method)

    market_prem = (
        market_profile['annual_return'] - services.get_risk_free_rate())
    return market_prem


def market_beta(ticker: str, start_date: Union[date, None] = None, end_date: Union[date, None] = None, market_profile: Union[dict, None] = None, market_correlation: Union[dict, None] = None, ticker_profile: Union[dict, None] = None, sample_prices: Union[dict, None] = None, method: str = settings.ESTIMATION_METHOD) -> float:
    """
    Returns the beta of an asset against the market return defined by the ticker symbol set `scrilla.settings.MARKET_PROXY`, which in turn is configured through the environment variable of the same name, `MARKET_PROXY`. 

    Parameters
    ----------
    1. **ticker**: ``str``
        A string of the ticker symbol whose asset beta will be computed.
    2. **start_date**: ``datetime.date``
        Start date of the time period for which the asset beta will be computed.
    3. **end_date**: ``datetime.date`` 
        End_date of the time period for which the asset beta will be computed.
    4. **method** : ``str``
        Estimation method used to calculate financial statistics. Defaults to the value set by `scrilla.settings.ESTIMATION_METHOD`. Allowable value are accessible through the `scrilla.keys.keys` dictionary.

    .. notes::
        * If not configured by an environment variable, `scrilla.settings.MARKET_PROXY` defaults to ``SPY``, the ETF tracking the *S&P500*.
    """
    start_date, end_date = errors.validate_dates(start_date=start_date, end_date=end_date,
                                                 asset_type=keys.keys['ASSETS']['EQUITY'])

    result = profile_cache.filter_profile_cache(
        ticker=ticker, start_date=start_date, end_date=end_date, method=method)

    if result is not None and result[keys.keys['STATISTICS']['BETA']] is not None:
        return result[keys.keys['STATISTICS']['BETA']]

    if market_profile is None:
        if sample_prices is None:
            market_profile = statistics.calculate_risk_return(ticker=settings.MARKET_PROXY, start_date=start_date,
                                                              end_date=end_date, method=method)
        else:
            market_profile = statistics.calculate_risk_return(ticker=settings.MARKET_PROXY, method=method,
                                                              sample_prices=sample_prices[settings.MARKET_PROXY])
    if ticker_profile is None:
        if sample_prices is None:
            ticker_profile = statistics.calculate_risk_return(ticker=ticker, start_date=start_date,
                                                              end_date=end_date, method=method)
        else:
            ticker_profile = statistics.calculate_risk_return(ticker=ticker, method=method,
                                                              sample_prices=sample_prices[ticker])

    market_covariance = statistics.calculate_return_covariance(ticker_1=ticker, ticker_2=settings.MARKET_PROXY,
                                                               profile_1=ticker_profile, profile_2=market_profile,
                                                               correlation=market_correlation,
                                                               sample_prices=sample_prices,
                                                               start_date=start_date, end_date=end_date)

    beta = market_covariance / (market_profile['annual_volatility']**2)

    profile_cache.save_or_update_row(
        ticker=ticker, start_date=start_date, end_date=end_date, asset_beta=beta, method=method)

    return beta


def cost_of_equity(ticker: str, start_date: Union[datetime.date, None] = None, end_date: Union[datetime.date, None] = None, market_profile: Union[Dict[str, float], None] = None, market_correlation: Union[Dict[str, float], None] = None, method=settings.ESTIMATION_METHOD) -> float:
    """
    Returns the cost of equity of an asset as estimated by the Capital Asset Pricing Model, i.e. the product of the market premium and asset beta increased by the risk free rate.

    Parameters
    ----------
    1. **ticker**: ``str``
        A string of the ticker symbol whose cost of equity ratio will be computed.
    2. **start_date**: ``Union[datetime.date, None]``
        *Optional*. Start date of the time period for which the cost of equity ratio will be computed
    3. **end_date**: ``Union[datetime.date, None]``
        *Optional.* End_date of the time period for which the cost of equity ratio will be computed.
    4. **market_profile**: ``Union[Dict[str, float], None]``
        *Optional*. Dictionary containing the assumed risk profile for the market proxy. Overrides calls to services and staistical methods, forcing the calculation fo the cost of equity with the inputted market profile. Format: ``{ 'annual_return': value, 'annual_volatility': value}``
    5. **market_correlation**: ``Union[Dict[str, float], None]``
        *Optional*. Dictionary containing the assumed correlation for the calculation. Overrides calls to services and statistical methods, forcing the calculation of the cost of equity with the inputted correlation. Format: ``{ 'correlation' : value }``
    6. **method** : ``str``
        *Optional*. Estimation method used to calculate financial statistics. Defaults to the value set by `scrilla.settings.ESTIMATION_METHOD`. Allowable value are accessible through the `scrilla.keys.keys` dictionary.
    """
    start_date, end_date = errors.validate_dates(start_date=start_date, end_date=end_date,
                                                 asset_type=keys.keys['ASSETS']['EQUITY'])

    result = profile_cache.filter_profile_cache(
        ticker=ticker, start_date=start_date, end_date=end_date, method=method)

    if result is not None and result[keys.keys['STATISTICS']['EQUITY']] is not None:
        return result[keys.keys['STATISTICS']['EQUITY']]

    beta = market_beta(ticker=ticker, start_date=start_date, end_date=end_date,
                       market_profile=market_profile, market_correlation=market_correlation,
                       method=method)
    premium = market_premium(start_date=start_date, end_date=end_date,
                             market_profile=market_profile, method=method)

    equity_cost = (premium*beta + services.get_risk_free_rate())

    profile_cache.save_or_update_row(
        ticker=ticker, start_date=start_date, end_date=end_date, equity_cost=equity_cost, method=method)
    return equity_cost


def screen_for_discount(model: str = keys.keys['MODELS']['DDM'], discount_rate: float = None) -> Dict[str, Dict[str, float]]:
    """
    Screens the stocks saved under the user watchlist in the `scrilla.settings.COMMON_DIR` directory for discounts relative to the model inputted into the function.

    Parameters
    ----------
    1. **model** : ``str``
        *Optional*. Model used to evaluated the equities saved in the watchlist. If no model is specified, the function will default to the discount dividend model. Model constants are accessible through the the `scrilla.keys.keys` dictionary.
    2. **discount_rate** : ``float``
        *Optional*. Rate used to discount future cashflows to present. Defaults to an equity's CAPM cost of equity, as calculated by `scrilla.analysis.markets.cost_of_equity`.

    Returns
    -------
    ``dict``
        A list of tickers that trade at a discount relative to the model price, formatted as follows: `{ 'ticker' : { 'spot_price': value, 'model_price': value,'discount': value }, ... }`
    """

    equities = list(files.get_watchlist())
    discounts = {}
    user_discount_rate = discount_rate

    for equity in equities:
        spot_price = services.get_daily_price_latest(ticker=equity)

        if user_discount_rate is None:
            discount_rate = cost_of_equity(ticker=equity)
        else:
            discount_rate = user_discount_rate

        if model == keys.keys['MODELS']['DDM']:
            logger.debug(
                'Using Discount Dividend Model to screen watchlisted equities for discounts.')
            dividends = services.get_dividend_history(equity)
            model_price = Cashflow(
                sample=dividends, discount_rate=discount_rate).calculate_net_present_value()
            discount = float(model_price) - float(spot_price)

            if discount > 0:
                discount_result = {}
                discount_result['spot_price'] = spot_price
                discount_result['model_price'] = model_price
                discount_result['discount'] = discount
                discounts[equity] = discount_result
                logger.debug(f'Discount of {discount} found for {equity}')

    return discounts
