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

from datetime import timedelta, date
from itertools import groupby
import datetime
from typing import Dict, List, Union
from numpy import log, sqrt, inf
from scipy.stats import norm, multivariate_normal
from scipy.optimize import fsolve, least_squares

from scrilla import services, files, settings, errors, cache
from scrilla.static import keys, functions, constants
from scrilla.analysis import estimators
from scrilla.util import outputter, helper, dater

logger = outputter.Logger(
    'scrilla.analysis.models.geometric.statistics', settings.LOG_LEVEL)
profile_cache = cache.ProfileCache()
correlation_cache = cache.CorrelationCache()


def get_sample_of_returns(ticker: str, sample_prices: dict = None, start_date: Union[date, None] = None, end_date: Union[date, None] = None, asset_type: Union[str, None] = None, daily: bool = False) -> list:
    """
    Generates a list of logarithmic returns on the sample `prices`. Sample return is annualized.

    Parameters
    ----------
    2. **start_date** : ``datetime.date``
        *Optional*. Start date of the time period over which the risk-return profile is to be calculated. Defaults to `None`, in which case the calculation proceeds as if `start_date` were set to 100 trading days prior to `end_date`. If `get_asset_type(ticker)=scrilla.keys.keys['ASSETS']['CRYPTO']`, this means 100 days regardless. If `get_asset_type(ticker)=scrilla.keys.keys['ASSETS']['EQUITY']`, this excludes weekends and holidays and decrements the `end_date` by 100 trading days.
    3. **end_date** : ``datetime.date``
        *Optional*. End date of the time period over which the risk-return profile is to be calculated. Defaults to `None`, in which the calculation proceeds as if `end_date` were set to today. If the `get_asset_type(ticker)==keys.keys['ASSETS']['CRYPTO']` this means today regardless. If `get_asset_type(ticker)=keys.keys['ASSETS']['EQUITY']` this excludes holidays and weekends and sets the end date to the last valid trading date. 
    4. **sample_prices** : ``list``
        *Optional*. A list of the asset prices for which the risk profile will be calculated. Overrides calls to service and forces calculation of risk price for sample of prices supplied. Function will disregard `start_date` and `end_date` and use the first and last key as the latest and earliest date, respectively. In other words, the `sample_prices` dictionary must be ordered from latest to earliest. Format: `{ 'date_1' : { 'open' : number, 'close' : number}, 'date_2': { 'open': number, 'close': number} ... }`
    5. **asset_type** : ``str``
         *Optional*. Specify asset type to prevent overusing redundant calculations. Allowable values: `scrilla.keys.keys['ASSETS']['EQUITY']`, `scrilla.keys.keys['ASSETS']['CRYPTO']`

    .. notes::
        * the `trading_period` for a single asset can be determined from its `asset_type`...should i use a conditional and fork constants.constants['ONE_TRADING_DAY'] instead of passing it in?
    """
    asset_type = errors.validate_asset_type(ticker, asset_type)
    trading_period = functions.get_trading_period(asset_type)

    if sample_prices is None:
        logger.debug('No sample prices provided, calling service.')
        start_date, end_date = errors.validate_dates(
            start_date, end_date, asset_type)
        prices = services.get_daily_price_history(
            ticker=ticker, start_date=start_date, end_date=end_date, asset_type=asset_type)
    else:
        logger.debug(
            f'{ticker} sample prices provided, skipping service call.')
        prices = sample_prices

    today = False
    sample_of_returns = []
    trading_period = functions.get_trading_period(asset_type=asset_type)

    for this_date in prices:
        todays_price = prices[this_date][keys.keys['PRICES']['CLOSE']]

        if today:
            logger.verbose(
                f'{this_date}: (todays_price, tomorrows_price) = ({todays_price}, {tomorrows_price})')
            # NOTE: crypto prices may have weekends and holidays removed during correlation algorithm
            # so samples can be compared to equities, need to account for these dates by increasing
            # the time_delta by the number of missed days.
            if asset_type == keys.keys['ASSETS']['CRYPTO'] or \
                    (asset_type == keys.keys['ASSETS']['EQUITY'] and not dater.consecutive_trading_days(tomorrows_date, this_date)):
                time_delta = (dater.parse_date_string(
                    tomorrows_date) - dater.parse_date_string(this_date)).days
            else:
                time_delta = 1

            todays_return = log(float(tomorrows_price) /
                                float(todays_price))/(time_delta)

            if not daily:
                todays_return = todays_return/trading_period

            sample_of_returns.append(todays_return)
        else:
            today = True

        tomorrows_price = prices[this_date][keys.keys['PRICES']['CLOSE']]
        tomorrows_date = this_date

    return sample_of_returns


