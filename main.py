import os, sys
import datetime
import scipy.optimize as optimize

import app.settings as settings
import app.statistics as statistics
import app.optimizer as optimizer
import app.services as services

from app.portfolio import Portfolio

import util.helpers as helper
import util.logger as logger

if __name__ == "__main__": 
    output = logger.Logger('app.pyfin.main')
    
    helper.clear_cache()

    # retrieve function argument
    opt = sys.argv[1]

    # parse function and invoke
    if opt == settings.FUNC_ARG_DICT["help"]:
        output.help()

    elif opt == settings.FUNC_ARG_DICT["examples"]:
        output.examples()

    else:
        args = sys.argv[2:]
        output.title_line('Results')
        output.line()

        if opt == settings.FUNC_ARG_DICT["correlation"]:
            if(len(args) > 1):
                for i in range(len(args)):
                    for j in range(i+1, len(args)):
                        result = statistics.calculate_correlation(args[i], args[j]) 
                        if result:
                            output.scalar_result(f'correlation_{args[i]}_{args[j]}', result['correlation'])
                        else:
                            output.comment('Error Encountered While Calculating. Try -ex Flag For Example Usage.')

            else:
                output.comment('Invalid Input. Try -ex Flag For Example Usage.')

        elif opt == settings.FUNC_ARG_DICT["crypto_spot"]:
            if(len(args)>1) or len(args)==1:
                for arg in args:
                    price = services.get_daily_price_latest(arg, settings.ASSET_CRYPTO)
                    output.scalar_result(arg, float(price))
                
            else:
                output.comment('Error Encountered While Calculating. Try -ex Flag For Example Usage.')
        
        elif opt == settings.FUNC_ARG_DICT["economic_statistics"]:
            if(len(args)>1) or len(args)==1:
                stats = services.get_daily_stats_latest(args)
                for i in range(len(stats)):
                    output.scalar_result(args[i], stats[i])
                
            else:
                output.comment('Error Encountered While Calculating. Try -ex Flag For Example Usage.')

        elif opt == settings.FUNC_ARG_DICT['efficient_frontier']:
            if(len(args)>1):
                frontier = optimizer.calculate_efficient_frontier(equities=args)
                output.efficient_frontier(portfolio=Portfolio(args), frontier=frontier)
            
            else: 
                output.debug('Invalid Input. Try -ex Flag For Example Usage.')

        elif opt == settings.FUNC_ARG_DICT["equity_spot"]:
            if(len(args)>1) or len(args)==1:
                for arg in args:
                    price = services.get_daily_price_latest(arg, settings.ASSET_EQUITY)
                    output.scalar_result(arg, float(price))
                
            else:
                output.comment('Error Encountered While Calculating. Try -ex Flag For Example Usage.')
        
        elif opt == settings.FUNC_ARG_DICT['maximize_return']:
            if (len(args)>1):
                allocation = optimizer.maximize_portfolio_return(equities=args)
                output.optimal_result(portfolio=Portfolio(args), allocation=allocation)

            else:
                output.comment('Invalid Input. Try -ex Flag For Example Usage.')
                
        elif opt == settings.FUNC_ARG_DICT['minimize_variance']:
            if(len(args)>1):
                allocation = optimizer.minimize_portfolio_variance(equities=args)
                output.optimal_result(portfolio=Portfolio(args), allocation=allocation)
            else: 
                output.comment('Invalid Input. Try -ex Flag For Example Usage.')

        elif opt == settings.FUNC_ARG_DICT['moving_averages']:
            if(len(args)>1) or len(args)==1:
                moving_averages = statistics.calculate_moving_averages(args)
                output.moving_average_result(args, moving_averages)

            else: 
                output.comment('Invalid Input. Try -ex Flag For Example Usage.')

        elif opt == settings.FUNC_ARG_DICT['optimize_portfolio']:
            if (len(args)>1):
                try:
                    target_return = float(args[len(args)-1])
                    equities = args[:(len(args)-1)]

                    allocation = optimizer.optimize_portfolio(equities=equities, target_return=target_return)   
                    output.optimal_result(portfolio=Portfolio(equities), allocation=allocation)

                except: 
                    e = sys.exc_info()[0]
                    f = sys.exc_info()[1]
                    g = sys.exc_info()[2]
                    output.debug(f'{e} {f} {g}')
                    output.comment('No Target Return Specified. Try -ex Flag For Example Usage.')
            
            else: 
                output.comment('Invalid Input. Try -ex Flag For Example Usage.')
        
        elif opt == settings.FUNC_ARG_DICT['plot_frontier']:
            if(len(args)>1):
                frontier = optimizer.calculate_efficient_frontier(equities=args)
                output.plot_frontier(portfolio=Portfolio(args), frontier=frontier)
            
            else: 
                output.debug('Invalid Input. Try Try -ex Flag For Example Usage.')

        elif opt == settings.FUNC_ARG_DICT['plot_moving_averages']:
            if(len(args)>1) or len(args)==1:
                moving_averages = statistics.calculate_moving_averages(args)
                output.plot_moving_averages(args, moving_averages)
            else:
                output.debug('Invalid Input. Try Try -ex Flag For Example Usage.')

        elif opt == settings.FUNC_ARG_DICT["risk_return"]:
            if(len(args)>1) or len(args)==1:
                for arg in args:
                    result = statistics.calculate_risk_return(arg)
                    if result:
                        output.scalar_result(f'mean_{arg}', result['annual_return'])
                        output.scalar_result(f'vol_{arg}', result['annual_volatility'])

                    else:
                        output.comment('Error Encountered While Calculating. Try -ex Flag For Example Usage.')
            
            else:
                output.comment('No Input Supplied. Try -ex Flag For Example Usage.')

        else:
            output.comment('No Function Supplied. Please Review Function Summary Below And Re-execute Script With Appropriate Arguments.')
            output.help()
        
        output.line()
