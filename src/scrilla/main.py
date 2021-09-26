# This file is part of scrilla: https://github.com/chinchalinchin/scrilla.

# scrilla is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 3
# as published by the Free Software Foundation.

# scrilla is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with scrilla.  If not, see <https://www.gnu.org/licenses/>
# or <https://github.com/chinchalinchin/scrilla/blob/develop/main/LICENSE>.

import sys, os, traceback, json
from typing import Callable

from scrilla import settings, services, files, static
from scrilla.errors import APIResponseError, ConfigurationError, InputValidationError, SampleSizeError, PriceError
from scrilla.util import helper, outputter, formatter
from scrilla.analysis import optimizer, markets, estimators
from scrilla.analysis.models.geometric import statistics, probability
# TODO: conditional imports based on value of ANALYSIS_MODE

from scrilla.analysis.objects.portfolio import Portfolio
from scrilla.analysis.objects.cashflow import Cashflow

if settings.APP_ENV != "container":
    import util.plotter as plotter

logger = outputter.Logger('main', settings.LOG_LEVEL)

"""
# CLI Entrypoint 
This script acts as the entrypoint for the CLI application and contains the majority of the control structures for the program. It parses the arguments supplied through the command line, delegates them to the appropriate application function and then passes the results to the `scrilla.outputter` module functions for formatting and printing to screen.

The arguments are parsed in such a way that arguments which are not supplied are set to None. All application functions are set up to accept None as a value for their optional arguments. This makes passing arguments to application functions easier as the `main.py` script doesn't have to worry about their values. In other words, `main.py` always passes all arguments to application functions, even if they aren't supplied through the command line; it just sets the ones which aren't supplied to None.

.. notes::
    * The idea behind the structure of the modules in this library is as follows: each sub-module should only depend on the sub-modules above it in the hierarchy of modules. At the top level, the modules are: `cache`, `errors`, `files`, `graphics`, `services`, `settings` and `static`. All of this modules are relatively independent (except the `settings` module which configures aspects of all the other modules, but it is made up entirely of values parsed from the environment and shouldn't introduce any circular dependencies), and expose mutually exclusive functionality. As you drill down in the sub-modules, the functions therein contain dependencies on the modules above them; for instance, the `analysis.markets` has dependencies on `services`, but `services` does not have dependencies on `analysis.markets`. There are instances where this design principle has been violated, but by and large, this is the motivating idea behind this project's organization.
"""
non_container_functions = [formatter.FUNC_ARG_DICT['plot_dividends'], formatter.FUNC_ARG_DICT['plot_moving_averages'],
                               formatter.FUNC_ARG_DICT['plot_risk_profile'], formatter.FUNC_ARG_DICT['plot_frontier']]

def validate_function_usage(selection: str, args: list, wrapper_function: Callable[[], None], required_length: int=1, exact: bool=False) -> None:
    """
    Parameters
    ----------
    1. **selection** : ``str``
    2. **args**: ``list``
        List of ticker/statistic symbols whose length is be to validated.
    3. **wrapper_function** : ``func()``
    4. **required_length** : ``int``
    5. **exact** : ``bool``
        *Optional*. If the required length constraint is an equality, set to `True`. If the constraint is an inequality, set to `False`. Defaults to `False`. 
    """
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

def print_format_to_screen(xtra_dict: dict):
    """
    Checks if the inputted optional arguments allow printing pretty formatted text to screen.

    Parameters
    ----------
    1. **xtra_dict** : ``dict``
        Formatted dictionary containing optional arguments. Result of a call to `helper.format_xtra_args_dict`.
    
    Returns
    -------
    ``bool``
    """
    return xtra_dict['json'] is None and xtra_dict['suppress'] is None

def print_json_to_screen(xtra_dict: dict):
    """
    Checks if inputted optional arguments allow printing json formatted text to screen.
    
    Parameters
    ----------
    1. **xtra_dict** : ``dict``
        Formatted dictionary containing optional arguments. Result of a call to `helper.format_xtra_args_dict`.
    
    Returns
    -------
    ``bool``
    """
    return xtra_dict['json'] is not None and xtra_dict['suppress'] is None

