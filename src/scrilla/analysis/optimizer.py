
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
import scipy.optimize as optimize
from scrilla import static, settings
from scrilla.analysis import estimators
import scrilla.util.outputter as outputter

logger = outputter.Logger('optimizer', settings.LOG_LEVEL)

"""
A module of functions that wrap around `scipy.optimize` in order to optimize statistical and financial functions of interest.
"""
def maximize_univariate_normal_likelihood(data):
    """
    Maximizes the normal (log-)likelihood of the sample with respect to the mean and volatility in order to estimate the mean and volatility of the population distribution described by the sample.

    Parameters
    ----------
    1. **data**: ``list``
        Sample of data drawn from a univariate normal population. 

    Returns
    -------
    ``list`` : A list containing the maximum likelihood estimates of the normal distribution's parameters. The first element of the list corresponds to the mean and the second element corresponds to the volatility.

    .. notes::
        * Some comments about the methodology. This module assumes an underlying asset price process that follows Geometric Brownian motion. This implies the return on the asset over intervals of  \\(\delta t\\) is normally distributed with mean \\(\mu * \delta t\\) and volatility \\(\sigma \cdot \sqrt{\delta t}\\). If the sample is scaled by \\(\delta t\\), then the mean becomes \\(\mu\\) and the volatility \\(\frac{\sigma}{\sqrt t}\\).  Moreover, increments are independent. Therefore, if the observations are made over equally spaced intervals, each observation is drawn from an independent, identially distributed normal random variable. The parameters \\(\mu\\) and :\\(\frac {\sigma}{\delta t}\\) can then be estimated by maximizing the probability of observing a given sample with respect to the parameters. To obtain the estimate for \\(\sigma\\), multiply the result of this function by \\(\delta t\\).
        * Theoretically, the output of this function should equal the same value obtained from the method of moment matching. However, there is a small discrepancy. It could be due to floating point arthimetic. However, see Section 2.2 of the following for what I think may be, if not the source, at least related to the `issue`_
        The author, however, is not considering the transformed Ito process, the log of the asset price process. It seems like his conclusion may be an artifact of Ito's Lemma? Not sure. Will need to think.

        .. _issue: https://www.researchgate.net/publication/5071468_Maximum_Likelihood_Estimation_of_Generalized_Ito_Processes_With_Discretely-Sampled_Data
    """

    likelihood = lambda x: (-1)*estimators.univariate_normal_likelihood_function(params=x, data=data)

    # make an educated guess
    first_quartile = estimators.sample_percentile(data=data, percentile=0.25)
    median = estimators.sample_percentile(data=data, percentile=0.5)
    third_quartile = estimators.sample_percentile(data, percentile=0.75)
    guess = [median, (third_quartile-first_quartile)/2]

    params = optimize.minimize(fun = likelihood, x0 = guess, options={'disp': False},
                                    method=static.constants['OPTIMIZATION_METHOD'])
    return params.x

def maximize_bivariate_normal_likelihood(data):
    """

    .. warning ::
        This does not work. Son of a gun.

    """

    x_data = [ datum[0] for datum in data ]
    y_data = [ datum[1] for datum in data ] 
    
    # x_estimates = maximize_univariate_normal_likelihood(data=x_data)
    # y_estimates = maximize_univariate_normal_likelihood(data=y_data)
    x_25_percentile = estimators.sample_percentile(x_data, 0.25)
    y_25_percentile = estimators.sample_percentile(y_data, 0.25)
    x_median = estimators.sample_percentile(x_data, 0.5)
    y_median = estimators.sample_percentile(y_data, 0.5)
    x_75_percentile = estimators.sample_percentile(x_data, 0.75)
    y_75_percentile = estimators.sample_percentile(y_data, 0.75)
    # knowns = [ x_estimates[0], y_estimates[0], x_estimates[1], y_estimates[1] ]

    likelihood = lambda x : (-1)*estimators.bivariate_normal_likelihood_function(params=x, 
                                                                                data=data)

    var_x_guess = (x_75_percentile - x_25_percentile)/2
    var_y_guess = (y_75_percentile - y_25_percentile)/2
    guess = [ x_median, y_median, var_x_guess, var_y_guess, 0]

    params = optimize.minimize(fun = likelihood, 
                                x0 = guess,
                                options ={'disp': False},
                                method=static.constants['OPTIMIZATION_METHOD'])
    print(params.x)
    return params.x
    
