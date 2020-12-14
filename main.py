import os, sys
import scipy.optimize as optimize
import app.utilities as utilities
import app.statistics as statistics
import app.portfolio as portfolio

if __name__ == "__main__": 
    output = utilities.Logger('app.pyfin.main')

    # clear previous price histories from cache
    # TODO: timestamp cache files and only delete if date != todays date
    filelist = [ f for f in os.listdir(utilities.BUFFER_DIR)]
    for f in filelist:
        os.remove(os.path.join(utilities.BUFFER_DIR, f))

    # retrieve function argument
    opt = sys.argv[1]

    # parse function and invoke
    if opt == utilities.FUNC_DICT["help"]:
        output.help()

    elif opt == utilities.FUNC_DICT["examples"]:
        # TODO: add function to utilities to print examples.
        pass

    else:
        args = sys.argv[2:]
        output.title_line('Results')
        output.line()

        if opt == utilities.FUNC_DICT["risk_return"]:
            if(len(args)>1) or len(args)==1:
                for arg in args:
                    result = statistics.calculate_risk_return(arg)
                    if result:
                        output.scalar_result(f'mean_{arg}', result['annual_return'])
                        output.scalar_result(f'vol_{arg}', result['annual_volatility'])
                    else:
                        output.debug('Error Encountered While Calculating. Try Again')
            
            else:
                output.debug('No Input Supplied. Try Again.')

        elif opt == utilities.FUNC_DICT["correlation"]:
            if(len(args) > 1):
                for i in range(len(args)):
                    for j in range(i+1, len(args)):
                        result = statistics.calculate_correlation(args[i], args[j]) 
                        if result:
                            output.scalar_result(f'correlation_{args[i]}_{args[j]}', result['correlation'])
                        else:
                            output.debug('Error Encountered While Calculating. Try Again.')


            else:
                output.debug('Invalid Input. Try Again.')

        elif opt == utilities.FUNC_DICT['minimize_variance']:
            if(len(args)>1):
                optimal_portfolio = portfolio.Portfolio(args)

                init_guess = optimal_portfolio.get_init_guess()
                equity_bounds = optimal_portfolio.get_default_bounds()
                equity_constraint = {
                    'type': 'eq',
                    'fun': optimal_portfolio.get_constraint
                }

                allocation = optimize.minimize(fun = optimal_portfolio.volatility_function, x0 = init_guess, 
                                            method='SLSQP', bounds=equity_bounds, constraints=equity_constraint, 
                                            options={'disp': False})

                output.array_result('Optimal Portfolio', allocation.x, args)
                output.title_line('Risk-Return Profile')
                output.scalar_result('Return', optimal_portfolio.return_function(allocation.x))
                output.scalar_result('Volatility', optimal_portfolio.volatility_function(allocation.x))

            else: 
                output.debug('Invalid Input. Try Again.')

        elif opt == utilities.FUNC_DICT['optimize_portfolio']:
            if (len(args)>1):
                try:
                    target_return = float(args[len(args)-1])
                    equities = args[:(len(args)-1)]

                    optimal_portfolio = portfolio.Portfolio(equities)
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
            
                    output.array_result('Optimal Portfolio', allocation.x, equities)
                    output.title_line('Risk-Return Profile')
                    output.scalar_result('Return', optimal_portfolio.return_function(allocation.x))
                    output.scalar_result('Volatility', optimal_portfolio.volatility_function(allocation.x))
                
                except: 
                    e = sys.exc_info()[0]
                    f = sys.exc_info()[1]
                    g = sys.exc_info()[2]
                    output.debug(f'{e} {f} {g}')
                    output.comment('No Target Return Specified. Try Again.')
            
            else: 
                output.comment('Invalid Input. Try Again.')

        elif opt == utilities.FUNC_DICT['efficient_frontier']:
            # TODO: calculate minimum variance portfolio
            # TODO: calculate maximum return portfolio, i.e. determine which equity has largest return
            # TODO: return point = (maximum return - minimum variance return)/n * i + minimum variance return 
                # and then optimize for each target return
            pass
        else:
            output.comment('No Function Supplied. Please Review Function Summary Below And Re-execute Script.')
            output.help()
        
        output.line()
