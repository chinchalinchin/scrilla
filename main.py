import os, sys
import scipy.optimize as optimize
import app.utilities as utilities
import app.statistics as statistics
import app.portfolio as portfolio

if __name__ == "__main__": 
    output = utilities.Logger('app.pyfin.main')

    # Clear previous price histories from buffer
    filelist = [ f for f in os.listdir(utilities.BUFFER_DIR)]
    for f in filelist:
        os.remove(os.path.join(utilities.BUFFER_DIR, f))

    opt = sys.argv[1]
    if opt == utilities.FUNC_DICT["help"]:
        output.help()
    
    else:
        args = sys.argv[2:]
        output.title_line('Results')
        output.line()

        if opt == utilities.FUNC_DICT["statistics"]:
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

        if opt == utilities.FUNC_DICT["correlation"]:
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

        if opt == utilities.FUNC_DICT['optimize']:
            if(len(args)>1):
                optimal_portfolio = portfolio.Portfolio(args)

                init_guess = optimal_portfolio.get_init_guess()
                equity_bounds = optimal_portfolio.get_bounds(args)
                equity_constraints = {
                    'type': 'eq',
                    'fun': optimal_portfolio.get_constraint
                }

                allocation = optimize.minimize(fun = optimal_portfolio.volatility_function, x0 = init_guess, 
                                            method='SLSQP', bounds=equity_bounds, constraints=equity_constraints, 
                                            options={'disp': False})
                output.array_result('Optimal Portfolio', allocation.x, args)

            else: 
                output.debug('Invalid Input. Try Again.')
        
        output.line()