def calculate_moving_averages(tickers: list, start_date: Union[date, None] = None, end_date: Union[date, None] = None, sample_prices: Union[Dict[str, Dict[str, float]], None] = None) -> list:
    # TODO: i need to redo this. this is needlessly inefficient. mean telescopes when
    #       calculating with moments. don't need to sum everything.
    # TODO: calculate moving averages with different estimation techniques.
    # TODO: simple moving averages vs exponential moving averages, etc.
    """
    Parameters
    ----------
    1. **tickers** : ``list``.
        array of ticker symbols correspond to the moving averages to be calculated. 
    2. **start_date** : ``datetime.date``
        *Optional*. Defaults to `None`. Start date of the time period over which the moving averages will be calculated.
    3. **end_date**: ``datetime.date``
        *Optional*. Defaults to `None`. End date of the time period over which the moving averages will be calculated. 
    4. **sample_prices** : ``dict``
        *Optional*. Defaults to `None`. A list of the asset prices for which moving_averages will be calculated. Overrides calls to service for sample prices. Function will disregard `start_date` and `end_date` if `sample_price` is specified. Must be of the format: `{'ticker_1': { 'date_1' : 'price_1', 'date_2': 'price_2'... }, 'ticker_2': { 'date_1' : 'price_1:, ... } }` and ordered from latest date to earliest date.

    Output
    ------
    ``(averages : dict, dates : list)``
    averages is a 3-node list with the following format `averages[ticker][period][date]` and dates is a list of dates between the `start_date` and `end_date`, inclusive.

    .. notes::
        * assumes `sample_prices` is ordered from latest to earliest date. 
        * If no start_date and end_date passed in, static snapshot of moving averages, i.e. the moving averages as of today (or last close), are calculated and returned.
        * If asset types are mixed, then the sample from which the average is calculated only consists of prices on business days. In other words, since crypto trades on weekends, to compare the moving average of equities and crypto, the moving average is only returned for business days. The moving average of crypto is still calculated using weekend price data, i.e. the moving average on Monday contains information about the moving average on Sunday, but the moving average on Sunday is discarded from the returned data, due to the fact equities are not traded on weekends. 
    """
    # MOVING AVERAGE OVER DATE RANGE LOOP CALCULATION PSEUDO-CODE
    #       1. for start date to end date:
    #            2. get today's price
    #            3. calculate today's return
    #            4. for all elements of MAs_n
    #                5. if today's date is less than a MA_n period away from the date of this MAs_n element
    #                    6. add today's return / MA_n_PERIOD to this element of MAs_n
    #                    7. create today's MAs_n element

    moving_averages = []

    ##########################################
    # Moving Average Snapshot On Single Date
    if start_date is None and end_date is None:
        for ticker in tickers:
            logger.debug(f'Calculating Moving Average for {ticker}')

            if sample_prices is None:
                prices = services.get_daily_price_history(ticker)
            else:
                prices = sample_prices[ticker]

            if not prices:
                raise errors.PriceError(
                    f'Prices could not be retrieved for {ticker}')

            asset_type = files.get_asset_type(ticker)
            trading_period = functions.get_trading_period(asset_type)

            today = False
            count, tomorrows_price, MA_1, MA_2, MA_3 = 1, 0, 0, 0, 0

            for this_date in prices:
                todays_price = prices[this_date][keys.keys['PRICES']['CLOSE']]
                if today:
                    todays_return = log(
                        float(tomorrows_price) / float(todays_price))/trading_period
                    logger.verbose(
                        f'todays_return == {tomorrows_price}/({todays_price}*{round(trading_period,2)}) = {todays_return}')

                    if count < settings.MA_1_PERIOD:
                        MA_1 += todays_return / settings.MA_1_PERIOD

                    if count < settings.MA_2_PERIOD:
                        MA_2 += todays_return / settings.MA_2_PERIOD

                    if count < settings.MA_3_PERIOD:
                        MA_3 += todays_return / settings.MA_3_PERIOD
                        count += 1

                else:
                    today = True

                tomorrows_price = prices[this_date][keys.keys['PRICES']['CLOSE']]

            logger.verbose(
                f'(MA_1, MA_2, MA_3)_{ticker} = ({MA_1}, {MA_2}, {MA_3}')
            moving_averages.append([MA_1, MA_2, MA_3])

        return moving_averages, None

    ################################################
    # Moving Average Scatter Plot Over Date Range

    # TODO: this needs work. needs the intersect_dict_keys method like correlation did.

    previous_asset_type, portfolio_asset_type = None, None
    mixed_flag = False
    original_day_count = 0

    ### START ARGUMENT VALIDATION ###
    logger.debug('Checking provided tickers for mixed asset types.')
    for ticker in tickers:
        asset_type = files.get_asset_type(ticker)
        portfolio_asset_type = asset_type
        if (
            previous_asset_type is not None
            and previous_asset_type != asset_type
        ):
            logger.debug(
                'Tickers include mixed asset types, flagging calculation.')
            portfolio_asset_type = None
            mixed_flag = True
            break
        previous_asset_type = asset_type

    if not mixed_flag:
        logger.debug(
            f'Tickers provided all of {portfolio_asset_type} asset type.')

    logger.debug('Calculating length of date range in trading days.')
    if mixed_flag:
        original_day_count = dater.business_days_between(start_date, end_date)
    elif portfolio_asset_type == keys.keys['ASSETS']['EQUITY']:
        original_day_count = dater.business_days_between(start_date, end_date)
    elif portfolio_asset_type == keys.keys['ASSETS']['CRYPTO']:
        original_day_count = (end_date - start_date).days
    else:
        original_day_count = dater.business_days_between(start_date, end_date)

    logger.debug(
        f'{end_date} - {start_date} = {original_day_count} trading days')

    for ticker in tickers:
        logger.debug(f'Calculating Moving Average for {ticker}.')

        asset_type = files.get_asset_type(ticker)
        trading_period = functions.get_trading_period(asset_type)

        logger.debug(
            'Offsetting start date to account for longest Moving Average period.')
        if asset_type == keys.keys['ASSETS']['CRYPTO']:
            logger.debug(f'{ticker}_asset_type = Crypto')

            logger.debug(
                'Configuring date variables to account for all dates.')
            new_start_date = start_date - timedelta(days=settings.MA_3_PERIOD)
            new_day_count = (end_date - new_start_date).days

            # amend equity trading dates to take account of weekends
        elif asset_type == keys.keys['ASSETS']['EQUITY']:
            logger.debug(f'{ticker}_asset_type = Equity')

            logger.debug(
                'Configuring date variables to account for weekends and holidays.')
            new_start_date = dater.decrement_date_by_business_days(start_date=start_date,
                                                                   business_days=settings.MA_3_PERIOD)
            new_day_count = dater.business_days_between(
                new_start_date, end_date)

        else:
            logger.debug(
                f'{ticker}_asset_type = Unknown; Defaulting to business dates')

            logger.debug(
                'Configuring date variables to account for weekends and holidays.')
            new_start_date = dater.decrement_date_by_business_days(start_date=start_date,
                                                                   business_days=settings.MA_3_PERIOD)
            new_day_count = dater.business_days_between(
                new_start_date, end_date)

        logger.debug(
            f'start_date -> new_start_date == {start_date} -> {new_start_date}')
        logger.debug(f'{end_date} - {new_start_date} == {new_day_count}')

        if sample_prices is None:
            logger.debug(
                f'No {ticker} sample prices provided, calling service.')
            prices = services.get_daily_price_history(
                ticker, new_start_date, end_date)
        else:
            logger.debug(
                f'{ticker} sample prices provided, skipping service call.')
            prices = sample_prices[ticker]

        if not prices:
            raise errors.PriceError(
                f'Prices could not be retrieved for {ticker}')
    ### END ARGUMENT VALIDATION ###

    ### START MOVING AVERAGE CALCULATION ###
        today = False
        count = 1
        tomorrows_price = 0
        MAs_1, MAs_2, MAs_3 = [], [], []

        # See NOTE #4
        for this_date in prices:
            logger.verbose(f'date: {this_date}')
            # todays_price = services.price_manager.parse_price_from_date(prices, date, asset_type)
            todays_price = prices[this_date][keys.keys['PRICES']['CLOSE']]

            if today:
                todays_return = log(float(tomorrows_price) /
                                    float(todays_price))/trading_period
                logger.verbose(
                    f'todays_return == ln({tomorrows_price}/{todays_price})/{round(trading_period,4)}) = {round(todays_return,4)}')

                for MA in MAs_1:
                    end_flag = False
                    if len(MAs_1) - MAs_1.index(MA) < settings.MA_1_PERIOD:
                        if len(MAs_1) - MAs_1.index(MA) == settings.MA_1_PERIOD - 1:
                            end_flag = True
                            if asset_type == keys.keys['ASSETS']['EQUITY']:
                                date_of_MA1 = dater.decrement_date_string_by_business_days(
                                    this_date, MAs_1.index(MA))
                            elif asset_type == keys.keys['ASSETS']['CRYPTO']:
                                date_of_MA1 = dater.string_to_date(
                                    this_date) - timedelta(days=MAs_1.index(MA))
                            else:
                                date_of_MA1 = dater.string_to_date(
                                    this_date) - timedelta(days=MAs_1.index(MA))

                        MA += todays_return / settings.MA_1_PERIOD

                        if end_flag:
                            logger.verbose(
                                f'{ticker}_MA_1({date_of_MA1}) = {MA}')

                # See NOTE #3
                if mixed_flag or portfolio_asset_type == keys.keys['ASSETS']['EQUITY']:
                    if not(dater.is_date_string_holiday(this_date) or dater.is_date_string_weekend(this_date)):
                        MAs_1.append((todays_return / settings.MA_1_PERIOD))
                elif portfolio_asset_type == keys.keys['ASSETS']['CRYPTO']:
                    MAs_1.append((todays_return / settings.MA_1_PERIOD))

                for MA in MAs_2:
                    end_flag = False
                    if len(MAs_2) - MAs_2.index(MA) < settings.MA_2_PERIOD:
                        if len(MAs_2) - MAs_2.index(MA) == settings.MA_2_PERIOD - 1:
                            end_flag = True
                            if asset_type == keys.keys['ASSETS']['EQUITY']:
                                date_of_MA2 = dater.decrement_date_string_by_business_days(
                                    this_date, MAs_2.index(MA))
                            elif asset_type == keys.keys['ASSETS']['CRYPTO']:
                                date_of_MA2 = dater.string_to_date(
                                    this_date) + timedelta(days=MAs_2.index(MA))
                            else:
                                date_of_MA2 = dater.string_to_date(
                                    this_date) + timedelta(days=MAs_2.index(MA))

                        MA += todays_return / settings.MA_2_PERIOD

                        if end_flag:
                            logger.verbose(
                                f'{ticker}_MA_2({date_of_MA2}) = {MA}')

                # See NOTE #3
                if mixed_flag or portfolio_asset_type == keys.keys['ASSETS']['EQUITY']:
                    if not(dater.is_date_string_holiday(this_date) or dater.is_date_string_weekend(this_date)):
                        MAs_2.append((todays_return / settings.MA_2_PERIOD))
                elif portfolio_asset_type == keys.keys['ASSETS']['CRYPTO']:
                    MAs_2.append((todays_return / settings.MA_2_PERIOD))

                for MA in MAs_3:
                    end_flag = False
                    if len(MAs_3) - MAs_3.index(MA) < settings.MA_3_PERIOD:
                        if len(MAs_3) - MAs_3.index(MA) == settings.MA_3_PERIOD - 1:
                            end_flag = True
                            if asset_type == keys.keys['ASSETS']['EQUITY']:
                                date_of_MA3 = dater.decrement_date_string_by_business_days(
                                    this_date, MAs_3.index(MA))
                            elif asset_type == keys.keys['ASSETS']['CRYPTO']:
                                date_of_MA3 = dater.string_to_date(
                                    this_date) + timedelta(days=MAs_3.index(MA))
                            else:
                                date_of_MA3 = dater.string_to_date(
                                    this_date) + timedelta(days=MAs_3.index(MA))

                        MA += todays_return / settings.MA_3_PERIOD

                        if end_flag:
                            logger.verbose(
                                f'{ticker}_MA_3({date_of_MA3}) = {MA}')

                # See NOTE #3
                if mixed_flag or portfolio_asset_type == keys.keys['ASSETS']['EQUITY']:
                    if not(dater.is_date_string_holiday(this_date) or dater.is_date_string_weekend(this_date)):
                        MAs_3.append((todays_return / settings.MA_3_PERIOD))
                elif portfolio_asset_type == keys.keys['ASSETS']['CRYPTO']:
                    MAs_3.append((todays_return / settings))

            else:
                today = True

            # tomorrows_price = services.price_manager.parse_price_from_date(prices, date, asset_type)
            tomorrows_price = prices[this_date][keys.keys['PRICES']['CLOSE']]

        MAs_1 = MAs_1[:original_day_count]
        MAs_2 = MAs_2[:original_day_count]
        MAs_3 = MAs_3[:original_day_count]

        moving_averages.append([MAs_1, MAs_2, MAs_3])

    ### END MOVING AVERAGE CALCULATION ###

    ### START RESPONSE FORMATTING ###
    if not mixed_flag:
        if portfolio_asset_type == keys.keys['ASSETS']['EQUITY']:
            dates_between = dater.business_dates_between(start_date, end_date)
        elif portfolio_asset_type == keys.keys['ASSETS']['CRYPTO']:
            dates_between = dater.dates_between(start_date, end_date)
        else:
            dates_between = dater.business_dates_between(start_date, end_date)
    else:
        dates_between = dater.business_dates_between(start_date, end_date)

    logger.debug(
        'If everything is correct, then len(moving_averages[0][1]) == len(dates_between)')
    if len(moving_averages[0][1]) == len(dates_between):
        logger.debug("Your program rules.")
        logger.debug('{} = {}'.format(
            len(moving_averages[0][1]), len(dates_between)))
    else:
        logger.debug("Your program sucks.")
        logger.debug('{} != {}'.format(
            len(moving_averages[0][1]), len(dates_between)))

    ### END RESPONSE FORMATTING ###
    return moving_averages, dates_between


def calculate_risk_return(ticker: str, start_date: Union[date, None] = None, end_date: Union[date, None] = None, sample_prices: Union[Dict[str, Dict[str, float]], None] = None, asset_type: Union[str, None] = None, weekends: Union[int, None] = None, method: str = settings.ESTIMATION_METHOD) -> Dict[str, float]:
    if method == keys.keys['ESTIMATION']['MOMENT']:
        return calculate_moment_risk_return(ticker=ticker,
                                            start_date=start_date,
                                            end_date=end_date,
                                            sample_prices=sample_prices,
                                            asset_type=asset_type,
                                            weekends=weekends)
    if method == keys.keys['ESTIMATION']['PERCENT']:
        return calculate_percentile_risk_return(ticker=ticker,
                                                start_date=start_date,
                                                end_date=end_date,
                                                sample_prices=sample_prices,
                                                asset_type=asset_type,
                                                weekends=weekends)
    if method == keys.keys['ESTIMATION']['LIKE']:
        return calculate_likelihood_risk_return(ticker=ticker,
                                                start_date=start_date,
                                                end_date=end_date,
                                                sample_prices=sample_prices,
                                                asset_type=asset_type,
                                                weekends=weekends)
    raise errors.ConfigurationError('Statistic estimation method not found')


