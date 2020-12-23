from app.portfolio import Portfolio
import app.utilities as utilities
import scipy.optimize as optimize
output = utilities.Logger('app.pyfin.optimizer')

def optimize_portfolio(equities, target_return, display):
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

    allocation = optimize.minimize(fun = optimal_portfolio.volatility_function, x0 = init_guess, 
                                    method='SLSQP', bounds=equity_bounds, constraints=portfolio_constraints, 
                                    options={'disp': False})

    if display:
        output.optimal_result(optimal_portfolio, allocation.x)

    return allocation.x

def minimize_portfolio_variance(equities, display):
    optimal_portfolio = Portfolio(equities)

    init_guess = optimal_portfolio.get_init_guess()
    equity_bounds = optimal_portfolio.get_default_bounds()
    equity_constraint = {
        'type': 'eq',
        'fun': optimal_portfolio.get_constraint
    }

    allocation = optimize.minimize(fun = optimal_portfolio.volatility_function, x0 = init_guess, 
                                    method='SLSQP', bounds=equity_bounds, constraints=equity_constraint, 
                                    options={'disp': False})

    if display:
        output.optimal_result(optimal_portfolio, allocation.x)
    
    return allocation.x

def maximize_portfolio_return(equities, display):
    optimal_portfolio = Portfolio(equities)

    init_guess = optimal_portfolio.get_init_guess()
    equity_bounds = optimal_portfolio.get_default_bounds()
    equity_constraint = {
        'type': 'eq',
        'fun': optimal_portfolio.get_constraint
    }

    minimize_function = lambda x: (-1)*optimal_portfolio.return_function(x)
    allocation = optimize.minimize(fun = minimize_function, x0 = init_guess, method='SLSQP',
                                    bounds=equity_bounds, constraints=equity_constraint, 
                                    options={'disp': False})

    if display:
        output.optimal_result(optimal_portfolio, allocation.x)
    
    return allocation.x