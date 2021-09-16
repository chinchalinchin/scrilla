import sys, os, traceback, json

#  Note: need to import from package when running from wheel.
# if running locally through main.py file, these imports should be replaced
#       from . import settings, from . import services, from . import files
# annoying, but it is what it is.
if __name__=="__main__":
    import settings, services, files, static
    from errors import APIResponseError, ConfigurationError, InputValidationError, SampleSizeError, PriceError

else:
    from scrilla import settings, services, files, static
    from scrilla.errors import APIResponseError, ConfigurationError, InputValidationError, SampleSizeError, PriceError


from util import helper, outputter, formatter
from analysis import statistics, optimizer, markets, blackscholes
from objects.portfolio import Portfolio
from objects.cashflow import Cashflow

if settings.APP_ENV != "container":
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
        logger.comment('Graphics functionality disabled when application is containerized.')

    else:
        try:
            if(not exact and (len(args)>(required_length-1))):
                wrapper_function()
            elif(exact and (len(args)==required_length)):
                wrapper_function()
            else:
                logger.comment(f'Invalid number of arguments for \'{selection}\' function.')

        except (PriceError, SampleSizeError, APIResponseError, \
                    InputValidationError, ConfigurationError) as e:
            print(str(e))
            traceback.print_exc()

def print_format_to_screen(xtra_dict):
    return xtra_dict['json'] is None and xtra_dict['suppress'] is None

def print_json_to_screen(xtra_dict):
    return xtra_dict['json'] is not None and xtra_dict['suppress'] is None