def calculate_likelihood_risk_return(ticker, start_date: Union[date, None] = None, end_date: Union[date, None] = None, sample_prices: Union[dict, None] = None, asset_type: Union[str, None] = None, weekends: Union[int, None] = None) -> Dict[str, float]:
    """
    Estimates the mean rate of return and volatility for a sample of asset prices as if the asset price followed a Geometric Brownian Motion process, i.e. the mean rate of return and volatility are constant and not functions of time or the asset price. Moreover, the return and volatility are estimated using the method of maximum likelihood estimation. The probability of each observation is calculated and then the product is taken to find the probability of the intersection; this probability is maximized with respect to the parameters of the normal distribution, the mean and the volatility.

    Parameters
    ----------
    1. **ticker** : ``str``
        Ticker symbol whose risk-return profile is to be calculated.
    2. **start_date** : ``datetime.date``
        Optional. Start date of the time period over which the risk-return profile is to be calculated. Defaults to `None`, in which case the calculation proceeds as if `start_date` were set to 100 trading days prior to `end_date`. If `get_asset_type(ticker)=scrilla.keys.keys['ASSETS']['CRYPTO']`, this means 100 days regardless. If `get_asset_type(ticker)=scrilla.keys.keys['ASSETS']['EQUITY']`, this excludes weekends and holidays and decrements the `end_date` by 100 trading days.
    3. **end_date** : ``datetime.date``
        *Optional*. End date of the time period over which the risk-return profile is to be calculated. Defaults to `None`, in which the calculation proceeds as if `end_date` were set to today. If the `get_asset_type(ticker)==keys.keys['ASSETS']['CRYPTO']` this means today regardless. If `get_asset_type(ticker)=keys.keys['ASSETS']['EQUITY']` this excludes holidays and weekends and sets the end date to the last valid trading date. 
    4. **sample_prices** : ``list``
        *Optional*. A list of the asset prices for which the risk profile will be calculated. Overrides calls to service and forces calculation of risk price for sample of prices supplied. Function will disregard `start_date` and `end_date` and use the first and last key as the latest and earliest date, respectively. In other words, the `sample_prices` dictionary must be ordered from latest to earliest. Format: `{ 'date_1' : { 'open' : number, 'close' : number}, 'date_2': { 'open': number, 'close': number} ... }`
    5. **asset_type** : ``str``
         *Optional*. Specify asset type to prevent overusing redundant calculations. Allowable values: `scrilla.keys.keys['ASSETS']['EQUITY']`, `scrilla.keys.keys['ASSETS']['CRYPTO']`

    Raises 
    ------
    1. **scrilla.errors.PriceError**
        If no price data is inputted into the function and the application cannot retrieve price data from the cache or external services, this error will be thrown.


    Returns
    ------
    ``Dict[str, float]``
        Dictionary containing the annualized return and volatility. Formatted as `{ 'annual_return' : float, 'annual_volatility': float }`

    .. notes::
        * assumes price history is ordered from latest to earliest date.
        * if the `sample_prices` dictionary is provided, the function will bypass the cache and the service call altogether. The function will assume `sample_prices` is the source of the truth.
    """
    from scrilla.analysis import optimizer

    asset_type = errors.validate_asset_type(ticker, asset_type)
    trading_period = functions.get_trading_period(asset_type)

    if weekends is None:
        if asset_type == keys.keys['ASSETS']['CRYPTO']:
            weekends = 1
        else:
            weekends = 0

    if sample_prices is None:
        start_date, end_date = errors.validate_dates(
            start_date, end_date, asset_type)
        results = profile_cache.filter_profile_cache(ticker=ticker, start_date=start_date, end_date=end_date,
                                                     method=keys.keys['ESTIMATION']['LIKE'])

        if results is not None \
                and results[keys.keys['STATISTICS']['RETURN']] is not None \
                and results[keys.keys['STATISTICS']['VOLATILITY']] is not None:
            return results

        logger.debug('No sample prices provided, calling service.')
        prices = services.get_daily_price_history(
            ticker=ticker, start_date=start_date, end_date=end_date, asset_type=asset_type)

        if asset_type == keys.keys['ASSETS']['CRYPTO'] and weekends == 0:
            logger.debug('Removing weekends from crypto sample')
            prices = dater.intersect_with_trading_dates(prices)

    else:
        logger.debug(
            f'{ticker} sample prices provided, skipping service call.')
        prices = sample_prices

    if not prices:
        raise errors.PriceError(f'No prices could be retrieved for {ticker}')

    sample_of_returns = get_sample_of_returns(
        ticker=ticker, sample_prices=prices, asset_type=asset_type)

    likelihood_estimates = optimizer.maximize_univariate_normal_likelihood(
        data=sample_of_returns)
    # See NOTE in docstring
    # NOTE: E(dln(S)/delta_t) = (mu - 0.5 * sigma ** 2) * delta_t / delta_t = mu - 0.5 * sigma ** 2
    # TODO: add :math to docstring with this
    # NOTE: Var(dln(S)/delta_t) = (1/delta_t**2)*Var(dlnS) = sigma**2*delta_t / delta_t**2 = sigma**2 / delta_t
    #       so need to multiply volatiliy by sqrt(delta_t) to get correct scale.
    vol = likelihood_estimates[1]*sqrt(trading_period)
    # ito's lemma
    mean = likelihood_estimates[0] + 0.5 * (vol ** 2)
    results = {
        keys.keys['STATISTICS']['RETURN']: mean,
        keys.keys['STATISTICS']['VOLATILITY']: vol
    }

    profile_cache.save_or_update_row(ticker=ticker, start_date=start_date, end_date=end_date,
                                     method=keys.keys['ESTIMATION']['LIKE'], weekends=weekends,
                                     annual_return=results[keys.keys['STATISTICS']['RETURN']],
                                     annual_volatility=results[keys.keys['STATISTICS']['VOLATILITY']])

    return results


def calculate_percentile_risk_return(ticker: str, start_date: Union[date, None] = None, end_date: Union[date, None] = None, sample_prices: Union[dict, None] = None, asset_type: Union[str, None] = None, weekends: Union[int, None] = None) -> Dict[str, float]:
    """
    Estimates the mean rate of return and volatility for a sample of asset prices as if the asset price followed a Geometric Brownian Motion process, i.e. the mean rate of return and volatility are constant and not functions of time or the asset price. Moreover, the return and volatility are estimated using the method of percentile matching, where the return and volatility are estimated by matching the 25th and 75th percentile calculated from the assumed GBM distribution to the sample of data.

    Parameters
    ----------
    1. **ticker** : ``str``
        Ticker symbol whose risk-return profile is to be calculated.
    2. **start_date** : ``datetime.date`` 
        *Optional*. Start date of the time period over which the risk-return profile is to be calculated. Defaults to `None`, in which case the calculation proceeds as if `start_date` were set to 100 trading days prior to `end_date`. If `get_asset_type(ticker)=scrilla.keys.keys['ASSETS']['CRYPTO']`, this means 100 days regardless. If `get_asset_type(ticker)=scrilla.keys.keys['ASSETS']['EQUITY']`, this excludes weekends and holidays and decrements the `end_date` by 100 trading days.
    3. **end_date** : ``datetime.date``
        *Optional*. End date of the time period over which the risk-return profile is to be calculated. Defaults to `None`, in which the calculation proceeds as if `end_date` were set to today. If the `get_asset_type(ticker)==keys.keys['ASSETS']['CRYPTO']` this means today regardless. If `get_asset_type(ticker)=keys.keys['ASSETS']['EQUITY']` this excludes holidays and weekends and sets the end date to the last valid trading date.
    4.**sample_prices** : ``dict``
        **Optional**. A list of the asset prices for which the correlation will be calculated. Overrides calls to service and forces calculation of correlation for sample of prices supplied. Function will disregard `start_date` and `end_date` and use the first and last key of the dictionary as the latest and earliest date, respectively. In other words, `sample_prices` must be ordered from latest to earliest. Must be formatted: `{ 'date_1' : { 'open' : float, 'close' : float}, 'date_2': { 'open': float, 'close': float } ... }`
    5. **asset_type** : ``str``
         Optional. Specify asset type to prevent overusing redundant calculations. Allowable values: scrilla.keys.keys['ASSETS']['EQUITY'], scrilla.keys.keys['ASSETS']['CRYPTO']

    Returns
    -------
    ``Dict[str, float]``
        Dictionary containing the annualized return and volatility. Formatted as `{ 'annual_return' : float, 'annual_volatility': float }`

    Raises 
    ------
    1. **scrilla.errors.PriceError**
        If no price data is inputted into the function and the application cannot retrieve price data from the cache or external services, this error will be thrown.

    .. notes::
        * assumes price history is ordered from latest to earliest date.
        * if the `sample_prices` dictionary is provided, the function will bypass the cache and the service call altogether. The function will assume `sample_prices` is the source of the truth.
    """
    asset_type = errors.validate_asset_type(ticker, asset_type)
    trading_period = functions.get_trading_period(asset_type)

    if weekends is None:
        if asset_type == keys.keys['ASSETS']['CRYPTO']:
            weekends = 1
        else:
            weekends = 0

    if sample_prices is None:
        if weekends == 1:
            start_date, end_date = errors.validate_dates(
                start_date, end_date, keys.keys['ASSETS']['CRYPTO'])
        else:
            start_date, end_date = errors.validate_dates(
                start_date, end_date, keys.keys['ASSETS']['EQUITY'])

        results = profile_cache.filter_profile_cache(ticker=ticker, start_date=start_date, end_date=end_date,
                                                     method=keys.keys['ESTIMATION']['PERCENT'],
                                                     weekends=weekends)

        if results is not None \
                and results[keys.keys['STATISTICS']['RETURN']] is not None \
                and results[keys.keys['STATISTICS']['VOLATILITY']] is not None:
            return results

        logger.debug('No sample prices provided, calling service.')
        prices = services.get_daily_price_history(
            ticker=ticker, start_date=start_date, end_date=end_date, asset_type=asset_type)

        if asset_type == keys.keys['ASSETS']['CRYPTO'] and weekends == 0:
            logger.debug('Removing weekends from crypto sample')
            prices = dater.intersect_with_trading_dates(prices)
    else:
        logger.debug(
            f'{ticker} sample prices provided, skipping service call.')
        prices = sample_prices

    if not prices:
        raise errors.PriceError(f'No prices could be retrieved for {ticker}')

    sample_of_returns = get_sample_of_returns(
        ticker=ticker, sample_prices=prices, asset_type=asset_type)

    first_quartile = estimators.sample_percentile(
        data=sample_of_returns, percentile=0.25)
    median = estimators.sample_percentile(
        data=sample_of_returns, percentile=0.50)
    third_quartile = estimators.sample_percentile(
        data=sample_of_returns, percentile=0.75)
    guess = (median, (third_quartile-first_quartile)/2)

    def objective(params):
        return [norm.cdf(x=first_quartile, loc=params[0], scale=params[1]) - 0.25,
                norm.cdf(x=third_quartile, loc=params[0], scale=params[1]) - 0.75]

    mean, vol = fsolve(objective, guess)

    # NOTE: Var(dln(S)/delta_t) = (1/delta_t^2)*Var(dlnS) = sigma^2*delta_t / delta_t^2 = sigma^2 / delta_t
    #       so need to multiply volatiliy by sqrt(delta_t) to get correct scale.
    vol = vol * sqrt(trading_period)
    # ito's lemma
    mean = mean + 0.5 * (vol ** 2)
    results = {
        keys.keys['STATISTICS']['RETURN']: mean,
        keys.keys['STATISTICS']['VOLATILITY']: vol
    }

    profile_cache.save_or_update_row(ticker=ticker, start_date=start_date, end_date=end_date,
                                     method=keys.keys['ESTIMATION']['PERCENT'], weekends=weekends,
                                     annual_return=results[keys.keys['STATISTICS']['RETURN']],
                                     annual_volatility=results[keys.keys['STATISTICS']['VOLATILITY']])
    return results


