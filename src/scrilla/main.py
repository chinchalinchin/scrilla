import sys

#  Note: need to import from package when running from wheel.
# if running locally through main.py file, these imports should be replaced
#       from . import settings, from . import services, from . import files
# annoying, but it is what it is.
if __name__=="__main__":
    import settings, services, files

else:
    from scrilla import settings, services, files

from util import helper, outputter, formatter
from analysis import statistics, optimizer, markets
from objects.portfolio import Portfolio
from objects.cashflow import Cashflow

if settings.APP_ENV != "container":
    from PyQt5 import QtWidgets
    import gui.menu as menu
    import util.plotter as plotter

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
"""
non_container_functions = [formatter.FUNC_ARG_DICT['plot_dividends'], formatter.FUNC_ARG_DICT['plot_moving_averages'],
                               formatter.FUNC_ARG_DICT['plot_risk_profile'], formatter.FUNC_ARG_DICT['plot_frontier']]

def validate_function_usage(selection, args, wrapper_function, required_length=1, exact=False):
    if selection in non_container_functions and settings.APP_ENV == 'container':
        logger.comment('GUI functionality disabled when application is containerized.')

    else:
        if(not exact and (len(args)>(required_length-1))):
            wrapper_function()
        elif(exact and (len(args)==required_length)):
            wrapper_function()
        else:
            logger.comment(f'Invalid number of arguments for \'{selection}\' function.')

def do_program():
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
            files.clear_directory(directory=settings.CACHE_DIR, retain=True)

        ### FUNCTION: Clear Watchlist
        elif opt == formatter.FUNC_ARG_DICT["clear_watchlist"]:
            logger.comment(f'Clearing {settings.COMMON_DIR}')
            files.clear_directory(directory=settings.COMMON_DIR, retain=True)

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
        elif opt == formatter.FUNC_ARG_DICT['list_watchlist']:
            tickers = files.get_watchlist()
            outputter.title_line("Stock Watchlist")
            outputter.print_list(tickers)

        ### FUNCTION: Risk Free Rate
        elif opt == formatter.FUNC_ARG_DICT['risk_free_rate']:
            outputter.title_line("Risk Free Rate")
            outputter.scalar_result(calculation=formatter.RISK_FREE_TITLE.format(settings.RISK_FREE_RATE), 
                                    result=services.get_risk_free_rate(), 
                                    currency=False)

        ### FUNCTION: Store Key
            # NOTE: not technically a single argument function, but requires special parsing, so
            #       treat it here.
        elif opt == formatter.FUNC_ARG_DICT['store']:
            keyvalue = sys.argv[2].split("=")
            if keyvalue[0] in ["ALPHA_VANTAGE_KEY", "QUANDL_KEY", "IEX_KEY"]:
               keystore = {}
               keystore[keyvalue[0]] = keyvalue[1]
               args = { 'key_name': keyvalue[0], 'key_value': keyvalue[1]}
               files.store_local_object(local_object=files.OBJECTS['api_key'],value=keystore, args=args)
            else:
                outputter.comment(f'Key of {keyvalue[0]} not recognized. See -help for more information.')
            pass

        ### FUNCTION: Purge Data Directories
        elif opt == formatter.FUNC_ARG_DICT["purge"]:
            logger.comment(f'Clearing {settings.STATIC_DIR}, {settings.CACHE_DIR} and {settings.CACHE_DIR}')
            files.clear_directory(directory=settings.STATIC_DIR, retain=True)
            files.clear_directory(directory=settings.CACHE_DIR, retain=True)
            files.clear_directory(directory=settings.COMMON_DIR, retain=True)

        ### FUNCTION: Yield Curve
        elif opt == formatter.FUNC_ARG_DICT['yield_curve']:
                for rate in settings.ARG_Q_YIELD_CURVE:
                    curve_rate = services.get_daily_stats_latest(statistic=settings.ARG_Q_YIELD_CURVE[rate])
                    outputter.scalar_result(calculation=rate, result=curve_rate, currency=False)

        # variable argument functions
        else:
            logger.debug('Initialzing /static/ directory, if applicable.')
            files.init_static_data()
            
            args = sys.argv[2:]
            xtra_args, xtra_values, main_args = helper.separate_and_parse_args(args)
            xtra_list = helper.format_xtra_args_list(xtra_args, xtra_values)
            logger.log_arguments(main_args=main_args, xtra_args=xtra_args, xtra_values=xtra_values)
            exact = False

            outputter.title_line('Results')
            outputter.print_line()

            ### FUNCTION: Asset Grouping
            if opt == formatter.FUNC_ARG_DICT['asset_type']:
                def cli_asset_type():
                    for arg in main_args:
                        asset_type = markets.get_asset_type(arg)
                        if asset_type:
                            outputter.string_result(f'asset_type({arg})', asset_type)
                        else: 
                            logger.comment('Error encountered while determining asset Type. Try -ex flag for example usage.')
                selected_function, required_length = cli_asset_type, 1

            ### FUNCTION: Capital Asset Pricing Model Cost of Equity
            elif opt == formatter.FUNC_ARG_DICT['capm_equity_cost']:
                def cli_capm_equity_cost():
                    for arg in main_args:
                        equity_cost = markets.cost_of_equity(ticker=arg, start_date=xtra_list['start_date'], 
                                                                end_date=xtra_list['end_date'])
                        outputter.scalar_result(f'{arg}_equity_cost', equity_cost, currency=False)
                selected_function, required_length = cli_capm_equity_cost, 1


            ### FUNCTION: Capital Asset Pricing Model Beta
            elif opt == formatter.FUNC_ARG_DICT['capm_beta']:
                def cli_capm_beta():
                    for arg in main_args:
                        beta = markets.market_beta(ticker=arg, start_date=xtra_list['start_date'], 
                                                    end_date=xtra_list['end_date'])
                        outputter.scalar_result(f'{arg}_beta', beta, currency=False)
                selected_function, required_length = cli_capm_beta, 1

            ### FUNCTION: Last Close Price
            elif opt == formatter.FUNC_ARG_DICT["close"]:
                def cli_close():
                    for arg in main_args:
                        price = services.get_daily_price_latest(arg)
                        outputter.scalar_result(calculation=f'Last {arg} close price', result=float(price))
                selected_function, required_length = cli_close, 1
                    
            ### FUNCTION: Correlation Matrix
            elif opt == formatter.FUNC_ARG_DICT["correlation"]:
                def cli_correlation():
                    result = statistics.get_ito_correlation_matrix_string(tickers=main_args, indent=formatter.INDENT, 
                                                                        start_date=xtra_list['start_date'], 
                                                                        end_date=xtra_list['end_date'])
                    outputter.print_below_new_line(f'\n{result}')
                selected_function, required_length = cli_correlation, 2

            ### FUNCTION: Correlation Time Series
            elif opt == formatter.FUNC_ARG_DICT['correlation_time_series']:
                def cli_correlation_series():
                    ticker_1, ticker_2 = main_args[0], main_args[1]
                    result = statistics.calculate_ito_correlation_series(ticker_1=ticker_1,ticker_2=ticker_2,
                                                                            start_date=xtra_list['start_date'],
                                                                            end_date=xtra_list['end_date'])
                    for date in result:
                        outputter.scalar_result(calculation=f'{date}_{ticker_1}_{ticker_2}_correlation', 
                                                result=float(result[date]), currency=False)
                    
                selected_function, required_length, exact = cli_correlation_series, 2, True

            ### FUNCTION: Discount Dividend Model
            elif opt == formatter.FUNC_ARG_DICT["discount_dividend"]:
                def cli_discount_dividend():
                    model_results = {}
                    for arg in main_args:
                        dividends = services.get_dividend_history(arg)
                        if xtra_list['discount'] is None:
                            discount = markets.cost_of_equity(ticker=arg)
                        else:
                            discount = xtra_list['discount']
                        model_results[f'{arg}_discount_dividend'] = Cashflow(sample=dividends, 
                                                                                discount_rate=discount).calculate_net_present_value()
                        outputter.scalar_result(f'Net Present Value ({arg} dividends)', 
                                                    model_results[f'{arg}_discount_dividend'])
                    if xtra_list['save_file'] is not None:
                        files.save_file(file_to_save=model_results, file_name=xtra_list['save_file'])
                selected_function, required_length = cli_discount_dividend, 1

            elif opt == formatter.FUNC_ARG_DICT['dividends']:
                def cli_dividends():
                    for arg in main_args:
                        dividends = services.get_dividend_history(arg)
                        for date in dividends:
                            outputter.scalar_result(calculation=f'{arg}_dividend({date})', result=dividends[date])
                selected_function, required_length = cli_dividends, 1

            ### FUNCTION: Efficient Frontier
            elif opt == formatter.FUNC_ARG_DICT['efficient_frontier']:
                def cli_efficient_frontier():
                    portfolio = Portfolio(tickers=main_args, start_date=xtra_list['start_date'], 
                                            end_date=xtra_list['end_date'])
                    frontier = optimizer.calculate_efficient_frontier(portfolio=portfolio)
                    outputter.efficient_frontier(portfolio=portfolio, frontier=frontier,
                                                    investment=xtra_list['investment'])
                    if xtra_list['save_file'] is not None:
                        files.save_frontier(portfolio=portfolio, frontier=frontier,
                                            investment=xtra_list['investment'], 
                                            file_name=xtra_list['save_file'])
                selected_function, required_length = cli_efficient_frontier, 2

            ### FUNCTION: Maximize Portfolio Return
            elif opt == formatter.FUNC_ARG_DICT['maximize_return']:
                def cli_maximize_return():
                    portfolio = Portfolio(tickers=main_args, start_date=xtra_list['start_date'], 
                                            end_date=xtra_list['end_date'])
                    allocation = optimizer.maximize_portfolio_return(portfolio=portfolio)
                    outputter.optimal_result(portfolio=portfolio, allocation=allocation, 
                                                investment=xtra_list['investment'])
                selected_function, required_length = cli_maximize_return, 2

            ### FUNCTION: Moving Averages of Logarithmic Returns
            elif opt == formatter.FUNC_ARG_DICT['moving_averages']:
                def cli_moving_averages():
                    moving_averages = statistics.calculate_moving_averages(tickers=main_args, 
                                                                            start_date=xtra_list['start_date'], 
                                                                            end_date=xtra_list['end_date'])
                    periods = [settings.MA_1_PERIOD, settings.MA_2_PERIOD, settings.MA_3_PERIOD]
                    outputter.moving_average_result(tickers=main_args, averages_output=moving_averages, 
                                                    periods=periods, start_date=xtra_list['start_date'], 
                                                    end_date=xtra_list['end_date'])
                selected_function, required_length = cli_moving_averages, 1

            ### FUNCTION: Optimize Portfolio Variance/Volatility
            elif opt == formatter.FUNC_ARG_DICT['optimize_portfolio_variance']:
                def cli_optimize_portfolio_variance():
                    portfolio = Portfolio(tickers=main_args, start_date=xtra_list['start_date'], end_date=xtra_list['end_date'])
                    if xtra_list['optimize_sharpe']:
                        allocation = optimizer.maximize_sharpe_ratio(portfolio=portfolio, target_return=xtra_list['target'])
                    else:
                        allocation = optimizer.optimize_portfolio_variance(portfolio=portfolio, target_return=xtra_list['target'])   
                    outputter.optimal_result(portfolio=portfolio, allocation=allocation, investment=xtra_list['investment'])

                    if xtra_list['save_file'] is not None:
                        files.save_allocation(allocation=allocation, portfolio=portfolio, file_name=xtra_list['save_file'],
                                                investment=xtra_list['investment'])
                selected_function, required_length = cli_optimize_portfolio_variance, 2
            
            elif opt == formatter.FUNC_ARG_DICT['optimize_portfolio_conditional_var']:
                def cli_optimize_conditional_value_at_risk():
                    portfolio = Portfolio(tickers=main_args, start_date=xtra_list['start_date'], end_date=xtra_list['end_date'])
                    allocation = optimizer.optimize_conditional_value_at_risk(portfolio=portfolio,
                                                                                prob=xtra_list['probability'],
                                                                                expiry=xtra_list['expiry'],
                                                                                target_return=xtra_list['target'])
                    outputter.optimal_result(portfolio=portfolio, allocation=allocation, investment=xtra_list['investment'])

                    if xtra_list['save_file'] is not None:
                        files.save_allocation(allocation=allocation, portfolio=portfolio, file_name=xtra_list['save_file'],
                                                investment=xtra_list['investment'])
                selected_function, required_length = cli_optimize_conditional_value_at_risk, 2
            ### FUNCTION: Plot Dividend History With Linear Regression Model
            elif opt == formatter.FUNC_ARG_DICT['plot_dividends']:
                def cli_plot_dividends():
                    dividends = services.get_dividend_history(ticker=main_args[0])
                    if xtra_list['discount'] is None:
                        xtra_list['discount'] = markets.cost_of_equity(ticker=main_args[0])
                    div_cashflow = Cashflow(sample=dividends, discount_rate=xtra_list['discount'])
                    plotter.plot_cashflow(ticker=main_args[0], cashflow=div_cashflow, show=True, 
                                            savefile=xtra_list['save_file'])
                selected_function, required_length, exact = cli_plot_dividends, 1, True

            ### FUNCTION: Plot Efficient Frontier
            elif opt == formatter.FUNC_ARG_DICT['plot_frontier']:
                def cli_plot_frontier():
                    portfolio = Portfolio(tickers=main_args, start_date=xtra_list['start_date'], 
                                            end_date=xtra_list['end_date'])
                    frontier = optimizer.calculate_efficient_frontier(portfolio=portfolio)
                    plotter.plot_frontier(portfolio=Portfolio(main_args), frontier=frontier, show=True, 
                                            savefile=xtra_list['save_file'])
                selected_function, required_length = cli_plot_frontier, 2

            ### FUNCTION: Plot Moving Averages of Logarithmic Returns
            elif opt == formatter.FUNC_ARG_DICT['plot_moving_averages']:
                def cli_plot_moving_averages():
                    moving_averages = statistics.calculate_moving_averages(tickers=main_args, 
                                                                            start_date=xtra_list['start_date'], 
                                                                            end_date=xtra_list['end_date'])
                    periods = [settings.MA_1_PERIOD, settings.MA_2_PERIOD, settings.MA_3_PERIOD]
                    plotter.plot_moving_averages(symbols=main_args, averages_output=moving_averages, periods=periods, 
                                                    show=True, savefile=xtra_list['save_file'])
                selected_function, required_length = cli_plot_moving_averages, 1

            ### FUNCTION: Plot Risk-Return Profile
            elif opt == formatter.FUNC_ARG_DICT['plot_risk_profile']:
                def cli_plot_risk_profile():
                    profiles = {}
                    for arg in main_args:
                        profiles[arg]=statistics.calculate_risk_return(ticker=arg, start_date=xtra_list['start_date'], 
                                                                            end_date=xtra_list['end_date'])
                    plotter.plot_profiles(symbols=main_args, profiles=profiles, show=True, 
                                            savefile=xtra_list['save_file'], 
                                            subtitle=helper.format_date_range(start_date=xtra_list['start_date'], 
                                                                                end_date=xtra_list['end_date']))
                selected_function, required_length = cli_plot_risk_profile, 1

            ### FUNCTION: Price History
            elif opt == formatter.FUNC_ARG_DICT['price_history']:
                def cli_price_history():
                    all_prices = {}
                    for arg in main_args:
                        prices = services.get_daily_price_history(ticker=arg, start_date=xtra_list['start_date'],
                                                                    end_date=xtra_list['end_date'])
                        asset_type = markets.get_asset_type(symbol=arg)
                        all_prices[arg] = {}
                        for date in prices:
                            price = services.parse_price_from_date(prices=prices, date=date, asset_type=asset_type)
                            outputter.scalar_result(calculation=f'{arg}({date})', result = float(price))
                            all_prices[arg][date] = price
                    if xtra_list['save_file'] is not None:
                        files.save_file(file_to_save=all_prices, file_name=xtra_list['save_file'])

                selected_function, required_length = cli_price_history, 1

            ### FUNCTION: Risk-Return Profile
            elif opt == formatter.FUNC_ARG_DICT["risk_return"]:
                def cli_risk_return():
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
                selected_function, required_length = cli_risk_return, 1

            ### FUNCTION: Model Discount Screener 
            elif  opt == formatter.FUNC_ARG_DICT["screener"]:
                if xtra_list['model'] is None:
                    model = markets.MODEL_DDM
                results = markets.screen_for_discount(model=model, discount_rate=xtra_list['discount'])
                outputter.screen_results(info=results, model=model)

            ### FUNCTION: Sharpe Ratio
            elif opt == formatter.FUNC_ARG_DICT["sharpe_ratio"]:
                def cli_sharpe_ratio():
                    for arg in main_args:
                        result = markets.sharpe_ratio(ticker=arg, start_date=xtra_list['start_date'],
                                                        end_date=xtra_list['end_date'])
                        outputter.scalar_result(calculation=f'{arg}_sharpe_ratio', result=result, 
                                                    currency=False)
                selected_function, required_length = cli_sharpe_ratio, 1

            ### FUNCTION: Get Latest Economic Statistic
            elif opt == formatter.FUNC_ARG_DICT["statistic"]:
                # TODO: implement start and end date and print eac.
                def cli_statistic():
                    for stat in main_args:
                        outputter.scalar_result(calculation=stat, 
                                                result=services.get_daily_stats_latest(stat),
                                                currency=False)
                selected_function, required_length = cli_statistic, 1
            
            ### FUNCTION: Statistic History
            elif opt == formatter.FUNC_ARG_DICT['statistic_history']:
                def cli_statistic_history():
                    for arg in main_args:
                        stats = services.get_daily_stats_history(statistic=arg, start_date=xtra_list['start_date'],
                                                            end_date=xtra_list['end_date'])
                        for date in stats:
                            outputter.scalar_result(calculation=f'{arg}({date})', result=stats[date], 
                                                        currency=False) 
                selected_function, required_length = cli_statistic_history, 1

            ### FUNCTION: Set Watchlist
            elif opt == formatter.FUNC_ARG_DICT["watchlist"]:
                def cli_watchlist():
                    files.add_watchlist(new_tickers=main_args)
                    logger.comment("Watchlist saved. Use -ls option to print watchlist.")
                selected_function, required_length = cli_watchlist, 1
    
            else:
                logger.comment('No function supplied. Please review Function Summary below and re-execute with appropriate arguments.')
                outputter.help_msg()
            
            validate_function_usage(selection=opt, args=main_args, 
                                    wrapper_function=selected_function, 
                                    required_length=required_length, exact=exact)
            outputter.print_line()
    else:
        logger.comment('No arguments Supplied. Please review function summary below and re-execute with appropriate arguments.')
        outputter.help_msg()

if __name__ == "__main__": 
    # TODO: check for API key and if none exists, prompt user to define ALPHA_VANTAGE_KEY, QUANDL_KEY and
    #       IEX_KEY environment variables. Then exit. 
    # TODO: possibly create PyQt widget to prompt user to enter credentials and save them to creds.json
    #       in /data/common/
    do_program()