def optimize_portfolio_variance(portfolio, target_return=None):
    """
    Parameters
    ----------
    1. portfolio : Portfolio \n
        An instance of the Portfolio class defined in  analysis.objects.portfolio. Must be initialized with an array of ticker symbols. Optionally, it can be initialized with a start_date and end_date datetime. If start_date and end_date are specified, the portfolio will be optimized over the stated time period.\n \n
    2. target_return : float \n
        The target return, as a decimal, subject to which the portfolio's volatility will be minimized.

    Output
    ------
    An array of floats that represents the proportion of the portfolio that should be allocated to the corresponding ticker symbols given as a parameter within the portfolio object. In other words, if portfolio.tickers = ['AAPL', 'MSFT'] and the output is [0.25, 0.75], this result means a portfolio with 25% allocation in AAPL and a 75% allocation in MSFT will result in an optimally constructed portfolio with respect to its volatility.  
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
        logger.debug(f'Optimizing {tickers} Portfolio Volatility Subject To Return = {target_return}')

        return_constraint = {
            'type': 'eq',
            'fun': portfolio.get_target_return_constraint
        }
        portfolio_constraints = [equity_constraint, return_constraint]
    else:
        logger.debug(f'Minimizing {tickers} Portfolio Volatility')
        portfolio_constraints = equity_constraint

    allocation = optimize.minimize(fun = portfolio.volatility_function, x0 = init_guess, 
                                    method=static.constants['OPTIMIZATION_METHOD'], bounds=equity_bounds, 
                                    constraints=portfolio_constraints, options={'disp': False})

    return allocation.x

def optimize_conditional_value_at_risk(portfolio, prob, expiry, target_return=None):
    """
    Parameters
    ----------
    1, portfolio : Portfolio \n
        An instance of the Portfolio class defined in  analysis.objects.portfolio. Must be initialized with an array of ticker symbols. Optionally, it can be initialized with a start_date and end_date datetime. If start_date and end_date are specified, the portfolio will be optimized over the stated time period.\n \n
    2. prob: float \n
        Confidence level for value at risk. \n \n
    3. expiry: float \n
        Time horizon for the value at risk expectation, i.e. the time in the future at which point the portfolio will be considered 'closed'. 
    """
    tickers = portfolio.tickers
    init_guess = portfolio.get_init_guess()
    equity_bounds = portfolio.get_default_bounds()

    equity_constraint = {
            'type': 'eq',
            'fun': portfolio.get_constraint
    }

    if target_return is not None:
        logger.debug(f'Optimizing {tickers} Portfolio Conditional Value at Risk Subject To Return = {target_return}')

        return_constraint = {
            'type': 'eq',
            'fun': portfolio.get_target_return_constraint
        }
        portfolio_constraints = [equity_constraint, return_constraint]
    else:
        logger.debug(f'Minimizing {tickers} Portfolio Conditional Value at Risk')
        portfolio_constraints = equity_constraint

    allocation = optimize.minimize(fun = lambda x: portfolio.conditional_value_at_risk_function(x, expiry, prob), 
                                    x0 = init_guess, 
                                    method=static.constants['OPTIMIZATION_METHOD'], bounds=equity_bounds, 
                                    constraints=portfolio_constraints, options={'disp': False})

    return allocation.x

def maximize_sharpe_ratio(portfolio, target_return=None):
    """
    Parameters
    ----------
    1. portfolio : Portfolio \n
        An instance of the Portfolio class defined in  analysis.objects.portfolio. Must be initialized with an array of ticker symbols. Optionally, it can be initialized with a start_date and end_date datetime. If start_date and end_date are specified, the portfolio will be optimized over the stated time period.\n \n
    2. target_return : float \n
        The target return, as a decimal, subject to which the portfolio's volatility will be minimized.

    Output
    ------
    An array of floats that represents the proportion of the portfolio that should be allocated to the corresponding ticker symbols given as a parameter within the portfolio object. In other words, if portfolio.tickers = ['AAPL', 'MSFT'] and the output is [0.25, 0.75], this result means a portfolio with 25% allocation in AAPL and a 75% allocation in MSFT will result in an optimally constructed portfolio with respect to its sharpe ratio.  
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
        logger.debug(f'Optimizing {tickers} Portfolio Sharpe Ratio Subject To Return = {target_return}')

        return_constraint = {
            'type': 'eq',
            'fun': portfolio.get_target_return_constraint
        }
        portfolio_constraints = [equity_constraint, return_constraint]
    else:
        logger.debug(f'Maximizing {tickers} Portfolio Sharpe Ratio')
        portfolio_constraints = equity_constraint

    allocation = optimize.minimize(fun = lambda x: (-1)*portfolio.sharpe_ratio_function(x), 
                                    x0 = init_guess, 
                                    method=static.constants['OPTIMIZATION_METHOD'], bounds=equity_bounds, 
                                    constraints=portfolio_constraints, options={'disp': False})

    return allocation.x

def maximize_portfolio_return(portfolio):
    """
    Parameters
    ----------
    * portfolio : Portfolio \n
        An instance of the Portfolio class defined in  analysis.objects.portfolio. Must be initialized with an array of ticker symbols. Optionally, it can be initialized with a start_date and end_date datetime. If start_date and end_date are specified, the portfolio will be optimized over the stated time period.\n \n

    Output
    ------
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
    allocation = optimize.minimize(fun = lambda x: (-1)*portfolio.return_function(x),
                                    x0 = init_guess, method=static.constants['OPTIMIZATION_METHOD'],
                                    bounds=equity_bounds, constraints=equity_constraint, 
                                    options={'disp': False})

    return allocation.x

def calculate_efficient_frontier(portfolio, steps=None):
    """
    Parameters
    ----------
    1. portfolio : Portfolio \n
        An instance of the Portfolio class defined in  analysis.objects.portfolio. Must be initialized with an array of ticker symbols. Optionally, it can be initialized with a start_date and end_date datetime. If start_date and end_date are specified, the portfolio will be optimized over the stated time period.\n \n

    2. steps : int \n
        The number of points calculated in the efficient frontier. If none is provided, it defaults to the environment variable FRONTIER_STEPS.
    Output
    ------
    An array of float arrays. Each float array corresponds to a point on a portfolio's efficient frontier, i.e. each array represents the percentage of a portfolio that should be allocated to the equity to the corresponding ticker symbol (supplied as an attribute portfolio parameter, portfolio.tickers) in order to produce a given rate of return with minimal volatility.
    """
    if steps is None:
        steps = settings.FRONTIER_STEPS

    minimum_allocation = optimize_portfolio_variance(portfolio=portfolio)
    maximum_allocation = maximize_portfolio_return(portfolio=portfolio)

    minimum_return = portfolio.return_function(minimum_allocation)
    maximum_return = portfolio.return_function(maximum_allocation)
    return_width = (maximum_return - minimum_return)/steps

    frontier=[]
    for i in range(steps+1):
        target_return = minimum_return + return_width*i
        allocation = optimize_portfolio_variance(portfolio=portfolio, target_return=target_return)
        frontier.append(allocation)
        
    return frontier