import os, sys
import datetime
import scipy.optimize as optimize


import app.settings as settings
import app.statistics as statistics
import app.optimizer as optimizer
import app.services as services
import app.markets as markets

from app.objects.portfolio import Portfolio
from app.objects.cashflow import Cashflow

if settings.APP_ENV != "container":
    from PyQt5 import QtWidgets
    import gui.menu as menu
    import util.plotter as plotter

import util.helper as helper
import util.logger as logger
import util.formatter as formatter

output = logger.Logger('main', settings.LOG_LEVEL)


if __name__ == "__main__": 

    if len(sys.argv)>0:
        output.debug('Parsing and invoking command line arguments')
        opt = sys.argv[1]
        
        # single argument functions
        ### FUNCTION: Help Message
        if opt == formatter.FUNC_ARG_DICT["help"]:
            output.help()

        ### FUNCTION: Clear Cache
        elif opt == formatter.FUNC_ARG_DICT["clear_cache"]:
            output.comment(f'Clearing {settings.CACHE_DIR}')
            helper.clear_directory(directory=settings.CACHE_DIR, retain=True, outdated_only=False)

        ### FUNCTION: Clear Watchlist
        elif opt == formatter.FUNC_ARG_DICT["clear_watchlist"]:
            output.comment(f'Clearing {settings.COMMON_DIR}')
            helper.clear_directory(directory=settings.COMMON_DIR, retain=True, outdated_only=False)

        ### FUNCTION: Function Examples
        elif opt == formatter.FUNC_ARG_DICT["examples"]:
            output.examples()
        
        ### FUNCTION: Graphical User Interface
        elif opt == formatter.FUNC_ARG_DICT["gui"] and settings.APP_ENV != "container":
            app = QtWidgets.QApplication([])

            widget = menu.MenuWidget()
            widget.resize(settings.GUI_WIDTH, settings.GUI_HEIGHT)
            widget.show()

            sys.exit(app.exec_())

        # NOTE: Docker doesn't support windowing libraries
        elif opt == formatter.FUNC_ARG_DICT["gui"] and settings.APP_ENV == "container":
            output.comment("GUI functionality disabled when application is containerized.")

        ### FUNCTION: Static Data Initialization
        elif opt == formatter.FUNC_ARG_DICT['initialize']:
            output.comment("Initializing /static/ directory")       
            services.init_static_data()

        ### FUNCTION: Print Stock Watchlist
        # TODO:
        elif opt == formatter.FUNC_ARG_DICT['list']:
            tickers = services.get_watchlist()
            output.title_line("Stock Watchlist")
            # output.print_list(tickers)

        ### FUNCTION: Risk Free Rate
        elif opt == formatter.FUNC_ARG_DICT['risk_free_rate']:
            output.scalar_result(formatter.RISK_FREE_TITLE, services.get_risk_free_rate())

        ### FUNCTION: Purge Data Directories
        elif opt == formatter.FUNC_ARG_DICT["purge"]:
            output.comment(f'Clearing {settings.STATIC_DIR} and {settings.CACHE_DIR}')
            helper.clear_directory(directory=settings.STATIC_DIR, retain=True, outdated_only=False)
            helper.clear_directory(directory=settings.CACHE_DIR, retain=True, outdated_only=False)


        # variable argument functions
        else:
            output.debug('Clearing /cache/ directory of outdated data.')
            helper.clear_directory(directory=settings.CACHE_DIR, retain=True, outdated_only=True)

            output.debug('Initialzing /static/ directory, if applicable.')
            services.init_static_data()
            
            args = sys.argv[2:]

            # Additional Argument Parsing
            xtra_args, xtra_values, main_args = helper.separate_and_parse_args(args)
            output.debug(f'Main Arguments: {main_args}')
            for xtra in xtra_args:
                i = xtra_args.index(xtra)
                output.debug(f'Extra Argument: {xtra} = {xtra_values[i]}')
            
            # Parse additional arguments or set to None
            start_date = helper.get_start_date(xtra_args, xtra_values)
            end_date = helper.get_end_date(xtra_args, xtra_values)
            save_file = helper.get_save_file(xtra_args, xtra_values)
            target = helper.get_target(xtra_args, xtra_values)
            discount = helper.get_discount(xtra_args, xtra_values)
            model = helper.get_model(xtra_args, xtra_values)

            output.title_line('Results')
            output.line()

            ### FUNCTION: Asset Grouping
            if opt == formatter.FUNC_ARG_DICT['asset_type']:
                for arg in main_args:
                    asset_type = markets.get_asset_type(arg)
                    if asset_type:
                        output.string_result(f'asset_type({arg})', asset_type)

                    else: 
                        output.comment('Error encountered while determining asset Type. Try -ex flag for example usage.')

            ### FUNCTION: Last Close Price
            elif opt == formatter.FUNC_ARG_DICT["close"]:
                if(len(main_args)>1) or len(main_args)==1:
                    for arg in main_args:
                        price = services.get_daily_price_latest(arg)
                        output.scalar_result(arg, float(price))
                    
                else:
                    output.comment('Error encountered while calculating. Try -ex flag for example usage.')
                    
            ### FUNCTION: Correlation Matrix
            elif opt == formatter.FUNC_ARG_DICT["correlation"]:
                if(len(main_args) > 1):
                    result = statistics.get_ito_correlation_matrix_string(tickers=main_args, indent=formatter.INDENT, 
                                                                        start_date=start_date, end_date=end_date)
                    output.comment(f'\n{result}')

                else:
                    output.comment('Invalid input. Try -ex flag for example usage.')

            ### FUNCTION: Discount Dividend Model
            elif opt == formatter.FUNC_ARG_DICT["discount_dividend"]:
                if(len(main_args)>1) or len(main_args)==1:
                    for arg in main_args:
                        dividends = services.get_dividend_history(arg)
                        div_npv = Cashflow(dividends).calculate_net_present_value(discount_rate=discount)
                        output.scalar_result(f'Net Present Value ({arg} dividends)', div_npv)
                else:
                    output.comment('Invalid input. Try -ex flag for example usage.')

            ### FUNCTION: Efficient Frontier
            elif opt == formatter.FUNC_ARG_DICT['efficient_frontier']:
                if(len(main_args)>1):
                    portfolio = Portfolio(tickers=main_args, start_date=start_date, end_date=end_date)
                    frontier = optimizer.calculate_efficient_frontier(portfolio=portfolio)
                    output.efficient_frontier(portfolio=portfolio, frontier=frontier,
                                                user_input=settings.INVESTMENT_MODE)
                
                else: 
                    output.comment('Invalid input. Try -ex flag for example usage.')
                    
            ### FUNCTION: Maximize Portfolio Return
            elif opt == formatter.FUNC_ARG_DICT['maximize_return']:
                if (len(main_args)>1):
                    portfolio = Portfolio(tickers=main_args, start_date=start_date, end_date=end_date)
                    allocation = optimizer.maximize_portfolio_return(portfolio=portfolio)
                    output.optimal_result(portfolio=portfolio, allocation=allocation, 
                                            user_input=settings.INVESTMENT_MODE)

                else:
                    output.comment('Invalid input. Try -ex flag for example usage.')

            ### FUNCTION: Moving Averages of Logarithmic Returns
            elif opt == formatter.FUNC_ARG_DICT['moving_averages']:
                if(len(main_args)>1) or len(main_args)==1:
                    moving_averages = statistics.calculate_moving_averages(main_args, start_date, end_date)
                    periods = [settings.MA_1_PERIOD, settings.MA_2_PERIOD, settings.MA_3_PERIOD]
                    output.moving_average_result(main_args, moving_averages, periods, start_date, end_date)

                else: 
                    output.comment('Invalid input. Try -ex flag for example usage.')

            ### FUNCTION: Optimize Portfolio Variance/Volatility
            elif opt == formatter.FUNC_ARG_DICT['optimize_portfolio']:
                if (len(main_args)>1):
                    portfolio = Portfolio(tickers=main_args, start_date=start_date, end_date=end_date)
                    allocation = optimizer.optimize_portfolio_variance(portfolio=portfolio, target_return=target)   
                    output.optimal_result(portfolio=portfolio, allocation=allocation,
                                            user_input=settings.INVESTMENT_MODE)
                
                else: 
                    output.comment('Invalid input. Try -ex flag for example usage.')
            
            ### FUNCTION: Plot Dividen History
            elif opt == formatter.FUNC_ARG_DICT['plot_dividends'] and settings.ENVIRONMENT != "container":
                if(len(main_args)>1) or len(main_args)==1:
                    output.comment('Dividend plotting goes here.')
                else: 
                    output.comment('Invalid input. Try -ex flag for example usage.')

            ### FUNCTION: Plot Efficient Frontier
            elif opt == formatter.FUNC_ARG_DICT['plot_frontier'] and settings.ENVIRONMENT != "container":
                if(len(main_args)>1):
                    frontier = optimizer.calculate_efficient_frontier(equities=main_args)
                    plotter.plot_frontier(portfolio=Portfolio(main_args), frontier=frontier, show=True, savefile=save_file)
                
                else: 
                    output.comment('Invalid input. Try -ex flag for example usage.')

            ### FUNCTION: Plot Moving Averages of Logarithmic Returns
            elif opt == formatter.FUNC_ARG_DICT['plot_moving_averages'] and settings.APP_ENV != "container":
                if(len(main_args)>1) or len(main_args)==1:
                    moving_averages = statistics.calculate_moving_averages(main_args, start_date, end_date)
                    periods = [settings.MA_1_PERIOD, settings.MA_2_PERIOD, settings.MA_3_PERIOD]
                    plotter.plot_moving_averages(symbols=main_args, averages_output=moving_averages, periods=periods, 
                                                    show=True, savefile=save_file)

                else:
                    output.debug('Invalid Input. Try Try -ex Flag For Example Usage.')

            ### FUNCTION: Plot Risk-Return Profile
            elif opt == formatter.FUNC_ARG_DICT['plot_risk_profile']:
                if len(main_args) > 0:
                    profiles = []
                    for arg in main_args:
                        profiles.append(statistics.calculate_risk_return(arg, start_date, end_date))
                    
                    plotter.plot_profiles(symbols=main_args, profiles=profiles, show=True, savefile=save_file, 
                                            subtitle=helper.format_date_range(start_date, end_date))
                
                else:
                    output.comment('Invalid input. Try -ex flag for example usage.')
                    
            ### FUNCTION: Risk-Return Profile
            elif opt == formatter.FUNC_ARG_DICT["risk_return"]:
                if(len(main_args)>1) or len(main_args)==1:
                    for arg in main_args:
                        result = statistics.calculate_risk_return(arg, start_date, end_date)
                        if result:
                            output.scalar_result(f'mean_{arg}', result['annual_return'])
                            output.scalar_result(f'vol_{arg}', result['annual_volatility'])

                        else:
                            output.comment('Error Encountered While Calculating. Try -ex Flag For Example Usage.')
                
                else:
                    output.comment('Invalid input. Try -ex flag for example usage.')

            ### FUNCTION: Model Discount Screener 
            elif  opt == formatter.FUNC_ARG_DICT["screener"]:
                if model is None:
                    model = markets.MODEL_DDM
                    
                results = markets.screen_for_discount(model=model)
                output.screen_results(info=results, model=model)

            ### FUNCTION: Get Latest Economic Statistic
            elif opt == formatter.FUNC_ARG_DICT["statistic"]:
                if(len(main_args)>1) or len(main_args)==1:
                    for stat in main_args:
                        output.scalar_result(stat, services.get_daily_stats_latest(stat))

                else:
                    output.comment('Error encountered while calculating. Try -ex flag for example usage.')
            
            ### FUNCTION: Set Watchlist
            elif opt == formatter.FUNC_ARG_DICT["watchlist"]:
                if(len(main_args)>1) or len(main_args)==1:
                    services.add_watchlist(new_tickers=main_args)
                    output.comment("Watchlist saved. Use -ls option to print watchlist.")
                else:
                    output.comment('Error encountered while calculating. Try -ex flag for example usage.')

            else:
                output.comment('No function supplied. Please review Function Summary below and re-execute with appropriate arguments.')
                output.help()
            
            output.line()
    else:
        output.comment('No arguments Supplied. Please review function summary below and re-execute with appropriate arguments.')
        output.help()