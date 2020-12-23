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
        output.title_line('Optimal Percentage Allocation')
        output.array_percent_result('Optimal Portfolio Percentage Allocation', allocation.x, equities)
        output.line()

        if utilities.PORTFOLIO_MODE:
            investment = utilities.get_number_input("Please Enter Total Investment : \n")
            shares = optimal_portfolio.calculate_approximate_shares(allocation.x, investment)
            total = optimal_portfolio.calculate_actual_total(allocation.x, investment)
            output.line()

            output.title_line('Optimal Share Allocation')
            output.array_result('Optimal Portfolio Shares Allocation', shares, equities)
            output.title_line('Optimal Portfolio Value')
            output.scalar_result('Total', total)

        output.title_line('Risk-Return Profile')
        output.scalar_result('Return', optimal_portfolio.return_function(allocation.x))
        output.scalar_result('Volatility', optimal_portfolio.volatility_function(allocation.x))

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
        output.title_line('Optimal Percentage Allocation')
        output.array_percent_result('Optimal Portfolio Percentage Allocation', allocation.x, equities)
        output.line()

        if utilities.PORTFOLIO_MODE:
            investment = utilities.get_number_input("Please Enter Total Investment : \n")
            shares = optimal_portfolio.calculate_approximate_shares(allocation.x, investment)
            total = optimal_portfolio.calculate_actual_total(allocation.x, investment)
            output.line()

            output.title_line('Optimal Share Allocation')
            output.array_result('Optimal Portfolio Shares Allocation', shares, equities)
            output.title_line('Optimal Portfolio Value')
            output.scalar_result('Total', total)

        output.title_line('Risk-Return Profile')
        output.scalar_result('Return', optimal_portfolio.return_function(allocation.x))
        output.scalar_result('Volatility', optimal_portfolio.volatility_function(allocation.x))