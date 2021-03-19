import sys

import app.settings as settings
import app.statistics as statistics
import app.optimizer as optimizer
import app.services as services
import app.markets as markets
import app.files as files

from app.objects.portfolio import Portfolio
from app.objects.cashflow import Cashflow

if settings.APP_ENV != "container":
    from PyQt5 import QtWidgets
    import gui.menu as menu
    import util.plotter as plotter

import util.helper as helper
import util.outputter as outputter
import util.formatter as formatter

logger = outputter.Logger('main', settings.LOG_LEVEL)

"""
main.py
-------
CLI Entrypoint 
--------------
Description
-----------
This script acts as the entrypoint for the CLI application. It parses the arguments supplied through the command line, delegates them to the appropriate application function and then passes the results to the Logger class for formatting and printing to screen. \n \n 

The arguments are parsed in such a way that arguments which are not supplied are set to None. All application functions are set up to accept None as a value for their optional arguments. This makes passing arguments to application functions easier as the `main.py` script doesn't have to worry about their values. In other words, `main.py` always passes all arguments to application functions, even if they aren't supplied through the command line; it just sets the ones which aren't supplied to None.  \n \n

Note, several of the application's function are not dealt with inside of this entrypoint script, namely the `-local` and `-container` flags, which start up a local Django development server or a containerized **gunicorn** server with the WSGI Application deployed onto it, respectively. For several reasons, the wrapper script '/scripts/pynance' takes cares of those arguments within the shell the `pynance` command is invoked from before passing the arguments to python. \n \n

First, before the containerized version of this application can be spun up, the Docker image must be built. This is easier to do from a shell script. Second, there are several 'manage.py' processes that must be completed before the server goes up, such as making migrations and migrating them to the database service. Doing so from inside of this script would be unnecessarily messy. Third, this application is designed to keep functionality as modularized as possible, i.e. the 'app' module is in charge purely of application calculations and algorithms, whereas the 'server' module is in charge of exposing the functions as an API and setting up all the necessary database tables, etc. Mixing and matching server tasks in this script would couple the application and server in ways that go counter to the design principles adopted for this package. \n \n
"""
if __name__ == "__main__": 

    if len(sys.argv)>0:
        logger.debug('Parsing and invoking command line arguments')
        opt = sys.argv[1]
        
        # single argument functions
        ### FUNCTION: Help Message
        if opt == formatter.FUNC_ARG_DICT["help"]:
            outputter.help_msg()

        ### FUNCTION: Clear Cache
        elif opt == formatter.FUNC_ARG_DICT["clear_cache"]:
            logger.comment(f'Clearing {settings.CACHE_DIR}')
            files.clear_directory(directory=settings.CACHE_DIR, retain=True, outdated_only=False)

        ### FUNCTION: Clear Watchlist
        elif opt == formatter.FUNC_ARG_DICT["clear_watchlist"]:
            logger.comment(f'Clearing {settings.COMMON_DIR}')
            files.clear_directory(directory=settings.COMMON_DIR, retain=True, outdated_only=False)

        ### FUNCTION: Function Examples
        elif opt == formatter.FUNC_ARG_DICT["examples"]:
            outputter.examples()
        
        ### FUNCTION: Graphical User Interface
        elif opt == formatter.FUNC_ARG_DICT["gui"] and settings.APP_ENV != "container":
            app = QtWidgets.QApplication([])

            widget = menu.MenuWidget()
            widget.resize(settings.GUI_WIDTH, settings.GUI_HEIGHT)
            widget.show()

            sys.exit(app.exec_())

        # NOTE: Docker doesn't support windowing libraries
        elif opt == formatter.FUNC_ARG_DICT["gui"] and settings.APP_ENV == "container":
            logger.comment("GUI functionality disabled when application is containerized.")

        ### FUNCTION: Static Data Initialization
        elif opt == formatter.FUNC_ARG_DICT['initialize']:
            logger.comment("Initializing /static/ directory")       
            files.init_static_data()

        ### FUNCTION: Print Stock Watchlist
        # TODO:
        elif opt == formatter.FUNC_ARG_DICT['list_watchlist']:
            tickers = files.get_watchlist()
            outputter.title_line("Stock Watchlist")
            outputter.print_list(tickers)

        ### FUNCTION: Risk Free Rate
        elif opt == formatter.FUNC_ARG_DICT['risk_free_rate']:
            outputter.title_line("Risk Free Rate")
            outputter.scalar_result(calculation=formatter.RISK_FREE_TITLE, 
                                    result=markets.get_risk_free_rate(), 
                                    currency=False)

        ### FUNCTION: Purge Data Directories
        elif opt == formatter.FUNC_ARG_DICT["purge"]:
            logger.comment(f'Clearing {settings.STATIC_DIR} and {settings.CACHE_DIR}')
            files.clear_directory(directory=settings.STATIC_DIR, retain=True, outdated_only=False)
            files.clear_directory(directory=settings.CACHE_DIR, retain=True, outdated_only=False)


        # variable argument functions
        else:
            logger.debug('Clearing /cache/ directory of outdated data.')
            files.clear_directory(directory=settings.CACHE_DIR, retain=True, outdated_only=True)

            logger.debug('Initialzing /static/ directory, if applicable.')
            files.init_static_data()
            
            args = sys.argv[2:]
            xtra_args, xtra_values, main_args = helper.separate_and_parse_args(args)
            xtra_list = helper.format_xtra_args_list(xtra_args, xtra_values)
            logger.log_arguments(main_args=main_args, xtra_args=xtra_args, xtra_values=xtra_values)

            outputter.title_line('Results')
            outputter.print_line()

            ### FUNCTION: Asset Grouping
            if opt == formatter.FUNC_ARG_DICT['asset_type']:
                for arg in main_args:
                    asset_type = markets.get_asset_type(arg)
                    if asset_type:
                        outputter.string_result(f'asset_type({arg})', asset_type)
                    else: 
                        logger.comment('Error encountered while determining asset Type. Try -ex flag for example usage.')

            ### FUNCTION: Capital Asset Pricing Model Cost of Equity
            elif opt == formatter.FUNC_ARG_DICT['capm_equity_cost']:
                if (len(main_args)>0):
                    for arg in main_args:
                        equity_cost = markets.cost_of_equity(ticker=arg, start_date=xtra_list['start_date'], 
                                                                end_date=xtra_list['end_date'])
                        outputter.scalar_result(f'{arg}_equity_cost', equity_cost, currency=False)
                else:
                    logger.comment('Error encountered while calculating. Try -ex flag for example usage.')

            ### FUNCTION: Capital Asset Pricing Model Beta
            elif opt == formatter.FUNC_ARG_DICT['capm_beta']:
                if (len(main_args)>0):
                    for arg in main_args:
                        beta = markets.market_beta(ticker=arg, start_date=xtra_list['start_date'], 
                                                    end_date=xtra_list['end_date'])
                        outputter.scalar_result(f'{arg}_beta', beta, currency=False)
                else:
                    logger.comment('Error encountered while calculating. Try -ex flag for example usage.')

            ### FUNCTION: Last Close Price
            elif opt == formatter.FUNC_ARG_DICT["close"]:
                if(len(main_args)>1) or len(main_args)==1:
                    for arg in main_args:
                        price = services.get_daily_price_latest(arg)
                        outputter.scalar_result(calculation=f'Last {arg} close price', result=float(price))
                else:
                    logger.comment('Error encountered while calculating. Try -ex flag for example usage.')
                    
            ### FUNCTION: Correlation Matrix
            elif opt == formatter.FUNC_ARG_DICT["correlation"]:
                if(len(main_args) > 1):
                    result = statistics.get_ito_correlation_matrix_string(tickers=main_args, indent=formatter.INDENT, 
                                                                        start_date=xtra_list['start_date'], 
                                                                        end_date=xtra_list['end_date'])
                    outputter.print_below_new_line(f'\n{result}')
                else:
                    logger.comment('Invalid input. Try -ex flag for example usage.')

            ### FUNCTION: Discount Dividend Model
            elif opt == formatter.FUNC_ARG_DICT["discount_dividend"]:
                # TODO: compute cost of capital equity and use as discount rate

                if(len(main_args)>1) or len(main_args)==1:
                    for arg in main_args:
                        dividends = services.get_dividend_history(arg)
                        if xtra_list['discount'] is None:
                            xtra_list['discount'] = markets.cost_of_equity(ticker=arg)
                        div_npv = Cashflow(sample=dividends, discount_rate=xtra_list['discount']).calculate_net_present_value()
                        outputter.scalar_result(f'Net Present Value ({arg} dividends)', div_npv)
                else:
                    logger.comment('Invalid input. Try -ex flag for example usage.')

            ### FUNCTION: Efficient Frontier
            elif opt == formatter.FUNC_ARG_DICT['efficient_frontier']:
                if(len(main_args)>1):
                    portfolio = Portfolio(tickers=main_args, start_date=xtra_list['start_date'], 
                                            end_date=xtra_list['end_date'])
                    frontier = optimizer.calculate_efficient_frontier(portfolio=portfolio)
                    outputter.efficient_frontier(portfolio=portfolio, frontier=frontier,
                                                    investment=xtra_list['investment'])
                    if xtra_list['save_file'] is not None:
                        files.save_frontier(portfolio=portfolio, frontier=frontier,
                                            investment=xtra_list['investment'], 
                                            file_name=xtra_list['save_file'])
                else: 
                    logger.comment('Invalid input. Try -ex flag for example usage.')
                    
            ### FUNCTION: Maximize Portfolio Return
            elif opt == formatter.FUNC_ARG_DICT['maximize_return']:
                if (len(main_args)>1):
                    portfolio = Portfolio(tickers=main_args, start_date=xtra_list['start_date'], 
                                            end_date=xtra_list['end_date'])
                    allocation = optimizer.maximize_portfolio_return(portfolio=portfolio)
                    outputter.optimal_result(portfolio=portfolio, allocation=allocation, 
                                                investment=xtra_list['investment'])
                else:
                    logger.comment('Invalid input. Try -ex flag for example usage.')

            ### FUNCTION: Moving Averages of Logarithmic Returns
            elif opt == formatter.FUNC_ARG_DICT['moving_averages']:
                if(len(main_args)>0):
                    moving_averages = statistics.calculate_moving_averages(tickers=main_args, 
                                                                            start_date=xtra_list['start_date'], 
                                                                            end_date=xtra_list['end_date'])
                    periods = [settings.MA_1_PERIOD, settings.MA_2_PERIOD, settings.MA_3_PERIOD]
                    outputter.moving_average_result(tickers=main_args, averages_output=moving_averages, 
                                                    periods=periods, start_date=xtra_list['start_date'], 
                                                    end_date=xtra_list['end_date'])
                else: 
                    logger.comment('Invalid input. Try -ex flag for example usage.')

            ### FUNCTION: Optimize Portfolio Variance/Volatility
            elif opt == formatter.FUNC_ARG_DICT['optimize_portfolio']:
                if (len(main_args)>1):
                    portfolio = Portfolio(tickers=main_args, start_date=xtra_list['start_date'], end_date=xtra_list['end_date'])
                    if xtra_list['optimize_sharpe']:
                        allocation = optimizer.maximize_sharpe_ratio(portfolio=portfolio, target_return=xtra_list['target'])
                    else:
                        allocation = optimizer.optimize_portfolio_variance(portfolio=portfolio, target_return=xtra_list['target'])   
                    outputter.optimal_result(portfolio=portfolio, allocation=allocation, investment=xtra_list['investment'])

                    if xtra_list['save_file'] is not None:
                        files.save_allocation(allocation=allocation, portfolio=portfolio, file_name=xtra_list['save_file'],
                                                investment=xtra_list['investment'])
                else: 
                    logger.comment('Invalid input. Try -ex flag for example usage.')
            
            ### FUNCTION: Plot Dividend History With Linear Regression Model
            elif opt == formatter.FUNC_ARG_DICT['plot_dividends'] and settings.APP_ENV != "container":
                if len(main_args)==1:
                    dividends = services.get_dividend_history(ticker=main_args[0])
                    if xtra_list['discount'] is None:
                        xtra_list['discount'] = markets.cost_of_equity(ticker=main_args[0])
                    div_cashflow = Cashflow(sample=dividends, discount_rate=xtra_list['discount'])
                    plotter.plot_cashflow(ticker=main_args[0], cashflow=div_cashflow, show=True, 
                                            savefile=xtra_list['save_file'])
                elif len(main_args) > 1:
                    logger.comment('Only one equity\'s dividend history can be plotted at a time.')
                else: 
                    logger.comment('Invalid input. Try -ex flag for example usage.')
            elif opt == formatter.FUNC_ARG_DICT['plot_dividends'] and settings.APP_ENV == "container":
                logger.comment('Plotting functionality disabled when application is containerized.')

            ### FUNCTION: Plot Efficient Frontier
            elif opt == formatter.FUNC_ARG_DICT['plot_frontier'] and settings.APP_ENV != "container":
                if(len(main_args)>1):
                    portfolio = Portfolio(tickers=main_args, start_date=xtra_list['start_date'], 
                                            end_date=xtra_list['end_date'])
                    frontier = optimizer.calculate_efficient_frontier(portfolio=portfolio)
                    plotter.plot_frontier(portfolio=Portfolio(main_args), frontier=frontier, show=True, 
                                            savefile=xtra_list['save_file'])
                else: 
                    logger.comment('Invalid input. Try -ex flag for example usage.')
            elif opt == formatter.FUNC_ARG_DICT['plot_frontier'] and settings.APP_ENV == "container":
                logger.comment('Plotting functionality disabled when application is containerized.')

            ### FUNCTION: Plot Moving Averages of Logarithmic Returns
            elif opt == formatter.FUNC_ARG_DICT['plot_moving_averages'] and settings.APP_ENV != "container":
                if(len(main_args)>0):
                    moving_averages = statistics.calculate_moving_averages(tickers=main_args, 
                                                                            start_date=xtra_list['start_date'], 
                                                                            end_date=xtra_list['end_date'])
                    periods = [settings.MA_1_PERIOD, settings.MA_2_PERIOD, settings.MA_3_PERIOD]
                    plotter.plot_moving_averages(symbols=main_args, averages_output=moving_averages, periods=periods, 
                                                    show=True, savefile=xtra_list['save_file'])
                else:
                    logger.comment('Invalid Input. Try Try -ex Flag For Example Usage.')
            elif opt == formatter.FUNC_ARG_DICT['plot_moving_averages'] and settings.APP_ENV == "container":
                logger.comment('Plotting functionality disabled when application is containerized.')

            ### FUNCTION: Plot Risk-Return Profile
            elif opt == formatter.FUNC_ARG_DICT['plot_risk_profile'] and settings.APP_ENV != "container":
                if len(main_args) > 0:
                    profiles = []
                    for arg in main_args:
                        profiles.append(statistics.calculate_risk_return(ticker=arg, start_date=xtra_list['start_date'], 
                                                                            end_date=xtra_list['end_date']))
                    plotter.plot_profiles(symbols=main_args, profiles=profiles, show=True, 
                                            savefile=xtra_list['save_file'], 
                                            subtitle=helper.format_date_range(start_date=xtra_list['start_date'], 
                                                                                end_date=xtra_list['end_date']))
                else:
                    logger.comment('Invalid input. Try -ex flag for example usage.')
            elif opt == formatter.FUNC_ARG_DICT['plot_risk_profile'] and settings.APP_ENV == "container":
                logger.comment('Plotting functionality disabled when application is containerized.')

            ### FUNCTION: Risk-Return Profile
            elif opt == formatter.FUNC_ARG_DICT["risk_return"]:
                if(len(main_args)>0):
                    profiles = {}
                    failed = False
                    for arg in main_args:
                        result = statistics.calculate_risk_return(ticker=arg, start_date=xtra_list['start_date'], 
                                                                    end_date=xtra_list['end_date'])
                        if result:
                            outputter.scalar_result(calculation=f'mean_{arg}', result=result['annual_return'],
                                                    currency=False)
                            outputter.scalar_result(calculation=f'vol_{arg}', result=result['annual_volatility'],
                                                    currency=False)
                            profiles[arg] = result
                        
                        else:
                            failed = True
                            logger.comment('Error Encountered While Calculating. Try -ex Flag For Example Usage.')
                        
                        if not failed and xtra_list['save_file'] is not None:
                            files.save_file(file_to_save=profiles, file_name=xtra_list['save_file'])
                else:
                    logger.comment('Invalid input. Try -ex flag for example usage.')

            ### FUNCTION: Model Discount Screener 
            elif  opt == formatter.FUNC_ARG_DICT["screener"]:
                if xtra_list['model'] is None:
                    model = markets.MODEL_DDM
                results = markets.screen_for_discount(model=model, discount_rate=xtra_list['discount'])
                outputter.screen_results(info=results, model=model)

            ### FUNCTION: Sharpe Ratio
            elif opt == formatter.FUNC_ARG_DICT["sharpe_ratio"]:
                if (len(main_args) > 0):
                    for arg in main_args:
                        result = markets.sharpe_ratio(ticker=arg, start_date=xtra_list['start_date'],
                                                        end_date=xtra_list['end_date'])
                        outputter.scalar_result(calculation=f'{arg}_sharpe_ratio', result=result, 
                                                    currency=False)
                else:
                    logger.comment('Error encountered while calculating. Try -ex flag for example usage.')

            ### FUNCTION: Get Latest Economic Statistic
            elif opt == formatter.FUNC_ARG_DICT["statistic"]:
                if(len(main_args)>0):
                    for stat in main_args:
                        outputter.scalar_result(calculation=stat, 
                                                result=services.get_daily_stats_latest(stat),
                                                currency=False)
                else:
                    logger.comment('Error encountered while calculating. Try -ex flag for example usage.')
            
            ### FUNCTION: Set Watchlist
            elif opt == formatter.FUNC_ARG_DICT["watchlist"]:
                if(len(main_args)>0):
                    files.add_watchlist(new_tickers=main_args)
                    logger.comment("Watchlist saved. Use -ls option to print watchlist.")
                else:
                    logger.comment('Error encountered while calculating. Try -ex flag for example usage.')
            else:
                logger.comment('No function supplied. Please review Function Summary below and re-execute with appropriate arguments.')
                outputter.help_msg()
            
            outputter.print_line()
    else:
        logger.comment('No arguments Supplied. Please review function summary below and re-execute with appropriate arguments.')
        outputter.help_msg()