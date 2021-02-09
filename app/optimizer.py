import scipy.optimize as optimize

from app.portfolio import Portfolio
import app.settings as settings
import util.logger as logger

output = logger.Logger('app.optimizer')

def optimize_portfolio(portfolio, target_return):
    tickers = portfolio.get_assets()
    portfolio.set_target_return(target_return)

    init_guess = portfolio.get_init_guess()
    equity_bounds = portfolio.get_default_bounds()
    equity_constraint = {
            'type': 'eq',
            'fun': portfolio.get_constraint
        }
    return_constraint = {
        'type': 'eq',
        'fun': portfolio.get_target_return_constraint
    }
    portfolio_constraints = [equity_constraint, return_constraint]

    output.debug(f'Optimizing {tickers} Portfolio Risk Subject To Return = {target_return}')
    allocation = optimize.minimize(fun = portfolio.volatility_function, x0 = init_guess, 
                                    method=settings.OPTIMIZATION_METHOD, bounds=equity_bounds, 
                                    constraints=portfolio_constraints, options={'disp': False})

    return allocation.x

def minimize_portfolio_variance(portfolio):
    tickers = portfolio.get_assets()
    init_guess = portfolio.get_init_guess()
    equity_bounds = portfolio.get_default_bounds()
    equity_constraint = {
        'type': 'eq',
        'fun': portfolio.get_constraint
    }

    output.debug(f'Minimizing {tickers} Portfolio Risk')
    allocation = optimize.minimize(fun = portfolio.volatility_function, x0 = init_guess, 
                                    method=settings.OPTIMIZATION_METHOD, bounds=equity_bounds, 
                                    constraints=equity_constraint, options={'disp': False})

    return allocation.x

def maximize_portfolio_return(portfolio):
    tickers = portfolio.get_assets()
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
    tickers = portfolio.get_assets()
    minimum_allocation = minimize_portfolio_variance(portfolio=portfolio)
    maximum_allocation = maximize_portfolio_return(portfolio=portfolio)

    minimum_return = portfolio.return_function(minimum_allocation)
    maximum_return = portfolio.return_function(maximum_allocation)
    return_width = (maximum_return - minimum_return)/settings.FRONTIER_STEPS

    frontier=[]
    for i in range(settings.FRONTIER_STEPS+1):
        target_return = minimum_return + return_width*i

        output.debug(f'Optimizing {tickers} Portfolio Return Subject To {target_return}')
        allocation = optimize_portfolio(portfolio=portfolio, target_return=target_return)
        
        frontier.append(allocation)
        
    return frontier