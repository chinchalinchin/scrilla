import scipy.optimize as optimize

from app.portfolio import Portfolio
import app.settings as settings
import util.logger as logger

output = logger.Logger('app.optimizer')

def optimize_portfolio(equities, target_return):
    optimal_portfolio = Portfolio(equities)
    optimal_portfolio.set_target_return(target_return)

    init_guess = optimal_portfolio.get_init_guess()
    equity_bounds = optimal_portfolio.get_default_bounds()
    equity_constraint = {
            'type': 'eq',
            'fun': optimal_portfolio.get_constraint
        }
    return_constraint = {
        'type': 'eq',
        'fun': optimal_portfolio.get_target_return_constraint
    }
    portfolio_constraints = [equity_constraint, return_constraint]

    output.debug(f'Optimizing {equities} Portfolio Risk Subject To Return = {target_return}')
    allocation = optimize.minimize(fun = optimal_portfolio.volatility_function, x0 = init_guess, 
                                    method='SLSQP', bounds=equity_bounds, constraints=portfolio_constraints, 
                                    options={'disp': False})

    return allocation.x

def minimize_portfolio_variance(equities):
    optimal_portfolio = Portfolio(equities)

    init_guess = optimal_portfolio.get_init_guess()
    equity_bounds = optimal_portfolio.get_default_bounds()
    equity_constraint = {
        'type': 'eq',
        'fun': optimal_portfolio.get_constraint
    }

    output.debug(f'Minimizing {equities} Portfolio Risk')
    allocation = optimize.minimize(fun = optimal_portfolio.volatility_function, x0 = init_guess, 
                                    method='SLSQP', bounds=equity_bounds, constraints=equity_constraint, 
                                    options={'disp': False})

    return allocation.x

def maximize_portfolio_return(equities):
    optimal_portfolio = Portfolio(equities)

    init_guess = optimal_portfolio.get_init_guess()
    equity_bounds = optimal_portfolio.get_default_bounds()
    equity_constraint = {
        'type': 'eq',
        'fun': optimal_portfolio.get_constraint
    }
    maximize_function = lambda x: (-1)*optimal_portfolio.return_function(x)
    
    output.debug(f'Maximizing {equities} Portfolio Return')
    allocation = optimize.minimize(fun = maximize_function, x0 = init_guess, method='SLSQP',
                                    bounds=equity_bounds, constraints=equity_constraint, 
                                    options={'disp': False})

    return allocation.x

def calculate_efficient_frontier(equities):
    optimal_portfolio = Portfolio(equities)
    minimum_allocation = minimize_portfolio_variance(equities=equities)
    maximum_allocation = maximize_portfolio_return(equities=equities)

    minimum_return = optimal_portfolio.return_function(minimum_allocation)
    maximum_return = optimal_portfolio.return_function(maximum_allocation)
    return_width = (maximum_return - minimum_return)/settings.FRONTIER_STEPS

    frontier=[]
    for i in range(settings.FRONTIER_STEPS+1):
        target_return = minimum_return + return_width*i

        output.debug(f'Optimizing {equities} Portfolio Return Subject To {target_return}')
        allocation = optimize_portfolio(equities=equities, target_return=target_return)
        
        frontier.append(allocation)
        
    return frontier