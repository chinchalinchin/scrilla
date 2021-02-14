import scipy.optimize as optimize

from app.objects.portfolio import Portfolio
import app.settings as settings
import util.logger as logger

output = logger.Logger('app.optimizer', settings.LOG_LEVEL)

def optimize_portfolio_variance(portfolio, target_return=None):
    """
    Parameters
    ----------
    * portfolio : Portfolio \n
        An instance of the Portfolio class defined in app.portfolio. Must be initialized with an array of ticker symbols. Optionally, it can be initialized with a start_date and end_date datetime. If start_date and end_date are specified, the portfolio will be optimized over the stated time period.\n \n
    * target_return : float \n
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
        output.debug(f'Optimizing {tickers} Portfolio Volatility Subject To Return = {target_return}')

        return_constraint = {
            'type': 'eq',
            'fun': portfolio.get_target_return_constraint
        }
        portfolio_constraints = [equity_constraint, return_constraint]
    else:
        output.debug(f'Minimizing {tickers} Portfolio Volatility')
        portfolio_constraints = equity_constraint

    allocation = optimize.minimize(fun = portfolio.volatility_function, x0 = init_guess, 
                                    method=settings.OPTIMIZATION_METHOD, bounds=equity_bounds, 
                                    constraints=portfolio_constraints, options={'disp': False})

    return allocation.x

def maximize_portfolio_return(portfolio):
    """
    Parameters
    ----------
    * portfolio : Portfolio \n
        An instance of the Portfolio class defined in app.portfolio. Must be initialized with an array of ticker symbols. Optionally, it can be initialized with a start_date and end_date datetime. If start_date and end_date are specified, the portfolio will be optimized over the stated time period.\n \n

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
    maximize_function = lambda x: (-1)*portfolio.return_function(x)
    
    output.debug(f'Maximizing {tickers} Portfolio Return')
    allocation = optimize.minimize(fun = maximize_function, x0 = init_guess, method='SLSQP',
                                    bounds=equity_bounds, constraints=equity_constraint, 
                                    options={'disp': False})

    return allocation.x

def calculate_efficient_frontier(portfolio):
    """
    Parameters
    ----------
    * portfolio : Portfolio \n
        An instance of the Portfolio class defined in app.portfolio. Must be initialized with an array of ticker symbols. Optionally, it can be initialized with a start_date and end_date datetime. If start_date and end_date are specified, the portfolio will be optimized over the stated time period.\n \n

    Output
    ------
    An array of float arrays. Each float array corresponds to a point on a portfolio's efficient frontier, i.e. each array represents the percentage of a portfolio that should be allocated to the equity to the corresponding ticker symbol (supplied as an attribute portfolio parameter, portfolio.tickers) in order to produce a given rate of return with minimal volatility.
    """
    tickers = portfolio.tickers
    minimum_allocation = optimize_portfolio_variance(portfolio=portfolio)
    maximum_allocation = maximize_portfolio_return(portfolio=portfolio)

    minimum_return = portfolio.return_function(minimum_allocation)
    maximum_return = portfolio.return_function(maximum_allocation)
    return_width = (maximum_return - minimum_return)/settings.FRONTIER_STEPS

    frontier=[]
    for i in range(settings.FRONTIER_STEPS+1):
        target_return = minimum_return + return_width*i

        output.debug(f'Optimizing {tickers} Portfolio Return Subject To {target_return}')
        allocation = optimize_portfolio_variance(portfolio=portfolio, target_return=target_return)
        
        frontier.append(allocation)
        
    return frontier