def calculate_moment_risk_return(ticker: str, start_date: Union[date, None] = None, end_date: Union[date, None] = None, sample_prices: Union[Dict[str, Dict[str, float]], None] = None, asset_type: Union[str, None] = None, weekends: Union[int, None] = None) -> Dict[str, float]:
    """
    Estimates the mean rate of return and volatility for a sample of asset prices as if the asset price followed a Geometric Brownian Motion process, i.e. the mean rate of return and volatility are constant and not functions of time or the asset price. Moreover, the return and volatility are estimated using the method of moment matching, where the return is estimated by equating it to the first moment of the sample and the volatility is estimated by equating it to the square root of the second moment of the sample.

    Parameters
    ----------
    1. **ticker** : ``str``
         Ticker symbol whose risk-return profile is to be calculated.
    2. **start_date** : ``Union[datetime.date, None]``
        *Optional*. Start date of the time period over which the risk-return profile is to be calculated. Defaults to `None`, in which case the calculation proceeds as if `start_date` were set to 100 trading days prior to `end_date`. If `get_asset_type(ticker)=scrilla.keys.keys['ASSETS']['CRYPTO']`, this means 100 days regardless.  If `get_asset_type(ticker)=scrilla.keys.keys['ASSETS']['EQUITY']`, this excludes weekends and holidays and decrements the `end_date` by 100 trading days.
    3. **end_date** : ``Union[datetime.date, None]`` 
        *Optional*. End date of the time period over which the risk-return profile is to be calculated. Defaults to `None`, in which the calculation proceeds as if `end_date` were set to today. If the `get_asset_type(ticker)==keys.keys['ASSETS']['CRYPTO']` this means today regardless. If `get_asset_type(ticker)=keys.keys['ASSETS']['EQUITY']` this excludes holidays and weekends and sets the end date to the last valid trading date. \n \n
    4. **sample_prices** : ``Union[Dict[str, Dict[str, float], None]`
        Optional. A list of the asset prices for which correlation will be calculated. Overrides calls to service and forces calculation of correlation for sample of prices supplied. Function will disregard `start_date` and `end_date` and use the first and last key as the latest and earliest date, respectively. In other words, the `sample_prices` dictionary must be ordered from latest to earliest. If this argument is supplied, the function will bypass calls to the cache for stored calculations. Format: `{ 'date_1' : { 'open' : number, 'close' : number}, 'date_2': { 'open': number, 'close': number} ... }`
    5. **asset_type** : ``Union[str, None]``
         *Optional*. Specify asset type to prevent overusing redundant calculations. Allowable values can be found in `scrilla.keys.keys['ASSETS']`
    6. **weekends**: ``Union[int, None]``

    Raises 
    ------
    1. **scrilla.errors.PriceError***
        If no price data is inputted into the function and the application cannot retrieve price data from the cache or external services, this error will be thrown.

    Returns 
    ------
    ``Dict[str, float]``
        Dictionary containing the annualized return and volatility. Formatted as `{ 'annual_return' : float, 'annual_volatility': float }`

    .. notes::
        * assumes price history is ordered from latest to earliest date.
        * function will bypass the cache if `sample_prices` is provided. In other words, the calculation can be forced by specifying `sample_prices`.
    """
    asset_type = errors.validate_asset_type(ticker, asset_type)
    trading_period = functions.get_trading_period(asset_type)

    if weekends is None:
        if asset_type == keys.keys['ASSETS']['CRYPTO']:
            weekends = 1
        else:
            weekends = 0

    if sample_prices is None:
        if weekends == 1:
            start_date, end_date = errors.validate_dates(
                start_date, end_date, keys.keys['ASSETS']['CRYPTO'])
        else:
            start_date, end_date = errors.validate_dates(
                start_date, end_date, keys.keys['ASSETS']['EQUITY'])

        results = profile_cache.filter_profile_cache(ticker=ticker, start_date=start_date, end_date=end_date,
                                                     method=keys.keys['ESTIMATION']['MOMENT'], weekends=weekends)

        if results is not None \
                and results[keys.keys['STATISTICS']['RETURN']] is not None \
                and results[keys.keys['STATISTICS']['VOLATILITY']] is not None:
            return results

        logger.debug('No sample prices provided, calling service.')
        prices = services.get_daily_price_history(
            ticker=ticker, start_date=start_date, end_date=end_date, asset_type=asset_type)

        if asset_type == keys.keys['ASSETS']['CRYPTO'] and weekends == 0:
            logger.debug('Removing weekends from crypto sample')
            prices = dater.intersect_with_trading_dates(prices)

    else:
        logger.debug(
            f'{ticker} sample prices provided, skipping service call.')
        prices = sample_prices

    if not prices:
        raise errors.PriceError(f'No prices could be retrieved for {ticker}')

    # Log of difference loses a sample
    sample = len(prices) - 1
    logger.debug(
        f'Calculating mean annual return over last {sample} days for {ticker}')

    # MEAN CALCULATION
    # NOTE: mean return is a telescoping series, i.e. sum of log(x1/x0) only depends on the first and
    # last terms' contributions (because log(x1/x0) + log(x2/x1)= log(x2) - log(x1) + log(x1) - log(x0)) = log(x2/x0))
    # which raises the question how accurate a measure the sample mean return is of the population mean return.
    last_date, first_date = list(prices)[0], list(prices)[-1]
    last_price = prices[last_date][keys.keys['PRICES']['CLOSE']]
    first_price = prices[first_date][keys.keys['PRICES']['CLOSE']]
    mean_return = log(float(last_price)/float(first_price)) / \
        (trading_period*sample)

    # VOLATILITY CALCULATION
    today, variance, tomorrows_price, tomorrows_date = False, 0, 0, None
    # adjust the random variable being measured so expectation is easier to calculate.
    mean_mod_return = mean_return*sqrt(trading_period)
    logger.debug(
        f'Calculating mean annual volatility over last {sample} days for {ticker}')

    for this_date in prices:
        todays_price = prices[this_date][keys.keys['PRICES']['CLOSE']]

        if today:
            logger.verbose(
                f'{this_date}: (todays_price, tomorrows_price) = ({todays_price}, {tomorrows_price})')

            # crypto prices may have weekends and holidays removed during correlation algorithm
            # so samples can be compared to equities, need to account for these dates by increasing
            # the time_delta by the number of missed days.
            if asset_type == keys.keys['ASSETS']['CRYPTO'] or \
                    (asset_type == keys.keys['ASSETS']['EQUITY'] and not dater.consecutive_trading_days(tomorrows_date, this_date)):
                time_delta = (dater.parse_date_string(
                    tomorrows_date) - dater.parse_date_string(this_date)).days
            else:
                time_delta = 1

            current_mod_return = log(
                float(tomorrows_price)/float(todays_price))/sqrt(time_delta*trading_period)
            daily = (current_mod_return - mean_mod_return)**2/(sample - 1)
            variance = variance + daily

            logger.verbose(
                f'{this_date}: (daily_variance, sample_variance) = ({round(daily, 4)}, {round(variance, 4)})')

        else:
            today = True

        tomorrows_price = prices[this_date][keys.keys['PRICES']['CLOSE']]
        tomorrows_date = this_date

    # adjust for output
    volatility = sqrt(variance)
    # ito's lemma
    mean_return = mean_return + 0.5*(volatility**2)
    logger.debug(
        f'(mean_return, sample_volatility) = ({round(mean_return, 2)}, {round(volatility, 2)})')

    results = {
        keys.keys['STATISTICS']['RETURN']: mean_return,
        keys.keys['STATISTICS']['VOLATILITY']: volatility
    }

    profile_cache.save_or_update_row(ticker=ticker, start_date=start_date, end_date=end_date,
                                     method=keys.keys['ESTIMATION']['MOMENT'], weekends=weekends,
                                     annual_return=results[keys.keys['STATISTICS']['RETURN']],
                                     annual_volatility=results[keys.keys['STATISTICS']['VOLATILITY']])
    return results


