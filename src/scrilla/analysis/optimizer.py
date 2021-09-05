import scipy.optimize as optimize

import settings
import util.outputter as outputter

logger = outputter.Logger('optimizer', settings.LOG_LEVEL)

def optimize_portfolio_variance(portfolio, target_return=None):
    """
    Parameters
    ----------
    1. portfolio : Portfolio \n
        An instance of the Portfolio class defined in  objects.portfolio. Must be initialized with an array of ticker symbols. Optionally, it can be initialized with a start_date and end_date datetime. If start_date and end_date are specified, the portfolio will be optimized over the stated time period.\n \n
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
                                    method=settings.OPTIMIZATION_METHOD, bounds=equity_bounds, 
                                    constraints=portfolio_constraints, options={'disp': False})

    return allocation.x

def optimize_conditional_value_at_risk(portfolio, prob, expiry, target_return=None):
    """
    Parameters
    ----------
    1, portfolio : Portfolio \n
        An instance of the Portfolio class defined in  objects.portfolio. Must be initialized with an array of ticker symbols. Optionally, it can be initialized with a start_date and end_date datetime. If start_date and end_date are specified, the portfolio will be optimized over the stated time period.\n \n
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
                                    method=settings.OPTIMIZATION_METHOD, bounds=equity_bounds, 
                                    constraints=portfolio_constraints, options={'disp': False})

    return allocation.x

def maximize_sharpe_ratio(portfolio, target_return=None):
    """
    Parameters
    ----------
    1. portfolio : Portfolio \n
        An instance of the Portfolio class defined in  objects.portfolio. Must be initialized with an array of ticker symbols. Optionally, it can be initialized with a start_date and end_date datetime. If start_date and end_date are specified, the portfolio will be optimized over the stated time period.\n \n
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
                                    method=settings.OPTIMIZATION_METHOD, bounds=equity_bounds, 
                                    constraints=portfolio_constraints, options={'disp': False})

    return allocation.x

def maximize_portfolio_return(portfolio):
    """
    Parameters
    ----------
    * portfolio : Portfolio \n
        An instance of the Portfolio class defined in  objects.portfolio. Must be initialized with an array of ticker symbols. Optionally, it can be initialized with a start_date and end_date datetime. If start_date and end_date are specified, the portfolio will be optimized over the stated time period.\n \n

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
                                    x0 = init_guess, method=settings.OPTIMIZATION_METHOD,
                                    bounds=equity_bounds, constraints=equity_constraint, 
                                    options={'disp': False})

    return allocation.x

def calculate_efficient_frontier(portfolio, steps=None):
    """
    Parameters
    ----------
    1. portfolio : Portfolio \n
        An instance of the Portfolio class defined in  objects.portfolio. Must be initialized with an array of ticker symbols. Optionally, it can be initialized with a start_date and end_date datetime. If start_date and end_date are specified, the portfolio will be optimized over the stated time period.\n \n

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