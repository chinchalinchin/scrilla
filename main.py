import os, sys
import datetime
import scipy.optimize as optimize

from PySide6 import QtWidgets

import app.settings as settings
import app.statistics as statistics
import app.optimizer as optimizer
import app.services as services
import app.markets as markets

from app.portfolio import Portfolio

import gui.menu as menu

import util.helpers as helper
import util.logger as logger

output = logger.Logger('main')


if __name__ == "__main__": 

    if len(sys.argv)>0:
        output.debug('Parsing and invoking command line arguments')
        opt = sys.argv[1]
        
        # single argument functions
        if opt == settings.FUNC_ARG_DICT["help"]:
            output.help()

        elif opt == settings.FUNC_ARG_DICT["examples"]:
            output.examples()

        elif opt == settings.FUNC_ARG_DICT["purge"]:
            output.comment(f'Clearing {settings.STATIC_DIR} and {settings.CACHE_DIR}')
            helper.clear_dir(directory=settings.STATIC_DIR, retain=True)
            helper.clear_dir(directory=settings.CACHE_DIR, retain=True)

        elif opt == settings.FUNC_ARG_DICT["gui"]:
            app = QtWidgets.QApplication([])

            widget = menu.MenuWidget()
            widget.resize(settings.GUI_WIDTH, settings.GUI_HEIGHT)
            widget.show()

            sys.exit(app.exec_())

        # variable argument functions
        else:
            output.debug('Clearing /cache/ directory')
            helper.clear_cache(outdated_only=True)

            output.debug('Initialzing /static/ directory, if applicable')
            services.init_static_data()
            
            args = sys.argv[2:]
            output.title_line('Results')
            output.line()

            # Asset Grouping
            if opt == settings.FUNC_ARG_DICT['asset_type']:
                for arg in args:
                    asset_type = markets.get_asset_type(arg)
                    if asset_type:
                        output.string_result(f'asset_type({arg})', asset_type)

                    else: 
                        output.comment('Error Encountered While Determining Asset Type. Try -ex Flag For Example Usage.')

            # Correlation Matrix
            elif opt == settings.FUNC_ARG_DICT["correlation"]:
                if(len(args) > 1):
                    result = statistics.get_correlation_matrix_string(args, settings.INDENT)
                    output.comment(f'\n{result}')

                else:
                    output.comment('Invalid Input. Try -ex Flag For Example Usage.')
            
            elif opt == settings.FUNC_ARG_DICT["economic_indicator"]:
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

            elif opt == settings.FUNC_ARG_DICT["last_close"]:
                if(len(args)>1) or len(args)==1:
                    for arg in args:
                        price = services.get_daily_price_latest(arg)
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
                        output.sys_error()
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
    else:
        output.comment('No Arguments Supplied. Please Review Function Summary Below and Re-execute Script.')
        output.help()