def calculate_correlation(ticker_1: str, ticker_2: str, asset_type_1: Union[str, None] = None, asset_type_2: Union[str, None] = None, start_date: Union[datetime.date, None] = None, end_date: Union[datetime.date, None] = None, sample_prices: Union[Dict[str, Dict[str, float]], None] = None, weekends: Union[int, None] = None, method: str = settings.ESTIMATION_METHOD) -> dict:
    """
    Returns the correlation between *ticker_1* and *ticker_2* from *start_date* to *end_date* using the estimation method *method*.

    Parameters
    ----------
    1. **ticker_1** : ``str``
        Ticker symbol for first asset.
    2. **ticker_2** : ``str``
        Ticker symbol for second asset
    3. **asset_type_1** : ``str``
        *Optional*. Specify asset type to prevent redundant calculations down the stack. Allowable values can be found in `scrilla.keys.keys['ASSETS]' dictionary.
    4. **asset_type_2** : ``str``
        *Optional*. Specify asset type to prevent redundant calculations down the stack. Allowable values can be found in `scrilla.keys.keys['ASSETS]' dictionary.
    5. *start_date* : ``datetime.date``
        *Optional*. Start date of the time period over which correlation will be calculated. If `None`, defaults to 100 trading days ago.
    6. **end_date** : ``datetime.date`` 
        *Optional*. End date of the time period over which correlation will be calculated. If `None`, defaults to last trading day.
    7. **sample_prices** : ``dict``
        *Optional*. A list of the asset prices for which correlation will be calculated. Overrides calls to service and calculates correlation for sample of prices supplied. Will disregard start_date and end_date. Must be of the format: `{'ticker_1': { 'date_1' : 'price_1', 'date_2': 'price_2' ...}, 'ticker_2': { 'date_1' : 'price_1:, ... } }` and ordered from latest date to earliest date. 
    8. **method** : ``str``
        *Optional*. Defaults to the value set by `scrilla.settings.ESTIMATION_METHOD`, which in turn is configured by the **DEFAULT_ESTIMATION_METHOD** environment variable. Determines the estimation method used during the calculation of sample statistics. Allowable values can be accessed through `scrilla.keys.keys['ESTIMATION']`.

    Raises
    ------
    1. **KeyError**
        If the `method` passed in doesn't map to one of the allowable estimation method values, this error will be thrown. 

    Returns
    ------
    ``Dict[str, float]``
        Dictionary containing the correlation of `ticker_1` and `ticker_2`: Formatted as: `{ 'correlation' : float }`.
    """
    if method == keys.keys['ESTIMATION']['MOMENT']:
        return calculate_moment_correlation(ticker_1, ticker_2, asset_type_1, asset_type_2, start_date, end_date, sample_prices, weekends)
    if method == keys.keys['ESTIMATION']['LIKE']:
        return calculate_likelihood_correlation(ticker_1, ticker_2, asset_type_1, asset_type_2, start_date, end_date, sample_prices, weekends)
    if method == keys.keys['ESTIMATION']['PERCENT']:
        return calculate_percentile_correlation(ticker_1, ticker_2, asset_type_1, asset_type_2, start_date, end_date, sample_prices, weekends)
    raise KeyError('Estimation method not found')


def calculate_percentile_correlation(ticker_1: str, ticker_2: str, asset_type_1: Union[str, None] = None, asset_type_2: Union[str, None] = None, start_date: Union[datetime.date, None] = None, end_date: Union[datetime.date, None] = None, sample_prices: Union[Dict[str, Dict[str, float]], None] = None, weekends: Union[int, None] = None) -> Dict[str, float]:
    """
    Returns the sample correlation calculated using the method of Percentile Matching, assuming underlying price process follows Geometric Brownian Motion, i.e. the price distribution is lognormal. 

   Parameters
    ----------
    1. **ticker_1** : ``str``
        Ticker symbol for first asset.
    2. **ticker_2** : ``str``
        Ticker symbol for second asset
    3. **asset_type_1** : ``str``
        *Optional*. Specify asset type to prevent redundant calculations down the stack. Allowable values can be found in `scrilla.keys.keys['ASSETS]' dictionary.
    4. **asset_type_2** : ``str``
        *Optional*. Specify asset type to prevent redundant calculations down the stack. Allowable values can be found in `scrilla.keys.keys['ASSETS]' dictionary.
    5. *start_date* : ``datetime.date``
        *Optional*. Start date of the time period over which correlation will be calculated. If `None`, defaults to 100 trading days ago.
    6. **end_date** : ``datetime.date`` 
        *Optional*. End date of the time period over which correlation will be calculated. If `None`, defaults to last trading day.
    7. **sample_prices** : ``Dict[str, float]``
        *Optional*. A list of the asset prices for which correlation will be calculated. Overrides calls to service and calculates correlation for sample of prices supplied. Will disregard start_date and end_date. Must be of the format: `{'ticker_1': { 'date_1' : 'price_1', 'date_2': 'price_2' ...}, 'ticker_2': { 'date_1' : 'price_1:, ... } }` and ordered from latest date to earliest date. 

    Raises
    ------
    1. **scrilla.errors.PriceError**
        If no price data is inputted into the function and the application cannot retrieve price data from the cache or external services, this error will be thrown.

    Returns
    ------
    ``Dict[str, float]``
        Dictionary containing the correlation of `ticker_1` and `ticker_2`: Formatted as: `{ 'correlation' : float }`.
    """
    ### START ARGUMENT PARSING ###
    asset_type_1 = errors.validate_asset_type(
        ticker=ticker_1, asset_type=asset_type_1)
    asset_type_2 = errors.validate_asset_type(
        ticker=ticker_2, asset_type=asset_type_2)

    # cache flag to signal if calculation includes weekends or not,
    # only perform check if not passed in as argument
    if weekends is None:
        if asset_type_1 == asset_type_2 and asset_type_2 == keys.keys['ASSETS']['CRYPTO']:
            weekends = 1
        else:
            weekends = 0

    if asset_type_1 == asset_type_2 and asset_type_2 == keys.keys['ASSETS']['CRYPTO'] and weekends == 1:
        # validate over total days.
        start_date, end_date = errors.validate_dates(start_date=start_date, end_date=end_date,
                                                     asset_type=keys.keys['ASSETS']['CRYPTO'])
    else:
        #   validate over trading days. since sample(date - 100 days) > (date - 100 trading days), always
        #   take the largest sample so intersect_dict_keys will return a sample of the correct size
        #   for mixed asset types.
        start_date, end_date = errors.validate_dates(start_date=start_date, end_date=end_date,
                                                     asset_type=keys.keys['ASSETS']['EQUITY'])

    if sample_prices is None:
        # TODO: extra save_or_update argument for estimation method, i.e. moments, percentiles or likelihood
        correlation = correlation_cache.filter_correlation_cache(ticker_1=ticker_1, ticker_2=ticker_2,
                                                                 start_date=start_date, end_date=end_date,
                                                                 weekends=weekends,
                                                                 method=keys.keys['ESTIMATION']['PERCENT'])
        if correlation is not None:
            return correlation

        sample_prices = {}
        logger.debug(
            f'No sample prices provided or cached ({ticker_1}, {ticker_2}) correlation found.')
        logger.debug('Retrieving price histories for calculation.')
        sample_prices[ticker_1] = services.get_daily_price_history(ticker=ticker_1, start_date=start_date,
                                                                   end_date=end_date, asset_type=asset_type_1)
        sample_prices[ticker_2] = services.get_daily_price_history(ticker=ticker_2, start_date=start_date,
                                                                   end_date=end_date, asset_type=asset_type_2)

    if asset_type_1 == asset_type_2 and asset_type_2 == keys.keys['ASSETS']['CRYPTO'] and weekends == 0:
        sample_prices[ticker_1] = dater.intersect_with_trading_dates(
            sample_prices[ticker_1])
        sample_prices[ticker_2] = dater.intersect_with_trading_dates(
            sample_prices[ticker_2])
    else:
        # intersect with equity keys to get trading days
        sample_prices[ticker_1], sample_prices[ticker_2] = helper.intersect_dict_keys(
            sample_prices[ticker_1], sample_prices[ticker_2])

    if 0 in [len(sample_prices[ticker_1]), len(sample_prices[ticker_2])]:
        raise errors.PriceError(
            "Prices cannot be retrieved for correlation calculation")

    if asset_type_1 == asset_type_2 and asset_type_1 == keys.keys['ASSETS']['CRYPTO']:
        trading_period = constants.constants['ONE_TRADING_DAY']['CRYPTO']
    else:
        trading_period = constants.constants['ONE_TRADING_DAY']['EQUITY']

    sample_of_returns_1 = get_sample_of_returns(
        ticker=ticker_1, sample_prices=sample_prices[ticker_1], asset_type=asset_type_1)
    sample_of_returns_2 = get_sample_of_returns(
        ticker=ticker_2, sample_prices=sample_prices[ticker_2], asset_type=asset_type_2)

    percentiles = [0.1, 0.25, 0.5, 0.75, 0.9]
    sample_percentiles_1, sample_percentiles_2 = [], []
    for percentile in percentiles:
        sample_percentiles_1.append(estimators.sample_percentile(
            data=sample_of_returns_1, percentile=percentile))
        sample_percentiles_2.append(estimators.sample_percentile(
            data=sample_of_returns_2, percentile=percentile))

    def cov_matrix(params):
        determinant = params[0]*params[1] - params[2]**2
        print('calling cov matrix', params)
        print('determinant', determinant)
        if determinant == 0 or determinant < 0 or determinant < 0.00000001:
            return 0
        return [[params[0], params[2]], [params[2], params[1]]]

    def objective(params):
        print('calling objective', params)
        return [
            (
                multivariate_normal.cdf(x=[sample_percentiles_1[i], sample_percentiles_2[i]],
                                        mean=params[:2],
                                        cov=cov_matrix(params[2:5]), allow_singular=True) - percentile
            ) for i, percentile in enumerate(percentiles)
        ]

    vol_1_guess = (sample_percentiles_1[3]-sample_percentiles_1[1])/2
    vol_2_guess = (sample_percentiles_2[3]-sample_percentiles_2[1])/2
    vol_1_bounds = max(sample_of_returns_1) - min(sample_of_returns_1)
    vol_2_bounds = max(sample_of_returns_2) - min(sample_of_returns_2)
    cov_bounds = (-1*sqrt(vol_1_bounds*vol_2_bounds),
                  sqrt(vol_1_bounds*vol_2_bounds))
    guess = (
        sample_percentiles_1[2], sample_percentiles_2[2], vol_1_guess, vol_2_guess, 0)

    lower_bound = (
        sample_percentiles_1[0], sample_percentiles_2[0], 0, 0, cov_bounds[0])
    upper_bound = (sample_percentiles_1[4], sample_percentiles_2[4],
                   vol_1_bounds, vol_2_bounds, cov_bounds[1])
    print('guess', guess)
    print('lower bound', lower_bound)
    print('upper bound', upper_bound)
    parameters = least_squares(
        objective, guess, bounds=(lower_bound, upper_bound))

    print(parameters)
    result = {keys.keys['STATISTICS']['correlation']:  parameters[4]}

    # correlation_cache.save_row(ticker_1=ticker_1, ticker_2=ticker_2,
    #                         start_date=start_date, end_date=end_date,
    #                        correlation=correlation, method=keys.keys['ESTIMATION']['PERCENT'])
    return result