def do_program():
    if len(sys.argv)>0:
        logger.debug('Parsing and invoking command line arguments')
        opt = sys.argv[1]
        logger.debug(f'Selected Function: {opt}')
        
        # single argument functions
        ### FUNCTION: Help Message
        if opt == formatter.FUNC_ARG_DICT["help"]:
            outputter.help_msg()

        ### FUNCTION: Clear Cache
        elif opt == formatter.FUNC_ARG_DICT["clear_cache"]:
            logger.comment(f'Clearing {settings.CACHE_DIR}')
            files.clear_directory(directory=settings.CACHE_DIR, retain=True)

        ### FUNCTION: Clear Static
        elif opt == formatter.FUNC_ARG_DICT["clear_static"]:
            logger.comment(f'Clearing {settings.STATIC_DIR}')
            files.clear_directory(directory=settings.STATIC_DIR, retain=True)

        ### FUNCTION: Clear Watchlist
        elif opt == formatter.FUNC_ARG_DICT["clear_watchlist"]:
            logger.comment(f'Clearing {settings.COMMON_DIR}')
            files.clear_directory(directory=settings.COMMON_DIR, retain=True)

        ### FUNCTION: Function Examples
        elif opt == formatter.FUNC_ARG_DICT["examples"]:
            outputter.examples()
        
        ### FUNCTION: Print Stock Watchlist
        elif opt == formatter.FUNC_ARG_DICT['list_watchlist']:
            tickers = files.get_watchlist()
            outputter.title_line("Stock Watchlist")
            outputter.print_list(tickers)

        ### FUNCTION: Store Key
            # NOTE: not technically a single argument function, but requires special parsing, so
            #       treat it here.
        elif opt == formatter.FUNC_ARG_DICT['store']:
            key = sys.argv[2].split("=")
            if key[0] in ["ALPHA_VANTAGE_KEY", "QUANDL_KEY", "IEX_KEY"]:
               files.set_credentials(value=key[1], whichkey=key[0])
            else:
                outputter.comment(f'Key of {key[0]} not recognized. See -help for more information.')

        ### FUNCTION: Purge Data Directories
        elif opt == formatter.FUNC_ARG_DICT["purge"]:
            logger.comment(f'Clearing {settings.STATIC_DIR}, {settings.CACHE_DIR} and {settings.CACHE_DIR}')
            files.clear_directory(directory=settings.STATIC_DIR, retain=True)
            files.clear_directory(directory=settings.CACHE_DIR, retain=True)
            files.clear_directory(directory=settings.COMMON_DIR, retain=True)
        
        ### FUNCTION: Display Version
        elif opt == formatter.FUNC_ARG_DICT["version"]:
            version_file = os.path.join(settings.APP_DIR, 'version.txt')
            with open(version_file, 'r') as f:
                print(f.read())

        # variable argument functions
        else:
            logger.debug('Initialzing /static/ directory, if applicable.')
            files.init_static_data()
            
            args = sys.argv[2:]
            xtra_args, xtra_values, main_args = helper.separate_and_parse_args(args)
            xtra_dict = helper.format_xtra_args_dict(xtra_args, xtra_values)
            logger.log_arguments(main_args=main_args, xtra_args=xtra_args, xtra_values=xtra_values)
            exact, selected_function = False, None

            if print_format_to_screen(xtra_dict):
                outputter.title_line('Results')
                outputter.print_line()

            ### FUNCTION: Asset Grouping
            if opt == formatter.FUNC_ARG_DICT['asset_type']:
                def cli_asset_type():
                    for arg in main_args:
                        asset_type = files.get_asset_type(arg)
                        if asset_type:
                            outputter.string_result(f'asset_type({arg})', asset_type)
                        else: 
                            logger.comment('Error encountered while determining asset Type. Try -ex flag for example usage.')
                selected_function, required_length = cli_asset_type, 1

            ### FUNCTION: Black-Scholes Value At Risk
            elif opt == formatter.FUNC_ARG_DICT['bs_var']:
                def cli_bs_var():
                    all_vars = {}
                    for arg in main_args:
                        prices = services.get_daily_price_history(ticker=arg, start_date=xtra_dict['start_date'],
                                                                    end_date=xtra_dict['end_date'])
                        latest_price = prices[helper.get_first_json_key(prices)]
                        profile = statistics.calculate_risk_return(ticker=arg, sample_prices=prices)
                        valueatrisk = blackscholes.percentile(S0=latest_price, vol=profile['annual_volatility'],
                                                                ret=profile['annual_return'], expiry=xtra_dict['expiry'],
                                                                percentile=xtra_dict['probability'])
                        all_vars[arg]=valueatrisk

                        if print_format_to_screen(xtra_dict):
                            outputter.scalar_result(f'{arg}_value_at_risk', valueatrisk)

                    if print_json_to_screen(xtra_dict):
                        print(json.dump(all_vars))
                    
                    if xtra_dict['save_file'] is not None:
                        files.save_file(file_to_save=all_vars, file_name=xtra_dict['save_file'])

                selected_function, required_length = cli_bs_var, 2
                
            ### FUNCTION: Black-Scholes Conditional Value At Risk
            elif opt == formatter.FUNC_ARG_DICT['bs_cvar']:
                def cli_bs_var():
                    all_cvars = {}
                    for arg in main_args:
                        prices = services.get_daily_price_history(ticker=arg, start_date=xtra_dict['start_date'],
                                                                    end_date=xtra_dict['end_date'])
                        latest_price = prices[helper.get_first_json_key(prices)]
                        profile = statistics.calculate_risk_return(ticker=arg, sample_prices=prices)
                        valueatrisk = blackscholes.percentile(S0=latest_price, vol=profile['annual_volatility'],
                                                                ret=profile['annual_return'], expiry=xtra_dict['expiry'],
                                                                percentile=xtra_dict['probability'])
                        cvar = blackscholes.conditional_expected_value(S0=latest_price, vol=profile['annual_volatility'],
                                                                        ret=profile['annual_return'], expiry=xtra_dict['expiry'],
                                                                        conditional_value=valueatrisk)
                        all_cvars[arg]=cvar

                        if print_format_to_screen(xtra_dict):
                            outputter.scalar_result(f'{arg}_value_at_risk', valueatrisk)

                    if print_json_to_screen(xtra_dict):
                        print(json.dumps(all_cvars))
                    
                    if xtra_dict['save_file'] is not None:
                        files.save_file(file_to_save=all_cvars, file_name=xtra_dict['save_file'])

                selected_function, required_length = cli_bs_var, 2

            ### FUNCTION: Capital Asset Pricing Model Cost of Equity
            elif opt == formatter.FUNC_ARG_DICT['capm_equity_cost']:
                def cli_capm_equity_cost():
                    all_costs = {}
                    for arg in main_args:
                        equity_cost = markets.cost_of_equity(ticker=arg, start_date=xtra_dict['start_date'], 
                                                                end_date=xtra_dict['end_date'])
                        all_costs[arg] = equity_cost

                        if print_format_to_screen(xtra_dict):
                            outputter.scalar_result(f'{arg}_equity_cost', equity_cost, currency=False)

                    if print_json_to_screen(xtra_dict):
                        print(json.dumps(all_costs))

                    if xtra_dict['save_file'] is not None:
                        files.save_file(file_to_save=all_costs, file_name=xtra_dict['save_file'])


                selected_function, required_length = cli_capm_equity_cost, 1


            ### FUNCTION: Capital Asset Pricing Model Beta
            elif opt == formatter.FUNC_ARG_DICT['capm_beta']:
                def cli_capm_beta():
                    all_betas = {}
                    for arg in main_args:
                        beta = markets.market_beta(ticker=arg, start_date=xtra_dict['start_date'], 
                                                    end_date=xtra_dict['end_date'])
                        all_betas[arg] = beta

                        if print_format_to_screen(xtra_dict):
                            outputter.scalar_result(f'{arg}_beta', beta, currency=False)

                    if print_json_to_screen(xtra_dict):
                        print(json.loads(all_betas))

                    if xtra_dict['save_file'] is not None:
                        files.save_file(file_to_save=all_betas, file_name=xtra_dict['save_file'])

                selected_function, required_length = cli_capm_beta, 1

            ### FUNCTION: Last Close Price
            elif opt == formatter.FUNC_ARG_DICT["close"]:
                def cli_close():
                    all_prices = {}
                    for arg in main_args:
                        price = services.get_daily_price_latest(arg)
                        all_prices[arg] = price

                        if print_format_to_screen(xtra_dict):
                            outputter.scalar_result(calculation=f'Last {arg} close price', result=float(price))

                    if print_json_to_screen(xtra_dict):
                        print(json.dumps(all_prices))

                    if xtra_dict['save_file'] is not None:
                        files.save_file(file_to_save=all_prices, file_name=xtra_dict['save_file'])
                selected_function, required_length = cli_close, 1
                    
            ### FUNCTION: Correlation Matrix
            elif opt == formatter.FUNC_ARG_DICT["correlation"]:
                def cli_correlation():
                    result = statistics.get_ito_correlation_matrix_string(tickers=main_args, indent=formatter.INDENT, 
                                                                        start_date=xtra_dict['start_date'], 
                                                                        end_date=xtra_dict['end_date'])
                    outputter.print_below_new_line(f'\n{result}')
                selected_function, required_length = cli_correlation, 2

            ### FUNCTION: Correlation Time Series
            elif opt == formatter.FUNC_ARG_DICT['correlation_time_series']:
                def cli_correlation_series():
                    ticker_1, ticker_2 = main_args[0], main_args[1]
                    result = statistics.calculate_ito_correlation_series(ticker_1=ticker_1,ticker_2=ticker_2,
                                                                            start_date=xtra_dict['start_date'],
                                                                            end_date=xtra_dict['end_date'])
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
                        if xtra_dict['discount'] is None:
                            discount = markets.cost_of_equity(ticker=arg)
                        else:
                            discount = xtra_dict['discount']
                        model_results[f'{arg}_discount_dividend'] = Cashflow(sample=dividends, 
                                                                                discount_rate=discount).calculate_net_present_value()
                        if print_format_to_screen(xtra_dict):
                            outputter.scalar_result(f'Net Present Value ({arg} dividends)', 
                                                    model_results[f'{arg}_discount_dividend'])

                    if print_json_to_screen(xtra_dict):
                        print(json.dumps(model_results))

                    if xtra_dict['save_file'] is not None:
                        files.save_file(file_to_save=model_results, file_name=xtra_dict['save_file'])

                selected_function, required_length = cli_discount_dividend, 1

            elif opt == formatter.FUNC_ARG_DICT['dividends']:
                def cli_dividends():
                    all_dividends = {}
                    for arg in main_args:
                        dividends = services.get_dividend_history(arg)
                        all_dividends[arg] = dividends
                        if print_format_to_screen(xtra_dict):
                            for date in dividends:
                                outputter.scalar_result(calculation=f'{arg}_dividend({date})', result=dividends[date])
                
                    if print_json_to_screen(xtra_dict):
                        print(json.dumps(all_dividends))
                
                selected_function, required_length = cli_dividends, 1

            ### FUNCTION: Efficient Frontier
            elif opt == formatter.FUNC_ARG_DICT['efficient_frontier']:
                def cli_efficient_frontier():
                    portfolio = Portfolio(tickers=main_args, start_date=xtra_dict['start_date'], 
                                            end_date=xtra_dict['end_date'])
                    frontier = optimizer.calculate_efficient_frontier(portfolio=portfolio)

                    if xtra_dict['suppress'] is None:
                        if xtra_dict['json'] is None:
                            outputter.efficient_frontier(portfolio=portfolio, frontier=frontier,
                                                    investment=xtra_dict['investment'])
                        else:
                            print(json.dumps(files.format_frontier(portfolio=portfolio, frontier=frontier, investment=xtra_dict['investment'])))

                    if xtra_dict['save_file'] is not None:
                        files.save_frontier(portfolio=portfolio, frontier=frontier,
                                            investment=xtra_dict['investment'], 
                                            file_name=xtra_dict['save_file'])
                selected_function, required_length = cli_efficient_frontier, 2

            ### FUNCTION: Maximize Portfolio Return
            elif opt == formatter.FUNC_ARG_DICT['maximize_return']:
                def cli_maximize_return():
                    portfolio = Portfolio(tickers=main_args, start_date=xtra_dict['start_date'], 
                                            end_date=xtra_dict['end_date'])
                    allocation = optimizer.maximize_portfolio_return(portfolio=portfolio)

                    if xtra_dict['suppress'] is None:
                        if xtra_dict['json'] is None:
                            outputter.optimal_result(portfolio=portfolio, allocation=allocation, 
                                                investment=xtra_dict['investment'])
                        else:
                            print(json.dumps(files.format_allocation(allocation=allocation, portfolio=portfolio, investment=xtra_dict['investment'])))

                    if xtra_dict['save_file'] is not None:
                        files.save_allocation(allocation=allocation, portfolio=portfolio, 
                                                file_name=xtra_dict['save_file'], investment=xtra_dict['investment'])
                selected_function, required_length = cli_maximize_return, 2

            ### FUNCTION: Moving Averages of Logarithmic Returns
            elif opt == formatter.FUNC_ARG_DICT['moving_averages']:
                def cli_moving_averages():
                    moving_averages = statistics.calculate_moving_averages(tickers=main_args, 
                                                                            start_date=xtra_dict['start_date'], 
                                                                            end_date=xtra_dict['end_date'])
                    periods = [settings.MA_1_PERIOD, settings.MA_2_PERIOD, settings.MA_3_PERIOD]

                    outputter.moving_average_result(tickers=main_args, averages_output=moving_averages, 
                                                    periods=periods, start_date=xtra_dict['start_date'], 
                                                    end_date=xtra_dict['end_date'])
                selected_function, required_length = cli_moving_averages, 1

            ### FUNCTION: Optimize Portfolio Variance/Volatility
            elif opt == formatter.FUNC_ARG_DICT['optimize_portfolio_variance']:
                def cli_optimize_portfolio_variance():
                    portfolio = Portfolio(tickers=main_args, start_date=xtra_dict['start_date'], end_date=xtra_dict['end_date'])
                    if xtra_dict['optimize_sharpe']:
                        allocation = optimizer.maximize_sharpe_ratio(portfolio=portfolio, target_return=xtra_dict['target'])
                    else:
                        allocation = optimizer.optimize_portfolio_variance(portfolio=portfolio, target_return=xtra_dict['target'])   
                    
                    if xtra_dict['suppress'] is None:
                        if xtra_dict['json'] is None:
                            outputter.optimal_result(portfolio=portfolio, allocation=allocation, investment=xtra_dict['investment'])
                        else:
                            print(json.dumps(files.format_allocation(allocation=allocation,portfolio=portfolio, investment=xtra_dict['investment'])))
                    
                    if xtra_dict['save_file'] is not None:
                        files.save_allocation(allocation=allocation, portfolio=portfolio, file_name=xtra_dict['save_file'],
                                                investment=xtra_dict['investment'])
                selected_function, required_length = cli_optimize_portfolio_variance, 2
            
            elif opt == formatter.FUNC_ARG_DICT['optimize_portfolio_conditional_var']:
                def cli_optimize_conditional_value_at_risk():
                    portfolio = Portfolio(tickers=main_args, start_date=xtra_dict['start_date'], end_date=xtra_dict['end_date'])
                    allocation = optimizer.optimize_conditional_value_at_risk(portfolio=portfolio,
                                                                                prob=xtra_dict['probability'],
                                                                                expiry=xtra_dict['expiry'],
                                                                                target_return=xtra_dict['target'])
                    if print_format_to_screen(xtra_dict):
                        outputter.optimal_result(portfolio=portfolio, allocation=allocation, investment=xtra_dict['investment'])

                    if print_json_to_screen(xtra_dict):
                        print(json.dumps(files.format_allocation(allocation=allocation, portfolio=portfolio, investment=xtra_dict['investment'])))
                    
                    if xtra_dict['save_file'] is not None:
                        files.save_allocation(allocation=allocation, portfolio=portfolio, file_name=xtra_dict['save_file'],
                                                investment=xtra_dict['investment'])
                selected_function, required_length = cli_optimize_conditional_value_at_risk, 2
            ### FUNCTION: Plot Dividend History With Linear Regression Model
            elif opt == formatter.FUNC_ARG_DICT['plot_dividends']:
                def cli_plot_dividends():
                    dividends = services.get_dividend_history(ticker=main_args[0])
                    if xtra_dict['discount'] is None:
                        xtra_dict['discount'] = markets.cost_of_equity(ticker=main_args[0])
                    div_cashflow = Cashflow(sample=dividends, discount_rate=xtra_dict['discount'])
                    plotter.plot_cashflow(ticker=main_args[0], cashflow=div_cashflow, show=True, 
                                            savefile=xtra_dict['save_file'])
                selected_function, required_length, exact = cli_plot_dividends, 1, True

            ### FUNCTION: Plot Efficient Frontier
            elif opt == formatter.FUNC_ARG_DICT['plot_frontier']:
                def cli_plot_frontier():
                    portfolio = Portfolio(tickers=main_args, start_date=xtra_dict['start_date'], 
                                            end_date=xtra_dict['end_date'])
                    frontier = optimizer.calculate_efficient_frontier(portfolio=portfolio)
                    plotter.plot_frontier(portfolio=Portfolio(main_args), frontier=frontier, show=True, 
                                            savefile=xtra_dict['save_file'])
                selected_function, required_length = cli_plot_frontier, 2

            ### FUNCTION: Plot Moving Averages of Logarithmic Returns
            elif opt == formatter.FUNC_ARG_DICT['plot_moving_averages']:
                def cli_plot_moving_averages():
                    moving_averages = statistics.calculate_moving_averages(tickers=main_args, 
                                                                            start_date=xtra_dict['start_date'], 
                                                                            end_date=xtra_dict['end_date'])
                    periods = [settings.MA_1_PERIOD, settings.MA_2_PERIOD, settings.MA_3_PERIOD]
                    plotter.plot_moving_averages(symbols=main_args, averages_output=moving_averages, periods=periods, 
                                                    show=True, savefile=xtra_dict['save_file'])
                selected_function, required_length = cli_plot_moving_averages, 1

            ### FUNCTION: Plot Risk-Return Profile
            elif opt == formatter.FUNC_ARG_DICT['plot_risk_profile']:
                def cli_plot_risk_profile():
                    profiles = {}
                    for arg in main_args:
                        profiles[arg]=statistics.calculate_risk_return(ticker=arg, start_date=xtra_dict['start_date'], 
                                                                            end_date=xtra_dict['end_date'])
                    plotter.plot_profiles(symbols=main_args, profiles=profiles, show=True, 
                                            savefile=xtra_dict['save_file'], 
                                            subtitle=helper.format_date_range(start_date=xtra_dict['start_date'], 
                                                                                end_date=xtra_dict['end_date']))
                selected_function, required_length = cli_plot_risk_profile, 1

            elif opt == formatter.FUNC_ARG_DICT['plot_yield_curve']:
                def cli_plot_yield_curve():
                    yield_curve = {}
                    xtra_dict['start_date'] = helper.get_next_business_date(xtra_dict['start_date'])
                    start_date_string = helper.date_to_string(xtra_dict['start_date'])
                    yield_curve[start_date_string] = []
                    for maturity in static.keys['YIELD_CURVE']:
                        rate = services.get_daily_interest_history(maturity=maturity, start_date=xtra_dict['start_date'],
                                                                    end_date=xtra_dict['start_date'])
                        yield_curve[start_date_string].append(rate[start_date_string])
                
                    plotter.plot_yield_curve(yield_curve=yield_curve, show=True,
                                                savefile=xtra_dict['save_file'])
                
                selected_function, required_length, exact = cli_plot_yield_curve, 0, True
            ### FUNCTION: Price History
            elif opt == formatter.FUNC_ARG_DICT['price_history']:
                def cli_price_history():
                    all_prices = {}
                    for arg in main_args:
                        prices = services.get_daily_price_history(ticker=arg, start_date=xtra_dict['start_date'],
                                                                    end_date=xtra_dict['end_date'])
                        all_prices[arg] = {}
                        for date in prices:
                            price = prices[date][static.keys['PRICES']['CLOSE']]
                            all_prices[arg][date] = price

                            if print_format_to_screen(xtra_dict):
                                outputter.scalar_result(calculation=f'{arg}({date})', result = float(price))

                    if print_json_to_screen(xtra_dict):
                        print(json.dumps(all_prices))

                    if xtra_dict['save_file'] is not None:
                        files.save_file(file_to_save=all_prices, file_name=xtra_dict['save_file'])

                selected_function, required_length = cli_price_history, 1

            ### FUNCTION: Interest Rate History
            elif opt == formatter.FUNC_ARG_DICT['interest_history']:
                def cli_interest_history():
                    all_rates = {}
                    for arg in main_args:
                        all_rates[arg] = services.get_daily_interest_history(maturity=arg, 
                                                                                start_date=xtra_dict['start_date'],
                                                                                end_date=xtra_dict['end_date'])
                        for date in all_rates[arg]:
                            all_rates[arg][date] = all_rates[arg][date]/100
                            
                        if print_format_to_screen(xtra_dict):
                            for date in all_rates[arg]:
                                outputter.scalar_result(calculation=f'{arg}_YIELD({date})', result=float(all_rates[arg][date])/100, currency=False)

                    if print_json_to_screen(xtra_dict):
                        print(json.dumps(all_rates))

                    if xtra_dict['save_file'] is not None:
                        files.save_file(file_to_save=all_rates, file_name=xtra_dict['save_file'])
                
                selected_function, required_length = cli_interest_history, 1
            
            ### FUNCTION: Risk Free Rate
            elif opt == formatter.FUNC_ARG_DICT['risk_free_rate']:
                def cli_risk_free_rate():
                    rate = {}
                    rate[settings.RISK_FREE_RATE] = services.get_risk_free_rate()
                    if xtra_dict['suppress'] is None:
                        if xtra_dict['json'] is None:
                            outputter.title_line("Risk Free Rate")
                            outputter.scalar_result(calculation=formatter.RISK_FREE_TITLE.format(settings.RISK_FREE_RATE), 
                                                        result=rate[settings.RISK_FREE_RATE], currency=False)
                        else:
                            print(json.dumps(rate))

                    if xtra_dict['save_file'] is not None:
                        files.save_file(file_to_save=rate, file_name=xtra_dict['save_file'])

                selected_function, required_length, exact = cli_risk_free_rate, 0, True

            ### FUNCTION: Risk-Return Profile
            elif opt == formatter.FUNC_ARG_DICT["risk_profile"]:
                def cli_risk_return():
                    profiles = {}
                    for arg in main_args:
                        profiles[arg] = statistics.calculate_risk_return(ticker=arg, start_date=xtra_dict['start_date'], 
                                                                            end_date=xtra_dict['end_date'])
                        profiles[arg]['sharpe_ratio'] = markets.sharpe_ratio(ticker=arg, start_date=xtra_dict['start_date'],
                                                                            end_date=xtra_dict['end_date'], 
                                                                            ticker_profile=profiles[arg])
                        profiles[arg]['asset_beta'] = markets.market_beta(ticker=arg, start_date=xtra_dict['start_date'],
                                                                            end_date=xtra_dict['end_date'],
                                                                            ticker_profile=profiles[arg])
                        profiles[arg]['equity_cost'] = markets.cost_of_equity(ticker=arg, start_date=xtra_dict['start_date'],
                                                                            end_date=xtra_dict['end_date'])
                    
                    if xtra_dict['suppress'] is None:
                        if xtra_dict['json'] is None:
                            outputter.risk_profile(profiles=profiles)
                        else:
                            print(json.dumps(profiles))

                    if xtra_dict['save_file'] is not None:
                        files.save_profiles(profiles=profiles, file_name=xtra_dict['save_file'])


                selected_function, required_length = cli_risk_return, 1

            ### FUNCTION: Model Discount Screener 
            elif  opt == formatter.FUNC_ARG_DICT["screener"]:
                if xtra_dict['model'] is None:
                    model = markets.MODEL_DDM
                results = markets.screen_for_discount(model=model, discount_rate=xtra_dict['discount'])
                outputter.screen_results(info=results, model=model)

            ### FUNCTION: Sharpe Ratio
            elif opt == formatter.FUNC_ARG_DICT["sharpe_ratio"]:
                def cli_sharpe_ratio():
                    all_results = {}
                    for arg in main_args:
                        result = markets.sharpe_ratio(ticker=arg, start_date=xtra_dict['start_date'],
                                                        end_date=xtra_dict['end_date'])
                        all_results[arg]=result
                        
                        if print_format_to_screen(xtra_dict):
                            outputter.scalar_result(calculation=f'{arg}_sharpe_ratio', result=result, 
                                                    currency=False)

                    if print_json_to_screen(xtra_dict):
                        print(json.dumps(all_results))

                    if xtra_dict['save_file'] is not None:
                        files.save_file(file_to_save=all_results, file_name=xtra_dict['save_file'])

                selected_function, required_length = cli_sharpe_ratio, 1

            ### FUNCTION: Get Latest Economic Statistic
            elif opt == formatter.FUNC_ARG_DICT["statistic"]:
                # TODO: implement start and end date and print eac.
                def cli_statistic():
                    all_stats = {}
                    for stat in main_args:
                        result = services.get_daily_fred_latest(symbol=stat)
                        all_stats[stat] = result
                        if print_format_to_screen(xtra_dict):
                            outputter.scalar_result(calculation=stat, result=result, currency=False)
    
                    if print_json_to_screen(xtra_dict):
                        print(json.dumps(all_stats))
                    if xtra_dict['save_file'] is not None:
                        files.save_file(file_to_save=all_stats, file_name=xtra_dict['save_file'])

                selected_function, required_length = cli_statistic, 1
            
            ### FUNCTION: Statistic History
            elif opt == formatter.FUNC_ARG_DICT['statistic_history']:
                def cli_statistic_history():
                    all_stats = {}
                    for arg in main_args:
                        stats = services.get_daily_fred_history(symbol=arg, start_date=xtra_dict['start_date'],
                                                            end_date=xtra_dict['end_date'])
                        all_stats[arg] = stats
                        if print_format_to_screen(xtra_dict):
                            for date in stats:
                                outputter.scalar_result(calculation=f'{arg}({date})', result=stats[date], 
                                                            currency=False) 

                    if print_json_to_screen(xtra_dict):
                        print(json.dumps(all_stats))
                    if xtra_dict['save_file'] is not None:
                        files.save_file(file_to_save=all_stats, file_name=xtra_dict['save_file'])
                        
                selected_function, required_length = cli_statistic_history, 1

            ### FUNCTION: Set Watchlist
            elif opt == formatter.FUNC_ARG_DICT["watchlist"]:
                def cli_watchlist():
                    files.add_watchlist(new_tickers=main_args)
                    logger.comment("Watchlist saved. Use -ls option to print watchlist.")
                selected_function, required_length = cli_watchlist, 1
    
            ### FUNCTION: Yield Curve
            elif opt == formatter.FUNC_ARG_DICT['yield_curve']:
                yield_curve = {}
                for maturity in static.keys['YIELD_CURVE']:
                    curve_rate = services.get_daily_interest_latest(maturity=maturity)
                    yield_curve[maturity] = curve_rate/100

                    if print_format_to_screen(xtra_dict):
                        outputter.scalar_result(calculation=maturity, result=curve_rate/100, currency=False)

                if print_json_to_screen(xtra_dict):
                    print(json.dumps(yield_curve))
                    
                if xtra_dict['save_file'] is not None:
                    files.save_file(file_to_save=yield_curve, file_name=xtra_dict['save_file'])

            else:
                logger.comment('No function supplied. Please review Function Summary below and re-execute with appropriate arguments.')
                outputter.help_msg()
            
            if selected_function is not None:
                validate_function_usage(selection=opt, args=main_args, 
                                        wrapper_function=selected_function, 
                                        required_length=required_length, exact=exact)
    
            if print_format_to_screen(xtra_dict):
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