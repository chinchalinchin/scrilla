
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
A module of functions that wrap around `scipy.optimize` in order to optimize statistical and financial functions of interest.
"""

from typing import List, Tuple
from math import sqrt

import scipy.optimize as optimize

from scrilla import settings
from scrilla.static import constants
from scrilla.analysis import estimators
from scrilla.analysis.objects.portfolio import Portfolio
import scrilla.util.outputter as outputter

logger = outputter.Logger('scrilla.analysis.optimizer', settings.LOG_LEVEL)


def maximize_univariate_normal_likelihood(data: List[float]) -> List[float]:
    r"""
    Maximizes the normal (log-)likelihood of the sample with respect to the mean and volatility in order to estimate the mean and volatility of the population distribution described by the sample.

    Parameters
    ----------
    1. **data**: ``List[float]``
        Sample of data drawn from a univariate normal population. 

    Returns
    -------
    ``List[float]``
        A list containing the maximum likelihood estimates of the univariates normal distribution's parameters. The first element of the list corresponds to the mean and the second element corresponds to the volatility.

    .. notes::
        * Some comments about the methodology. This module assumes an underlying asset price process that follows Geometric Brownian motion. This implies the return on the asset over intervals of  \\(\delta t\\) is normally distributed with mean \\(\mu * \delta t\\) and volatility \\(\sigma \cdot \sqrt{\delta t}\\). If the sample is scaled by \\(\delta t\\), then the mean becomes \\(\mu\\) and the volatility \\(\frac{\sigma}{\sqrt t}\\).  Moreover, increments are independent. Therefore, if the observations are made over equally spaced intervals, each observation is drawn from an independent, identially distributed normal random variable. The parameters \\(\mu\\) and :\\(\frac {\sigma}{\delta t}\\) can then be estimated by maximizing the probability of observing a given sample with respect to the parameters. To obtain the estimate for \\(\sigma\\), multiply the result of this function by \\(\delta t\\).
        * Theoretically, the output of this function should equal the same value obtained from the method of moment matching. However, there is a small discrepancy. It could be due to floating point arthimetic. However, see Section 2.2 of the following for what I think may be, if not the source, at least related to the [issue](https://www.researchgate.net/publication/5071468_Maximum_Likelihood_Estimation_of_Generalized_Ito_Processes_With_Discretely-Sampled_Data)
        The author, however, is not considering the transformed Ito process, the log of the asset price process. It seems like his conclusion may be an artifact of Ito's Lemma? Not sure. Will need to think.
    """

    def likelihood(x): return (-1) * \
        estimators.univariate_normal_likelihood_function(params=x, data=data)

    # make an educated guess
    first_quartile = estimators.sample_percentile(data=data, percentile=0.25)
    median = estimators.sample_percentile(data=data, percentile=0.5)
    third_quartile = estimators.sample_percentile(data, percentile=0.75)
    guess = [median, (third_quartile-first_quartile)/2]

    params = optimize.minimize(fun=likelihood, x0=guess, options={'disp': False},
                               method=constants.constants['OPTIMIZATION_METHOD'])
    return params.x


def maximize_bivariate_normal_likelihood(data: List[Tuple[float, float]]) -> List[float]:
    r"""

    .. warning ::
        This can take an extremely long time to solve...

    Returns
    -------
    ``List[float]``
        A list containing the maximum likelihood estimates of the bivariates normal distribution's parameters. The first element of the list corresponds to \\(\mu_x)\\), the second element the \\(\mu_y)\\), the third element \\(\sigma_x)\\), the fourth element \\(\sigma_y)\\) and the fifth element \\(\rho_{xy} \cdot \sigma_y \cdot \sigma_x)\\).
    """

    x_data = [datum[0] for datum in data]
    y_data = [datum[1] for datum in data]

    x_25_percentile = estimators.sample_percentile(x_data, 0.25)
    y_25_percentile = estimators.sample_percentile(y_data, 0.25)
    x_median = estimators.sample_percentile(x_data, 0.5)
    y_median = estimators.sample_percentile(y_data, 0.5)
    x_75_percentile = estimators.sample_percentile(x_data, 0.75)
    y_75_percentile = estimators.sample_percentile(y_data, 0.75)
    x_1_percentile = estimators.sample_percentile(x_data, 0.01)
    y_1_percentile = estimators.sample_percentile(y_data, 0.01)
    x_99_percentile = estimators.sample_percentile(x_data, 0.99)
    y_99_percentile = estimators.sample_percentile(y_data, 0.99)

    def likelihood(x): return (-1)*estimators.bivariate_normal_likelihood_function(params=x,
                                                                                   data=data)

    var_x_guess = (x_75_percentile - x_25_percentile)/2
    var_y_guess = (y_75_percentile - y_25_percentile)/2
    guess = [x_median, y_median, var_x_guess, var_y_guess, 0]
    var_x_bounds = x_99_percentile - x_1_percentile
    var_y_bounds = y_99_percentile - y_1_percentile
    cov_bounds = sqrt(var_x_bounds*var_y_bounds)

    params = optimize.minimize(fun=likelihood,
                               x0=guess,
                               bounds=[
                                   (None, None),
                                   (None, None),
                                   (0, var_x_bounds),
                                   (0, var_y_bounds),
                                   (-cov_bounds, cov_bounds)
                               ],
                               options={'disp': False},
                               method='Nelder-Mead')
    return params.x


def optimize_portfolio_variance(portfolio: Portfolio, target_return: float = None) -> List[float]:
    """
    Parameters
    ----------
    1. **portfolio**: `scrilla.analysis.objects.Portfolio`
        An instance of the `Portfolio` class. Must be initialized with an array of ticker symbols. Optionally, it can be initialized with a start_date and end_date datetime. If start_date and end_date are specified, the portfolio will be optimized over the stated time period. Otherwise, date range will default to range defined by `scrilla.settings.DEFAULT_ANALYSIS_PERIOD`.
    2. **target_return**: ``float``
        *Optional*. Defaults to `None`. The target return, as a decimal, subject to which the portfolio's volatility will be minimized.

    Returns
    -------
    `List[float]`
        A list of floats that represents the proportion of the portfolio that should be allocated to the corresponding ticker symbols given as a parameter within the portfolio object. In other words, if portfolio.tickers = ['AAPL', 'MSFT'] and the output is [0.25, 0.75], this result means a portfolio with 25% allocation in AAPL and a 75% allocation in MSFT will result in an optimally constructed portfolio with respect to its volatility.  
    """
    tickers = portfolio.tickers
    portfolio.set_target_return(target_return)

    init_guess = portfolio.get_init_guess()
    equity_bounds = portfolio.get_default_bounds()
    equity_constraint = {
        'type': 'eq',
        'fun': portfolio.get_constraint
    }

    if target_return is not None:
        logger.debug(
            f'Optimizing {tickers} Portfolio Volatility Subject To Return = {target_return}')

        return_constraint = {
            'type': 'eq',
            'fun': portfolio.get_target_return_constraint
        }
        portfolio_constraints = [equity_constraint, return_constraint]
    else:
        logger.debug(f'Minimizing {tickers} Portfolio Volatility')
        portfolio_constraints = equity_constraint

    allocation = optimize.minimize(fun=portfolio.volatility_function, x0=init_guess,
                                   method=constants.constants['OPTIMIZATION_METHOD'], bounds=equity_bounds,
                                   constraints=portfolio_constraints, options={'disp': False})

    return allocation.x


def optimize_conditional_value_at_risk(portfolio: Portfolio, prob: float, expiry: float, target_return: float = None) -> List[float]:
    """
    Parameters
    ----------
    1. **portfolio**: `scrilla.analysis.objects.Portfolio`
        An instance of the `Portfolio` class. Must be initialized with an array of ticker symbols. Optionally, it can be initialized with a start_date and end_date datetime. If start_date and end_date are specified, the portfolio will be optimized over the stated time period. Otherwise, date range will default to range defined by `scrilla.settings.DEFAULT_ANALYSIS_PERIOD`.
    2. **prob**: ``float``
        Probability of loss.
    3. **expiry**: ``float``
        Time horizon for the value at risk expectation, i.e. the time in the future at which point the portfolio will be considered "closed" and the hypothetical loss will occur. 
    4. **target_return**: ``float``
        *Optional*. Defaults to `None`. The target return constraint, as a decimal, subject to which the portfolio's conditional value at risk will be optimized.

    Returns
    -------
    ``list``
        A list of floats that represents the proportion of the portfolio that should be allocated to the corresponding ticker symbols given as a parameter within the `Portfolio` object. In other words, if `portfolio.tickers = ['AAPL', 'MSFT']` and the output to this function is `[0.25, 0.75]`, this result means a portfolio with 25% allocation in AAPL and a 75% allocation in MSFT will result in an optimally constructed portfolio with respect to its conditional value at risk. 

    """
    tickers = portfolio.tickers
    init_guess = portfolio.get_init_guess()
    equity_bounds = portfolio.get_default_bounds()

    equity_constraint = {
        'type': 'eq',
        'fun': portfolio.get_constraint
    }

    if target_return is not None:
        logger.debug(
            f'Optimizing {tickers} Portfolio Conditional Value at Risk Subject To Return = {target_return}')

        return_constraint = {
            'type': 'eq',
            'fun': portfolio.get_target_return_constraint
        }
        portfolio_constraints = [equity_constraint, return_constraint]
    else:
        logger.debug(
            f'Minimizing {tickers} Portfolio Conditional Value at Risk')
        portfolio_constraints = equity_constraint

    allocation = optimize.minimize(fun=lambda x: portfolio.conditional_value_at_risk_function(x, expiry, prob),
                                   x0=init_guess,
                                   method=constants.constants['OPTIMIZATION_METHOD'], bounds=equity_bounds,
                                   constraints=portfolio_constraints, options={'disp': False})

    return allocation.x


def maximize_sharpe_ratio(portfolio: Portfolio, target_return: float = None) -> List[float]:
    """
    Parameters
    ----------
    1. **portfolio**: `scrilla.analysis.objects.Portfolio`
        An instance of the `Portfolio` class. Must be initialized with an array of ticker symbols. Optionally, it can be initialized with a start_date and end_date datetime. If start_date and end_date are specified, the portfolio will be optimized over the stated time period. Otherwise, date range will default to range defined by `scrilla.settings.DEFAULT_ANALYSIS_PERIOD`.
    2. **target_return**: ``float``
        *Optional*. Defaults to `None`. The target return constraint, as a decimal, subject to which the portfolio's sharpe ratio will be maximized.

    Returns
    -------
    ``list``
        A list of floats that represents the proportion of the portfolio that should be allocated to the corresponding ticker symbols given as a parameter within the `Portfolio` object. In other words, if `portfolio.tickers = ['AAPL', 'MSFT']` and the output to this function is `[0.25, 0.75]`, this result means a portfolio with 25% allocation in AAPL and a 75% allocation in MSFT will result in an optimally constructed portfolio with respect to its sharpe ratio.  
    """
    tickers = portfolio.tickers
    portfolio.set_target_return(target_return)

    init_guess = portfolio.get_init_guess()
    equity_bounds = portfolio.get_default_bounds()
    equity_constraint = {
        'type': 'eq',
        'fun': portfolio.get_constraint
    }

    if target_return is not None:
        logger.debug(
            f'Optimizing {tickers} Portfolio Sharpe Ratio Subject To Return = {target_return}')

        return_constraint = {
            'type': 'eq',
            'fun': portfolio.get_target_return_constraint
        }
        portfolio_constraints = [equity_constraint, return_constraint]
    else:
        logger.debug(f'Maximizing {tickers} Portfolio Sharpe Ratio')
        portfolio_constraints = equity_constraint

    allocation = optimize.minimize(fun=lambda x: (-1)*portfolio.sharpe_ratio_function(x),
                                   x0=init_guess,
                                   method=constants.constants['OPTIMIZATION_METHOD'], bounds=equity_bounds,
                                   constraints=portfolio_constraints, options={'disp': False})

    return allocation.x


def maximize_portfolio_return(portfolio: Portfolio) -> List[float]:
    """
    Parameters
    ----------
    1. **portfolio**: `scrilla.analysis.objects.Portfolio`
        An instance of the Portfolio class. Must be initialized with an array of ticker symbols. Optionally, it can be initialized with a ``start_date`` and ``end_date`` ``datetime.date``. If ``start_date`` and ``end_date`` are specified, the portfolio will be optimized over the stated time period.

    Output
    ------
    ``List[float]``
        An array of floats that represents the proportion of the portfolio that should be allocated to the corresponding ticker symbols given as a parameter within the portfolio object to achieve the maximum return. Note, this function is often uninteresting because if the rate of return for equity A is 50% and the rate of return of equity B is 25%, the portfolio with a maximized return will always allocated 100% of its value to equity A. However, this function is useful for determining whether or not the optimization algorithm is actually working, so it has been left in the program for debugging purposes. 
    """
    tickers = portfolio.tickers
    init_guess = portfolio.get_init_guess()
    equity_bounds = portfolio.get_default_bounds()
    equity_constraint = {
        'type': 'eq',
        'fun': portfolio.get_constraint
    }

    logger.debug(f'Maximizing {tickers} Portfolio Return')
    allocation = optimize.minimize(fun=lambda x: (-1)*portfolio.return_function(x),
                                   x0=init_guess, method=constants.constants['OPTIMIZATION_METHOD'],
                                   bounds=equity_bounds, constraints=equity_constraint,
                                   options={'disp': False})

    return allocation.x


def calculate_efficient_frontier(portfolio: Portfolio, steps=None) -> List[List[float]]:
    """
    Parameters
    ----------
    1. **portfolio**: `scrilla.analysis.objects.Portfolio`
        An instance of the Portfolio class defined in  analysis.objects.portfolio. Must be initialized with an array of ticker symbols. Optionally, it can be initialized with a start_date and end_date datetime. If start_date and end_date are specified, the portfolio will be optimized over the stated time period.\n \n

    2. **steps**: ``int``
        *Optional*. Defaults to `None`. The number of points calculated in the efficient frontier. If none is provided, it defaults to the environment variable **FRONTIER_STEPS**.

    Returns
    -------
    ``List[List[float]]``
        A nested list of floats. Each float list corresponds to a point on a portfolio's efficient frontier, i.e. each list represents the percentage of a portfolio that should be allocated to the equity with the corresponding ticker symbol supplied as an attribute to the ``scrilla.analysis.objects.Portfolio`` object parameter.
    """
    if steps is None:
        steps = settings.FRONTIER_STEPS

    minimum_allocation = optimize_portfolio_variance(portfolio=portfolio)
    maximum_allocation = maximize_portfolio_return(portfolio=portfolio)

    minimum_return = portfolio.return_function(minimum_allocation)
    maximum_return = portfolio.return_function(maximum_allocation)
    return_width = (maximum_return - minimum_return)/steps

    frontier = []
    for i in range(steps+1):
        target_return = minimum_return + return_width*i
        allocation = optimize_portfolio_variance(
            portfolio=portfolio, target_return=target_return)
        frontier.append(allocation)

    return frontier