def calculate_likelihood_correlation(ticker_1: str, ticker_2: str, asset_type_1: Union[str, None] = None, asset_type_2: Union[str, None] = None, start_date: Union[datetime.date, None] = None, end_date: Union[datetime.date, None] = None, sample_prices: Union[Dict[str, Dict[str, float]], None] = None, weekends: Union[int, None] = None) -> Dict[str, float]:
    """
    Calculates the sample correlation using the maximum likelihood estimators, assuming underlying price process follows Geometric Brownian Motion, i.e. the price distribution is lognormal. 

    Parameters
    ----------
    1. **ticker_1** : ``str``
        Ticker symbol for first asset.
    2. **ticker_2** : ``str``
        Ticker symbol for second asset
    3. **asset_type_1** : ``str``
        *Optional*. Specify asset type to prevent redundant calculations down the stack. Allowable values can be found in `scrilla.keys.keys['ASSETS]' dictionary.
    4. **asset_type_2** : ``str``
        *Optional*. Specify asset type to prevent redundant calculations down the stack. Allowable values can be found in `scrilla.keys.keys['ASSETS]' dictionary.
    5. *start_date* : ``datetime.date``
        *Optional*. Start date of the time period over which correlation will be calculated. If `None`, defaults to 100 trading days ago.
    6. **end_date** : ``datetime.date`` 
        *Optional*. End date of the time period over which correlation will be calculated. If `None`, defaults to last trading day.
    7. **sample_prices** : ``dict``
        *Optional*. A list of the asset prices for which correlation will be calculated. Overrides calls to service and calculates correlation for sample of prices supplied. Will disregard start_date and end_date. Must be of the format: `{'ticker_1': { 'date_1' : 'price_1', 'date_2': 'price_2' ...}, 'ticker_2': { 'date_1' : 'price_1:, ... } }` and ordered from latest date to earliest date. 

    Raises
    ------
    1. **scrilla.errors.PriceError**
        If no price data is inputted into the function and the application cannot retrieve price data from the cache or external services, this error will be thrown.

    Returns
    ------
    ``Dict[str, float]``
        Dictionary containing the correlation of `ticker_1` and `ticker_2`: Formatted as: `{ 'correlation' : float }`.
    """
    from scrilla.analysis import optimizer
    ### START ARGUMENT PARSING ###
    asset_type_1 = errors.validate_asset_type(
        ticker=ticker_1, asset_type=asset_type_1)
    asset_type_2 = errors.validate_asset_type(
        ticker=ticker_2, asset_type=asset_type_2)

    # cache flag to signal if calculation includes weekends or not,
    # only perform check if not passed in as argument
    if weekends is None:
        if asset_type_1 == asset_type_2 and asset_type_2 == keys.keys['ASSETS']['CRYPTO']:
            weekends = 1
        else:
            weekends = 0

    if asset_type_1 == asset_type_2 and asset_type_2 == keys.keys['ASSETS']['CRYPTO'] and weekends == 1:
        # validate over total days.
        start_date, end_date = errors.validate_dates(start_date=start_date, end_date=end_date,
                                                     asset_type=keys.keys['ASSETS']['CRYPTO'])
    else:
        #   validate over trading days. since sample(date - 100 days) > (date - 100 trading days), always
        #   take the largest sample so intersect_dict_keys will return a sample of the correct size
        #   for mixed asset types.
        start_date, end_date = errors.validate_dates(start_date=start_date, end_date=end_date,
                                                     asset_type=keys.keys['ASSETS']['EQUITY'])

    if sample_prices is None:
        correlation = correlation_cache.filter_correlation_cache(ticker_1=ticker_1, ticker_2=ticker_2,
                                                                 start_date=start_date, end_date=end_date,
                                                                 weekends=weekends,
                                                                 method=keys.keys['ESTIMATION']['LIKE'])
        if correlation is not None:
            return correlation

        sample_prices = {}
        logger.debug(
            f'No sample prices provided or cached ({ticker_1}, {ticker_2}) correlation found.')
        logger.debug('Retrieving price histories for calculation.')
        sample_prices[ticker_1] = services.get_daily_price_history(ticker=ticker_1,
                                                                   start_date=start_date,
                                                                   end_date=end_date,
                                                                   asset_type=asset_type_1)
        sample_prices[ticker_2] = services.get_daily_price_history(ticker=ticker_2,
                                                                   start_date=start_date,
                                                                   end_date=end_date,
                                                                   asset_type=asset_type_2)

    if asset_type_1 == asset_type_2 and asset_type_2 == keys.keys['ASSETS']['CRYPTO'] and weekends == 0:
        sample_prices[ticker_1] = dater.intersect_with_trading_dates(
            sample_prices[ticker_1])
        sample_prices[ticker_2] = dater.intersect_with_trading_dates(
            sample_prices[ticker_2])
    else:
        # intersect with equity keys to get trading days
        sample_prices[ticker_1], sample_prices[ticker_2] = helper.intersect_dict_keys(
            sample_prices[ticker_1], sample_prices[ticker_2])

    if 0 in [len(sample_prices[ticker_1]), len(sample_prices[ticker_2])]:
        raise errors.PriceError(
            "Prices cannot be retrieved for correlation calculation")

    sample_of_returns_1 = get_sample_of_returns(ticker=ticker_1,
                                                sample_prices=sample_prices[ticker_1],
                                                asset_type=asset_type_1)
    sample_of_returns_2 = get_sample_of_returns(ticker=ticker_2,
                                                sample_prices=sample_prices[ticker_2],
                                                asset_type=asset_type_2)

    combined_sample = [[sample_of_returns_1[i], sample_of_returns_2[i]]
                       for i, el in enumerate(sample_of_returns_1)]

    likelihood_estimates = optimizer.maximize_bivariate_normal_likelihood(
        data=combined_sample)

    # Var(d lnS / delta_t ) = Var(d lnS )/delta_t**2 = sigma**2 * delta_t / delta_t**2
    #   = sigma**2/delta_t
    # Cov(d lnS/delta_t, d lnQ/delta_t) = Cov(d lnS, dlnQ)/delta_t**2
    #   = rho * sigma_s * sigma_q / delta_t**2
    vol_1 = sqrt(likelihood_estimates[2])
    vol_2 = sqrt(likelihood_estimates[3])

    correlation = likelihood_estimates[4] / (vol_1*vol_2)

    result = {'correlation': correlation}

    correlation_cache.save_row(ticker_1=ticker_1, ticker_2=ticker_2,
                               start_date=start_date, end_date=end_date,
                               correlation=correlation, weekends=weekends,
                               method=keys.keys['ESTIMATION']['LIKE'])
    return result


