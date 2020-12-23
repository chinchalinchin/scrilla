import os, sys
import datetime
import scipy.optimize as optimize
import app.utilities as utilities
import app.statistics as statistics
import app.portfolio as portfoli
import app.optimizer as optimizer

if __name__ == "__main__": 
    output = utilities.Logger('app.pyfin.main')
    now = datetime.datetime.now()
    
    # clear previous price histories from cache
    filelist = [ f for f in os.listdir(utilities.BUFFER_DIR)]
    timestamp = '{}{}{}'.format(now.month, now.day, now.year)
    for f in filelist:
        filename = os.path.basename(f)
        if filename != ".gitkeep" and timestamp not in filename:
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
                optimizer.minimize_portfolio_variance(equities=args, display=True)

            else: 
                output.debug('Invalid Input. Try Again.')

        elif opt == utilities.FUNC_DICT['optimize_portfolio']:
            if (len(args)>1):
                try:
                    target_return = float(args[len(args)-1])
                    equities = args[:(len(args)-1)]

                    optimizer.optimize_portfolio(equities=equities, target_return=target_return, display=True)   
                                 
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