def do_program() -> None:
    """
    Parses command line arguments and passes the formatted arguments to appropriate function from the library.
    """
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

        ### FUNCTION: Clear Common
        elif opt == formatter.FUNC_ARG_DICT["clear_common"]:
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
            xtra_dict = helper.format_xtra_args_dict(xtra_args, xtra_values, settings.ESTIMATION_METHOD)
            logger.log_arguments(main_args,xtra_args,xtra_values)
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
            elif opt == formatter.FUNC_ARG_DICT['var']:
                def cli_var():
                    all_vars = {}
                    for arg in main_args:
                        prices = services.get_daily_price_history(ticker=arg, 
                                                                    start_date=xtra_dict['start_date'],
                                                                    end_date=xtra_dict['end_date'])
                        latest_price = prices[helper.get_first_json_key(prices)]
                        profile = statistics.calculate_risk_return(ticker=arg, 
                                                                    sample_prices=prices, 
                                                                    method=xtra_dict['estimation'])
                        valueatrisk = probability.percentile(S0=latest_price, 
                                                                vol=profile['annual_volatility'],
                                                                ret=profile['annual_return'], 
                                                                expiry=xtra_dict['expiry'],
                                                                percentile=xtra_dict['probability'])
                        all_vars[arg]=valueatrisk

                        if print_format_to_screen(xtra_dict):
                            outputter.scalar_result(f'{arg}_value_at_risk', valueatrisk)

                    if print_json_to_screen(xtra_dict):
                        print(json.dump(all_vars))
                    
                    if xtra_dict['save_file'] is not None:
                        files.save_file(file_to_save=all_vars, file_name=xtra_dict['save_file'])

                selected_function, required_length = cli_var, 2
                
            ### FUNCTION: Black-Scholes Conditional Value At Risk
            elif opt == formatter.FUNC_ARG_DICT['cvar']:
                def cli_var():
                    all_cvars = {}
                    for arg in main_args:
                        prices = services.get_daily_price_history(ticker=arg, 
                                                                    start_date=xtra_dict['start_date'],
                                                                    end_date=xtra_dict['end_date'])
                        latest_price = prices[helper.get_first_json_key(prices)]
                        profile = statistics.calculate_moment_risk_return(ticker=arg, 
                                                                            sample_prices=prices, 
                                                                            method=xtra_dict['estimation'])
                        valueatrisk = probability.percentile(S0=latest_price, 
                                                                vol=profile['annual_volatility'],
                                                                ret=profile['annual_return'], 
                                                                expiry=xtra_dict['expiry'],
                                                                percentile=xtra_dict['probability'])
                        cvar = probability.conditional_expected_value(S0=latest_price, 
                                                                        vol=profile['annual_volatility'],
                                                                        ret=profile['annual_return'], 
                                                                        expiry=xtra_dict['expiry'],
                                                                        conditional_value=valueatrisk)
                        all_cvars[arg]=cvar

                        if print_format_to_screen(xtra_dict):
                            outputter.scalar_result(f'{arg}_value_at_risk', valueatrisk)

                    if print_json_to_screen(xtra_dict):
                        print(json.dumps(all_cvars))
                    
                    if xtra_dict['save_file'] is not None:
                        files.save_file(file_to_save=all_cvars, file_name=xtra_dict['save_file'])

                selected_function, required_length = cli_var, 2

            ### FUNCTION: Capital Asset Pricing Model Cost of Equity
            elif opt == formatter.FUNC_ARG_DICT['capm_equity_cost']:
                def cli_capm_equity_cost():
                    all_costs = {}
                    for arg in main_args:
                        equity_cost = markets.cost_of_equity(ticker=arg, start_date=xtra_dict['start_date'], 
                                                                end_date=xtra_dict['end_date'], 
                                                                method=xtra_dict['estimation'])
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
                        beta = markets.market_beta(ticker=arg, 
                                                    start_date=xtra_dict['start_date'], 
                                                    end_date=xtra_dict['end_date'], 
                                                    method=xtra_dict['estimation'])
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
                    matrix = statistics.correlation_matrix(tickers=main_args,
                                                            start_date=xtra_dict['start_date'], 
                                                            end_date=xtra_dict['end_date'],
                                                            method=xtra_dict['estimation'])
                    if print_format_to_screen(xtra_dict):
                        outputter.correlation_matrix(tickers=main_args, correlation_matrix=matrix)
    
                    elif print_json_to_screen(xtra_dict):
                        print(json.dumps(matrix))

                    if xtra_dict['save_file'] is not None:
                        files.save_file(file_to_save=matrix, file_name=xtra_dict['save_file'])
                        
                selected_function, required_length = cli_correlation, 2

            ### FUNCTION: Correlation Time Series
            elif opt == formatter.FUNC_ARG_DICT['correlation_time_series']:
                def cli_correlation_series():
                    ticker_1, ticker_2 = main_args[0], main_args[1]
                    result = statistics.calculate_moment_correlation_series(ticker_1=ticker_1,ticker_2=ticker_2,
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
                            discount = markets.cost_of_equity(ticker=arg, method=xtra_dict['estimation'])
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
                    portfolio = Portfolio(tickers=main_args, 
                                            start_date=xtra_dict['start_date'], 
                                            end_date=xtra_dict['end_date'],
                                            method=xtra_dict['estimation'])
                    frontier = optimizer.calculate_efficient_frontier(portfolio=portfolio, 
                                                                        steps=xtra_dict['steps'])

                    if xtra_dict['suppress'] is None:
                        if xtra_dict['json'] is None:
                            outputter.efficient_frontier(portfolio=portfolio, 
                                                            frontier=frontier,
                                                            investment=xtra_dict['investment'])
                        else:
                            print(json.dumps(formatter.format_frontier(portfolio=portfolio, 
                                                                        frontier=frontier, 
                                                                        investment=xtra_dict['investment'])))

                    if xtra_dict['save_file'] is not None:
                        files.save_frontier(portfolio=portfolio, 
                                            frontier=frontier,
                                            investment=xtra_dict['investment'], 
                                            file_name=xtra_dict['save_file'])
                selected_function, required_length = cli_efficient_frontier, 2

            ### FUNCTION: Maximize Portfolio Return
            elif opt == formatter.FUNC_ARG_DICT['maximize_return']:
                def cli_maximize_return():
                    portfolio = Portfolio(tickers=main_args, 
                                            start_date=xtra_dict['start_date'], 
                                            end_date=xtra_dict['end_date'],
                                            method=xtra_dict['estimation'])
                    allocation = optimizer.maximize_portfolio_return(portfolio=portfolio)

                    if xtra_dict['suppress'] is None:
                        if xtra_dict['json'] is None:
                            outputter.optimal_result(portfolio=portfolio, 
                                                        allocation=allocation, 
                                                        investment=xtra_dict['investment'])
                        else:
                            print(json.dumps(formatter.format_allocation(allocation=allocation, 
                                                                            portfolio=portfolio, 
                                                                            investment=xtra_dict['investment'])))

                    if xtra_dict['save_file'] is not None:
                        files.save_allocation(allocation=allocation, 
                                                portfolio=portfolio, 
                                                file_name=xtra_dict['save_file'], 
                                                investment=xtra_dict['investment'])
                selected_function, required_length = cli_maximize_return, 2

            ### FUNCTION: Moving Averages of Logarithmic Returns
            elif opt == formatter.FUNC_ARG_DICT['moving_averages']:
                def cli_moving_averages():
                    # TODO: moving averages with estimation techniques
                    # TODO: print results as json to screen and ability to save results
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
                    portfolio = Portfolio(tickers=main_args, 
                                            start_date=xtra_dict['start_date'], 
                                            end_date=xtra_dict['end_date'],
                                            method=xtra_dict['estimation'])

                    if xtra_dict['optimize_sharpe']:
                        allocation = optimizer.maximize_sharpe_ratio(portfolio=portfolio, target_return=xtra_dict['target'])
                    else:
                        allocation = optimizer.optimize_portfolio_variance(portfolio=portfolio, target_return=xtra_dict['target'])   
                    
                    if xtra_dict['suppress'] is None:
                        if xtra_dict['json'] is None:
                            outputter.optimal_result(portfolio=portfolio, allocation=allocation, investment=xtra_dict['investment'])
                        else:
                            print(json.dumps(formatter.format_allocation(allocation=allocation,portfolio=portfolio, investment=xtra_dict['investment'])))
                    
                    if xtra_dict['save_file'] is not None:
                        files.save_allocation(allocation=allocation, portfolio=portfolio, file_name=xtra_dict['save_file'],
                                                investment=xtra_dict['investment'])
                selected_function, required_length = cli_optimize_portfolio_variance, 2
            
            elif opt == formatter.FUNC_ARG_DICT['optimize_portfolio_conditional_var']:
                def cli_optimize_conditional_value_at_risk():
                    portfolio = Portfolio(tickers=main_args, 
                                            start_date=xtra_dict['start_date'], 
                                            end_date=xtra_dict['end_date'],
                                            method=xtra_dict['estimation'])
                    allocation = optimizer.optimize_conditional_value_at_risk(portfolio=portfolio,
                                                                                prob=xtra_dict['probability'],
                                                                                expiry=xtra_dict['expiry'],
                                                                                target_return=xtra_dict['target'])
                    if print_format_to_screen(xtra_dict):
                        outputter.optimal_result(portfolio=portfolio, allocation=allocation, investment=xtra_dict['investment'])

                    if print_json_to_screen(xtra_dict):
                        print(json.dumps(formatter.format_allocation(allocation=allocation, portfolio=portfolio, investment=xtra_dict['investment'])))
                    
                    if xtra_dict['save_file'] is not None:
                        files.save_allocation(allocation=allocation, portfolio=portfolio, file_name=xtra_dict['save_file'],
                                                investment=xtra_dict['investment'])
                selected_function, required_length = cli_optimize_conditional_value_at_risk, 2

            ### FUNCTION: Plot Dividend History With Linear Regression Model
            elif opt == formatter.FUNC_ARG_DICT['plot_dividends']:
                def cli_plot_dividends():
                    dividends = services.get_dividend_history(ticker=main_args[0])
                    if xtra_dict['discount'] is None:
                        xtra_dict['discount'] = markets.cost_of_equity(ticker=main_args[0],
                                                                        method=xtra_dict['estimation'])
                    div_cashflow = Cashflow(sample=dividends, 
                                            discount_rate=xtra_dict['discount'])
                    plotter.plot_cashflow(ticker=main_args[0], 
                                            cashflow=div_cashflow, show=True, 
                                            savefile=xtra_dict['save_file'])
                selected_function, required_length, exact = cli_plot_dividends, 1, True

            ### FUNCTION: Plot Efficient Frontier
            elif opt == formatter.FUNC_ARG_DICT['plot_frontier']:
                def cli_plot_frontier():
                    portfolio = Portfolio(tickers=main_args, 
                                            start_date=xtra_dict['start_date'], 
                                            end_date=xtra_dict['end_date'],
                                            method=xtra_dict['estimation'])
                    frontier = optimizer.calculate_efficient_frontier(portfolio=portfolio,
                                                                        steps=xtra_dict['steps'])
                    plotter.plot_frontier(portfolio=Portfolio(main_args), 
                                            frontier=frontier, 
                                            show=True, 
                                            savefile=xtra_dict['save_file'])
                selected_function, required_length = cli_plot_frontier, 2

            ### FUNCTION: Plot Moving Averages of Logarithmic Returns
            elif opt == formatter.FUNC_ARG_DICT['plot_moving_averages']:
                def cli_plot_moving_averages():
                    # TODO: estimation techniques with moving averages
                    moving_averages = statistics.calculate_moving_averages(tickers=main_args, 
                                                                            start_date=xtra_dict['start_date'], 
                                                                            end_date=xtra_dict['end_date'])
                    periods = [settings.MA_1_PERIOD, settings.MA_2_PERIOD, settings.MA_3_PERIOD]
                    plotter.plot_moving_averages(symbols=main_args, 
                                                    averages_output=moving_averages, 
                                                    periods=periods, 
                                                    show=True, savefile=xtra_dict['save_file'])
                selected_function, required_length = cli_plot_moving_averages, 1

            ### FUNCTION: Plot Return QQ Series
            elif opt == formatter.FUNC_ARG_DICT['plot_returns']:
                def cli_plot_returns():
                    asset_type = files.get_asset_type(symbol=main_args[0])
                    prices = services.get_daily_price_history(ticker=main_args[0], 
                                                                start_date=xtra_dict['start_date'],
                                                                end_date=xtra_dict['end_date'],
                                                                asset_type=asset_type)
                    returns = statistics.get_sample_of_returns(prices, asset_type)
                    qq_series = estimators.qq_series_for_sample(sample=returns)
                    plotter.plot_qq_series(ticker=main_args[0], 
                                            sample=qq_series, 
                                            show=True, 
                                            savefile=xtra_dict['save_file'])

                selected_function, required_length, exact = cli_plot_returns, 1, True

            ### FUNCTION: Plot Risk-Return Profile
            elif opt == formatter.FUNC_ARG_DICT['plot_risk_profile']:
                def cli_plot_risk_profile():
                    profiles = {}
                    for arg in main_args:
                        profiles[arg]=statistics.calculate_risk_return(ticker=arg, 
                                                                        start_date=xtra_dict['start_date'], 
                                                                        end_date=xtra_dict['end_date'],
                                                                        method=xtra_args['estimation'])
                    plotter.plot_profiles(symbols=main_args, 
                                            show=True,
                                            profiles=profiles, 
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
                        rate = services.get_daily_interest_history(maturity=maturity, 
                                                                    start_date=xtra_dict['start_date'],
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
                        prices = services.get_daily_price_history(ticker=arg, 
                                                                    start_date=xtra_dict['start_date'],
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
                        profiles[arg] = statistics.calculate_risk_return(ticker=arg, 
                                                                            method = xtra_dict['estimation'],
                                                                            start_date=xtra_dict['start_date'], 
                                                                            end_date=xtra_dict['end_date'])
                        profiles[arg]['sharpe_ratio'] = markets.sharpe_ratio(ticker=arg, 
                                                                            start_date=xtra_dict['start_date'],
                                                                            end_date=xtra_dict['end_date'], 
                                                                            ticker_profile=profiles[arg],
                                                                            method=xtra_dict['estimation'])
                        profiles[arg]['asset_beta'] = markets.market_beta(ticker=arg, 
                                                                            start_date=xtra_dict['start_date'],
                                                                            end_date=xtra_dict['end_date'],
                                                                            ticker_profile=profiles[arg],
                                                                            method=xtra_dict['estimation'])
                        profiles[arg]['equity_cost'] = markets.cost_of_equity(ticker=arg, 
                                                                            start_date=xtra_dict['start_date'],
                                                                            end_date=xtra_dict['end_date'], 
                                                                            method=xtra_dict['estimation'])
                    
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
                        result = markets.sharpe_ratio(ticker=arg, 
                                                        start_date=xtra_dict['start_date'],
                                                        end_date=xtra_dict['end_date'],
                                                        method=xtra_dict['estimation'])
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
                        stats = services.get_daily_fred_history(symbol=arg, 
                                                                start_date=xtra_dict['start_date'],
                                                                end_date=xtra_dict['end_date'])
                        all_stats[arg] = stats
                        if print_format_to_screen(xtra_dict):
                            for date in stats:
                                outputter.scalar_result(calculation=f'{arg}({date})', 
                                                            result=stats[date], 
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
                validate_function_usage(selection=opt, 
                                            args=main_args, 
                                            wrapper_function=selected_function, 
                                            required_length=required_length, 
                                            exact=exact)
    
            if print_format_to_screen(xtra_dict):
                outputter.print_line()
    else:
        logger.comment('No arguments Supplied. Please review function summary below and re-execute with appropriate arguments.')
        outputter.help_msg()

if __name__ == "__main__": 
    do_program()