def calculate_moment_correlation(ticker_1: str, ticker_2: str, asset_type_1: Union[str, None] = None, asset_type_2: Union[str, None] = None, start_date: Union[datetime.date, None] = None, end_date: Union[datetime.date, None] = None, sample_prices: Union[Dict[str, Dict[str, float]], None] = None, weekends: Union[int, None] = None) -> Dict[str, float]:
    """
    Returns the sample correlation using the method of Moment Matching, assuming underlying price process follows Geometric Brownian Motion, i.e. the price distribution is lognormal. 

    Parameters
    ----------
    1. **ticker_1** : ``str``
        Ticker symbol for first asset.
    2. **ticker_2** : ``str``
        Ticker symbol for second asset
    3. **asset_type_1** : ``Union[str,None]``
        *Optional*. Specify asset type to prevent redundant calculations down the stack. Allowable values can be found in `scrilla.keys.keys['ASSETS]' dictionary.
    4. **asset_type_2** : ``Union[str,None]``
        *Optional*. Specify asset type to prevent redundant calculations down the stack. Allowable values can be found in `scrilla.keys.keys['ASSETS]' dictionary.
    5. *start_date* : ``Union[datetime.date,None]``
        *Optional*. Start date of the time period over which correlation will be calculated. If `None`, defaults to 100 trading days ago.
    6. **end_date** : ``Union[datetime.date None]`` 
        *Optional*. End date of the time period over which correlation will be calculated. If `None`, defaults to last trading day.
    7. **sample_prices** : ``Union[dict,None]``
        *Optional*. A list of the asset prices for which correlation will be calculated. Overrides calls to service and calculates correlation for sample of prices supplied. Will disregard start_date and end_date. Must be of the format: `{'ticker_1': { 'date_1' : 'price_1', 'date_2': 'price_2' ...}, 'ticker_2': { 'date_1' : 'price_1:, ... } }` and ordered from latest date to earliest date. 
    8. **weekends** : ``Union[int,None]``
        **Optional**. A flag to signal that calculations should include/exclude weekend dates. See *notes* for more information. Defauts to `None` and is implicitly determined by the asset types passed in.

    Raises
    ------
    1. **scrilla.errors.PriceError**
        If no price data is inputted into the function and the application cannot retrieve price data from the cache or external services, this error will be thrown.

    Returns
    ------
    ``Dict[str, float]``
        Dictionary containing the correlation of `ticker_1` and `ticker_2`: Formatted as: `{ 'correlation' : float }`

    .. notes:: 
        * when the asset types are mixed, i.e. `asset_type_1` == 'equity' and `asset_type_2`== 'crypto', the sample prices will contain different information, since crypto trades on weekends and holidays. The solution is to throw away the weekend and holiday prices for crypto. This presents another problem, since the risk profile for a crypto-currency that is cached in the local fileystem will be calculated over the entire sample including the missing data, whereas the risk profile required by the correlation needs to be calculated over the censored sample (i.e. the one with weekends and holidays removed) so that the means of the mixed asset types are scaled to the same time delta. In this case, the correlation algorithm needs to be able to override calls to the cache and force the risk profile algorithms to calculate based on the sample. Note: this issue only applies to correlation calculations using the method of moment matching, since the other methods determine the value of the correlation by solving constrained systems of equations instead of deriving it analytically with a formula. 
        * The `weekends` flag is only relevant for assets of type `scrilla.static.keys.keys['ASSETS']['CRYPTO']`, i.e. cryptocurrency. It is passed in when the correlation calculation is part of a larger correlation matrix calculation, so that entries in the matrix have equivalent time frames. E.g., if the `scrilla.analysis.models.geometric.statistics.correlation_matrix` is calculating a matrix for a collection of mixed asset types, say, `["BTC", "ETH", "ALLY", "SPY"]`, the correlations between (crypto, equity) and (equity, equity) will only include weekdays, where as the (crypto,crypto) pairing will include weekends and thus result in an inaccurate matrix. To resolve this problem, the `weekends` flag can be passed into this calculation to prevent (crypto,crypto) pairings from including weekends.

    """
    ### START ARGUMENT PARSING ###
    asset_type_1 = errors.validate_asset_type(
        ticker=ticker_1, asset_type=asset_type_1)
    asset_type_2 = errors.validate_asset_type(
        ticker=ticker_2, asset_type=asset_type_2)

    # cache flag to signal if calculation includes weekends or not,
    # only perform check if not passed in as argument so that agent
    # calling can override default weekend behavior, i.e. make
    # crypto pairing forcibly exclude weekends from their calculation.
    if weekends is None:
        if asset_type_1 == asset_type_2 and asset_type_2 == keys.keys['ASSETS']['CRYPTO']:
            weekends = 1
        else:
            weekends = 0

    if asset_type_1 == asset_type_2 and asset_type_2 == keys.keys['ASSETS']['CRYPTO'] and weekends == 1:
        # validate over total days.
        start_date, end_date = errors.validate_dates(start_date=start_date, end_date=end_date,
                                                     asset_type=keys.keys['ASSETS']['CRYPTO'])
    else:
        # validate over trading days.
        start_date, end_date = errors.validate_dates(start_date=start_date, end_date=end_date,
                                                     asset_type=keys.keys['ASSETS']['EQUITY'])

    if sample_prices is None:
        correlation = correlation_cache.filter_correlation_cache(ticker_1=ticker_1, ticker_2=ticker_2,
                                                                 start_date=start_date, end_date=end_date,
                                                                 weekends=weekends,
                                                                 method=keys.keys['ESTIMATION']['MOMENT'])
        if correlation is not None:
            return correlation

        sample_prices = {}
        logger.debug(
            f'No sample prices provided or cached ({ticker_1}, {ticker_2}) correlation found.')
        logger.debug('Retrieving price histories for calculation.')
        sample_prices[ticker_1] = services.get_daily_price_history(ticker=ticker_1, start_date=start_date,
                                                                   end_date=end_date, asset_type=asset_type_1)
        sample_prices[ticker_2] = services.get_daily_price_history(ticker=ticker_2, start_date=start_date,
                                                                   end_date=end_date, asset_type=asset_type_2)

    # TODO: pretty sure something about this is causing the issue.
    if asset_type_1 == asset_type_2 and asset_type_2 == keys.keys['ASSETS']['CRYPTO'] and weekends == 0:
        # remove weekends and holidays from sample
        logger.debug('Removing weekends from crypto sample')
        sample_prices[ticker_1] = dater.intersect_with_trading_dates(
            sample_prices[ticker_1])
        sample_prices[ticker_2] = dater.intersect_with_trading_dates(
            sample_prices[ticker_2])
    else:
        # intersect with equity keys to get trading days
        sample_prices[ticker_1], sample_prices[ticker_2] = helper.intersect_dict_keys(
            sample_prices[ticker_1], sample_prices[ticker_2])

    if 0 in [len(sample_prices[ticker_1]), len(sample_prices[ticker_2])]:
        raise errors.PriceError(
            "Prices cannot be retrieved for correlation calculation")

    if asset_type_1 == keys.keys['ASSETS']['CRYPTO']:
        trading_period_1 = constants.constants['ONE_TRADING_DAY']['CRYPTO']
    else:
        trading_period_1 = constants.constants['ONE_TRADING_DAY']['EQUITY']
    if asset_type_2 == keys.keys['ASSETS']['CRYPTO']:
        trading_period_2 = constants.constants['ONE_TRADING_DAY']['CRYPTO']
    else:
        trading_period_2 = constants.constants['ONE_TRADING_DAY']['EQUITY']
    ### END ARGUMENT PARSING ###

    ### START SAMPLE STATISTICS CALCULATION DEPENDENCIES ###
        # i.e. statistics that need to be calculated before correlation can be calculated
    logger.debug(
        f'Preparing calculation dependencies for ({ticker_1},{ticker_2}) correlation')

    stats_1 = calculate_moment_risk_return(ticker=ticker_1,
                                           start_date=start_date,
                                           end_date=end_date,
                                           asset_type=asset_type_1,
                                           weekends=weekends)

    stats_2 = calculate_moment_risk_return(ticker=ticker_2,
                                           start_date=start_date,
                                           end_date=end_date,
                                           asset_type=asset_type_2,
                                           weekends=weekends)

    # ito's lemma
    mod_mean_1 = (stats_1['annual_return'] - 0.5*(stats_1['annual_volatility'])
                  ** 2)*sqrt(trading_period_1)

    mod_mean_2 = (stats_2['annual_return'] - 0.5*(stats_2['annual_volatility'])
                  ** 2)*sqrt(trading_period_2)

    logger.debug(f'Calculating ({ticker_1}, {ticker_2}) correlation.')
    # END SAMPLE STATISTICS CALCULATION DEPENDENCIES

    # Initialize loop variables
    covariance, time_delta = 0, 1
    today, tomorrows_date = False, None
    sample = len(sample_prices[ticker_1])

    #### START CORRELATION LOOP ####
    for this_date in sample_prices[ticker_1]:
        todays_price_1 = sample_prices[ticker_1][this_date][keys.keys['PRICES']['CLOSE']]
        todays_price_2 = sample_prices[ticker_2][this_date][keys.keys['PRICES']['CLOSE']]

        if today:
            logger.verbose(f'today = {this_date}')
            logger.verbose(
                f'(todays_price, tomorrows_price)_{ticker_1} = ({todays_price_1}, {tomorrows_price_1})')
            logger.verbose(
                f'(todays_price, tomorrows_price)_{ticker_2} = ({todays_price_2}, {tomorrows_price_2})')

            # NOTE: crypto prices may have weekends and holidays removed during correlation algorithm
            # so samples can be compared to equities, need to account for these dates by increasing
            # the time_delta by the number of missed days, to offset the weekend and holiday return.
            if asset_type_1 == keys.keys['ASSETS']['CRYPTO'] or \
                    (asset_type_1 == keys.keys['ASSETS']['EQUITY'] and not dater.consecutive_trading_days(tomorrows_date, this_date)):
                time_delta = (dater.parse_date_string(
                    tomorrows_date) - dater.parse_date_string(this_date)).days
            else:
                time_delta = 1

            current_mod_return_1 = log(
                float(tomorrows_price_1)/float(todays_price_1))/sqrt(time_delta*trading_period_1)

            # see above note
            if asset_type_2 == keys.keys['ASSETS']['CRYPTO'] or \
                    (asset_type_2 == keys.keys['ASSETS']['EQUITY'] and not dater.consecutive_trading_days(tomorrows_date, this_date)):
                time_delta = (dater.parse_date_string(
                    tomorrows_date) - dater.parse_date_string(this_date)).days
            else:
                time_delta = 1

            current_mod_return_2 = log(
                float(tomorrows_price_2)/float(todays_price_2))/sqrt(time_delta*trading_period_2)

            current_sample_covariance = (
                current_mod_return_1 - mod_mean_1)*(current_mod_return_2 - mod_mean_2)/(sample - 1)
            covariance = covariance + current_sample_covariance

            logger.verbose(
                f'(return_{ticker_1}, return_{ticker_2}) = ({round(current_mod_return_1, 2)}, {round(current_mod_return_2, 2)})')
            logger.verbose(
                f'(current_sample_covariance, covariance) = ({round(current_sample_covariance, 2)}, {round(covariance, 2)})')

        else:
            today = True

        tomorrows_price_1, tomorrows_price_2, tomorrows_date = todays_price_1, todays_price_2, this_date
    #### END CORRELATION LOOP ####

    # Scale covariance into correlation
    correlation = covariance / \
        (stats_1['annual_volatility']*stats_2['annual_volatility'])

    logger.debug(f'correlation = ({round(correlation, 2)})')

    result = {'correlation': correlation}

    correlation_cache.save_row(ticker_1=ticker_1, ticker_2=ticker_2,
                               start_date=start_date, end_date=end_date,
                               correlation=correlation, weekends=weekends,
                               method=keys.keys['ESTIMATION']['MOMENT'])
    return result


def correlation_matrix(tickers, asset_types=None, start_date=None, end_date=None, sample_prices=None, method=settings.ESTIMATION_METHOD, weekends: Union[int, None] = None) -> List[List[float]]:
    """
    Returns the correlation matrix for *tickers* from *start_date* to *end_date* using the estimation method *method*.

    Parameters
    ----------
    1. **tickers** : ``list``
        List of ticker symbols whose correlation matrix is to be calculated. Format: `['ticker_1', 'ticker_2', ...]`
    2. **asset_type2** : ``list``
        *Optional*. List of asset types that map to the `tickers` list. Specify **asset_types** to prevent redundant calculations down the stack. Allowable values can be found in `scrilla.keys.keys['ASSETS]' dictionary.
    3. *start_date* : ``datetime.date``
        *Optional*. Start date of the time period over which correlation will be calculated. If `None`, defaults to 100 trading days ago.
    4. **end_date** : ``datetime.date`` 
        *Optional*. End date of the time period over which correlation will be calculated. If `None`, defaults to last trading day.
    5. **sample_prices** : ``dict``
        *Optional*. A list of the asset prices for which correlation will be calculated. Overrides calls to service and calculates correlation for sample of prices supplied. Will disregard start_date and end_date. Must be of the format: `{'ticker_1': { 'date_1' : 'price_1', 'date_2': 'price_2' ...}, 'ticker_2': { 'date_1' : 'price_1:, ... } }` and ordered from latest date to earliest date. 
    6. **method** : ``str``
        *Optional*. Defaults to the value set by `scrilla.settings.ESTIMATION_METHOD`, which in turn is configured by the **DEFAULT_ESTIMATION_METHOD** environment variable. Determines the estimation method used during the calculation of sample statistics. Allowable values can be accessed through `scrilla.keys.keys['ESTIMATION']`.

    Raises
    ------
    1. **scrilla.errors.SampleSizeErrors**
        If list of tickers is not large enough to calculate a correlation matrix, this error will be thrown. 

    Returns
    ------
    ``List[List[float]]`` 
        correlation matrix of `tickers`. indices correspond to the Cartesian product of `tickers` x `tickers`. 
    """
    correl_matrix = [
                        [ 0 for _ in tickers ] for _ in tickers
                    ]


    # let correlation function handle argument parsing
    if asset_types is None:
        asset_types = [ errors.validate_asset_type(ticker) for ticker in tickers ]

    # NOTE: since crypto trades on weekends and equities do not, the function
    #       must determine if the inputted assets are of mixed type. If any
    #       single asset is of a different type, weekends must be truncated
    #       from sample to ensure correlation is calculated over the samples
    #       of like size.

    # By default, exclude weekends.
    if weekends is None:
        weekends = 0

    asset_groups = 0     
    for _ in groupby(sorted(asset_types)):
        asset_groups += 1


    # if all assets of the same type, include weekends only if asset type is crypto
    if asset_groups == 1 and asset_types[0] == keys.keys['ASSETS']['CRYPTO']:
        logger.debug('Assets of same type, which is crypto, keeping weekends')
        weekends = 1
    else:
        if asset_groups > 1:
            logger.debug('Assets of different type, removing weekends')
        else:
            logger.debug(
                'Assets of same type, which is equity, excluding weekends')

    if(len(tickers) > 1):
        for i, item in enumerate(tickers):
            correl_matrix[i][i] = 1
            for j in range(i+1, len(tickers)):
                cor = calculate_correlation(ticker_1=item,
                                            ticker_2=tickers[j],
                                            asset_type_1=asset_types[i],
                                            asset_type_2=asset_types[j],
                                            start_date=start_date,
                                            end_date=end_date,
                                            sample_prices=sample_prices,
                                            weekends=weekends,
                                            method=method)
                correl_matrix[i][j] = cor['correlation']
                correl_matrix[j][i] = correl_matrix[i][j]

        correl_matrix[len(tickers) - 1][len(tickers) - 1] = 1
        return correl_matrix
    if (len(tickers) == 1):
        correl_matrix[0][0] = 1
        return correl_matrix
    raise errors.SampleSizeError(
        'Cannot calculate correlation matrix for portfolio size <= 1.')


def calculate_moment_correlation_series(ticker_1: str, ticker_2: str, start_date: Union[date, None] = None, end_date: Union[date, None] = None) -> dict:
    asset_type_1 = errors.validate_asset_type(ticker=ticker_1)
    asset_type_2 = errors.validate_asset_type(ticker=ticker_2)
    if asset_type_1 == keys.keys['ASSETS']['CRYPTO'] and asset_type_2 == keys.keys['ASSETS']['CRYPTO']:
        # validate over all days
        start_date, end_date = errors.validate_dates(start_date=start_date, end_date=end_date,
                                                     asset_type=keys.keys['ASSETS']['CRYPTO'])
    else:
        #   validate over trading days. since (date - 100 days) > (date - 100 trading days), always
        #   take the largest sample so intersect_dict_keys will return a sample of the correct size
        #   for mixed asset types.
        start_date, end_date = errors.validate_dates(start_date=start_date, end_date=end_date,
                                                     asset_type=keys.keys['ASSETS']['EQUITY'])

    same_type = False
    correlation_series = {}

    if asset_type_1 == asset_type_2:
        same_type = True

    # TODO: what if start_date or end_date is None?
    if same_type and asset_type_1 == keys.keys['ASSETS']['CRYPTO']:
        date_range = [start_date] + dater.dates_between(start_date, end_date)
    else:  # default to business days
        date_range = [dater.get_previous_business_date(
            start_date)] + dater.business_dates_between(start_date, end_date)

    for this_date in date_range:
        calc_date_end = this_date
        todays_cor = calculate_moment_correlation(ticker_1=ticker_1,
                                                  ticker_2=ticker_2,
                                                  end_date=calc_date_end)
        correlation_series[dater.date_to_string(
            this_date)] = todays_cor['correlation']

    result = {}
    result[f'{ticker_1}_{ticker_2}_correlation_time_series'] = correlation_series
    return correlation_series


def calculate_return_covariance(ticker_1: str, ticker_2: str, start_date: Union[date, None] = None, end_date: Union[date, None] = None, sample_prices: Union[dict, None] = None, correlation: Union[dict, None] = None, profile_1: Union[dict, None] = None, profile_2: Union[dict, None] = None, method=settings.ESTIMATION_METHOD) -> float:
    """
    Returns the return covariance between *ticker_1* and *ticker_2* from *start_date* to *end_date* using the estimation method *method*.

    Parameters
    ----------
    1. **ticker_1** : ``str``
        Ticker symbol for first asset.
    2. **ticker_2** : ``str``
        Ticker symbol for second asset
    3. *start_date* : ``datetime.date``
        *Optional*. Start date of the time period over which correlation will be calculated. If `None`, defaults to 100 trading days ago.
    4. **end_date** : ``datetime.date`` 
        *Optional*. End date of the time period over which correlation will be calculated. If `None`, defaults to last trading day.
    5. **sample_prices** : ``dict``
        *Optional*. A dictionary containing the asset prices. Must be formatted as : ` { 'ticker_1': { 'date_1': value, ...}, 'ticker_2': { 'date_2' : value, ...}}.
    6. **correlation** : ``dict``
        *Optional*. Overrides correlation caluclation. A dictionary containing the correlation that should be used in lieu of estimating it from historical data. Formatted as : `{ 'correlation': value }
    7. **profile_1** : ``dict``
        *Optional*. Overrides asset 1's risk profile calculation. A dictionary containing the risk profile of the first asset that should be used in lieu of estimating it from historical data.
    8. **profile_2** : ``dict``
        *Optional*. Overrides asset 2's risk profile calculation. A dictionary containing the risk profile of the second asset that should be used in lieu of estimating it from historical data.
    9. **method** : ``str``
        *Optional*. Defaults to the value set by `scrilla.settings.ESTIMATION_METHOD`, which in turn is configured by the **DEFAULT_ESTIMATION_METHOD** environment variable. Determines the estimation method used during the calculation of sample statistics. Allowable values can be accessed through `scrilla.keys.keys['ESTIMATION']`.

    Returns
    ------
    ``float`` :  return covariance
    """
    if correlation is None:
        if sample_prices is None:
            correlation = calculate_correlation(ticker_1=ticker_1, ticker_2=ticker_2, start_date=start_date,
                                                end_date=end_date, method=method)
        else:
            correlation = calculate_correlation(ticker_1=ticker_1, ticker_2=ticker_2,
                                                sample_prices=sample_prices, method=method)

    if profile_1 is None:
        if sample_prices is None:
            profile_1 = calculate_risk_return(ticker=ticker_1, start_date=start_date, end_date=end_date,
                                              method=method)
        else:
            profile_1 = calculate_risk_return(ticker=ticker_1, sample_prices=sample_prices[ticker_1],
                                              method=method)

    if profile_2 is None:
        if sample_prices is None:
            profile_2 = calculate_risk_return(ticker=ticker_2, start_date=start_date, end_date=end_date,
                                              method=method)
        else:
            profile_2 = calculate_risk_return(ticker=ticker_2, sample_prices=sample_prices[ticker_2],
                                              method=method)

    covariance = profile_1['annual_volatility'] * \
        profile_2['annual_volatility']*correlation['correlation']
    return covariance
