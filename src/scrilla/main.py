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

"""
# CLI Entrypoint 
This script acts as the entrypoint for the CLI application and contains the majority of the control structures for the program. It parses the arguments supplied through the command line, delegates them to the appropriate application function and then passes the results to the `scrilla.util.outputter` module functions for formatting and printing to screen.

The arguments are parsed in such a way that arguments which are not supplied are set to None. All application functions are set up to accept None as a value for their optional arguments. This makes passing arguments to application functions easier as the `main.py` script doesn't have to worry about their values. In other words, `main.py` always passes all arguments to application functions, even if they aren't supplied through the command line; it just sets the ones which aren't supplied to None.
"""

import sys, os, json
from typing import Callable

from scrilla import settings, services, files, static
from scrilla.errors import InputValidationError
from scrilla.util import dater, outputter, formatter, helper
from scrilla.analysis import optimizer, markets, estimators
from scrilla.analysis.models.geometric import statistics, probability

# TODO: conditional imports based on value of ANALYSIS_MODE

from scrilla.analysis.objects.portfolio import Portfolio
from scrilla.analysis.objects.cashflow import Cashflow

if settings.APP_ENV != "container":
    import util.plotter as plotter

logger = outputter.Logger('main', settings.LOG_LEVEL)

non_container_functions = [formatter.FUNC_DICT['plot_dividends'], formatter.FUNC_DICT['plot_moving_averages'],
                               formatter.FUNC_DICT['plot_risk_profile'], formatter.FUNC_DICT['plot_frontier']]

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
        raise InputValidationError('Graphics functionality disabled when application is containerized.')

    if(not exact and (len(args)>(required_length-1))):
        wrapper_function()
    elif(exact and (len(args)==required_length)):
        wrapper_function()
    else:
        raise InputValidationError(f'Invalid number of arguments for \'{selection}\' function.')
        

def print_format_to_screen(args: dict):
    """
    Checks if the inputted optional arguments allow printing pretty formatted text to screen.

    Parameters
    ----------
    1. **args** : ``dict``
        Formatted dictionary containing optional arguments. Result of a call to `helper.format_xtra_args_dict`.
    
    Returns
    -------
    ``bool``
    """
    return args['json'] is None and args['suppress'] is None

def print_json_to_screen(args: dict):
    """
    Checks if inputted optional arguments allow printing json formatted text to screen.
    
    Parameters
    ----------
    1. **args** : ``dict``
        Formatted dictionary containing optional arguments. Result of a call to `helper.format_xtra_args_dict`.
    
    Returns
    -------
    ``bool``
    """
    return args['json'] is not None and args['suppress'] is None

def do_program() -> None:
    """
    Parses command line arguments and passes the formatted arguments to appropriate function from the library.
    """
    if len(sys.argv)>0:
        opt = sys.argv[1]
        logger.debug(f'Selected Function: {opt}')

        # single argument functions
        ### FUNCTION: Help Message
        if opt in formatter.FUNC_DICT["help"]:
            def cli_help():
                outputter.help_msg()
            selected_function, required_length = cli_help, 0

        ### FUNCTION: Clear Cache
        elif opt in formatter.FUNC_DICT["clear_cache"]:
            def cli_clear_cache():
                logger.comment(f'Clearing {settings.CACHE_DIR}')
                files.clear_directory(directory=settings.CACHE_DIR, retain=True)
            selected_function, required_length = cli_clear_cache, 0

        ### FUNCTION: Clear Static
        elif opt in formatter.FUNC_DICT["clear_static"]:
            def cli_clear_static():
                logger.comment(f'Clearing {settings.STATIC_DIR}')
                files.clear_directory(directory=settings.STATIC_DIR, retain=True)
            selected_function, required_length = cli_clear_static, 0

        ### FUNCTION: Clear Common
        elif opt in formatter.FUNC_DICT["clear_common"]:
            def cli_clear_common():
                logger.comment(f'Clearing {settings.COMMON_DIR}')
                files.clear_directory(directory=settings.COMMON_DIR, retain=True)
            selected_function, required_length = cli_clear_common, 0

        ### FUNCTION: Function Examples
        elif opt in formatter.FUNC_DICT["examples"]:
            def cli_examples():
                outputter.examples()
            selected_function, required_length = cli_examples, 0

        ### FUNCTION: Print Stock Watchlist
        elif opt in formatter.FUNC_DICT['list_watchlist']:
            def cli_watchlist():
                tickers = files.get_watchlist()
                outputter.title_line("Stock Watchlist")
                outputter.print_list(tickers)
            selected_function, required_length = cli_watchlist, 0

        ### FUNCTION: Store Key
            # NOTE: not technically a single argument function, but requires special parsing, so
            #       treat it here.
        elif opt in formatter.FUNC_DICT['store']:
            def cli_store():
                key = sys.argv[2].split("=")
                if key[0] in ["ALPHA_VANTAGE_KEY", "QUANDL_KEY", "IEX_KEY"]:
                   files.set_credentials(value=key[1], which_key=key[0])
                else:
                    outputter.comment(f'Key of {key[0]} not recognized. See -help for more information.')
            selected_function, required_length = cli_store, 0

        ### FUNCTION: Purge Data Directories
        elif opt in formatter.FUNC_DICT["purge"]:
            def cli_purge():
                logger.comment(f'Clearing {settings.STATIC_DIR}, {settings.CACHE_DIR} and {settings.CACHE_DIR}')
                files.clear_directory(directory=settings.STATIC_DIR, retain=True)
                files.clear_directory(directory=settings.CACHE_DIR, retain=True)
                files.clear_directory(directory=settings.COMMON_DIR, retain=True)
            selected_function, required_length = cli_purge, 0

        ### FUNCTION: Display Version
        elif opt in formatter.FUNC_DICT["version"]:
            def cli_version():
                version_file = os.path.join(settings.APP_DIR, 'version.txt')
                with open(version_file, 'r') as f:
                    print(f.read())
            selected_function, required_length = cli_version, 0

        # variable argument functions
        else:
            logger.debug('Initialzing /static/ directory, if applicable.')
            files.init_static_data()
            
            args = helper.format_args(sys.argv[2:])
            exact, selected_function = False, None

            if print_format_to_screen(args):
                outputter.title_line('Results')
                outputter.print_line()

            ### FUNCTION: Asset Grouping
            if opt in formatter.FUNC_DICT['asset_type']:
                def cli_asset_type():
                    for arg in args['tickers']:
                        asset_type = files.get_asset_type(arg)
                        if asset_type:
                            outputter.string_result(f'asset_type({arg})', asset_type)
                        else: 
                            logger.comment('Error encountered while determining asset Type. Try -ex flag for example usage.')
                selected_function, required_length = cli_asset_type, 1

            ### FUNCTION: Black-Scholes Value At Risk
            elif opt in formatter.FUNC_DICT['var']:
                def cli_var():
                    all_vars = {}
                    for arg in args['tickers']:
                        prices = services.get_daily_price_history(ticker=arg, 
                                                                    start_date=args['start_date'],
                                                                    end_date=args['end_date'])
                        latest_price = prices[helper.get_first_json_key(prices)][static.keys['PRICES']['CLOSE']]
                        profile = statistics.calculate_risk_return(ticker=arg, 
                                                                    sample_prices=prices, 
                                                                    method=args['estimation'])
                        valueatrisk = probability.percentile(S0=latest_price, 
                                                                vol=profile['annual_volatility'],
                                                                ret=profile['annual_return'], 
                                                                expiry=args['expiry'],
                                                                percentile=args['probability'])
                        all_vars[arg]=valueatrisk

                        if print_format_to_screen(args):
                            outputter.scalar_result(f'{arg}_value_at_risk', valueatrisk)

                    if print_json_to_screen(args):
                        print(json.dumps(all_vars))
                    
                    if args['save_file'] is not None:
                        files.save_file(file_to_save=all_vars, file_name=args['save_file'])

                selected_function, required_length = cli_var, 2
                
            ### FUNCTION: Black-Scholes Conditional Value At Risk
            elif opt in formatter.FUNC_DICT['cvar']:
                def cli_cvar():
                    all_cvars = {}
                    for arg in args['tickers']:
                        prices = services.get_daily_price_history(ticker=arg, 
                                                                    start_date=args['start_date'],
                                                                    end_date=args['end_date'])
                        latest_price = prices[helper.get_first_json_key(prices)][static.keys['PRICES']['CLOSE']]
                        profile = statistics.calculate_risk_return(ticker=arg, 
                                                                    sample_prices=prices, 
                                                                    method=args['estimation'])
                        valueatrisk = probability.percentile(S0=latest_price, 
                                                                vol=profile['annual_volatility'],
                                                                ret=profile['annual_return'], 
                                                                expiry=args['expiry'],
                                                                percentile=args['probability'])
                        cvar = probability.conditional_expected_value(S0=latest_price, 
                                                                        vol=profile['annual_volatility'],
                                                                        ret=profile['annual_return'], 
                                                                        expiry=args['expiry'],
                                                                        conditional_value=valueatrisk)
                        all_cvars[arg]=cvar

                        if print_format_to_screen(args):
                            outputter.scalar_result(f'{arg}_conditional_value_at_risk', valueatrisk)

                    if print_json_to_screen(args):
                        print(json.dumps(all_cvars))
                    
                    if args['save_file'] is not None:
                        files.save_file(file_to_save=all_cvars, file_name=args['save_file'])

                selected_function, required_length = cli_cvar, 2

            ### FUNCTION: Capital Asset Pricing Model Cost of Equity
            elif opt in formatter.FUNC_DICT['capm_equity_cost']:
                def cli_capm_equity_cost():
                    all_costs = {}
                    for arg in args['tickers']:
                        equity_cost = markets.cost_of_equity(ticker=arg, start_date=args['start_date'], 
                                                                end_date=args['end_date'], 
                                                                method=args['estimation'])
                        all_costs[arg] = equity_cost

                        if print_format_to_screen(args):
                            outputter.scalar_result(f'{arg}_equity_cost', equity_cost, currency=False)

                    if print_json_to_screen(args):
                        print(json.dumps(all_costs))

                    if args['save_file'] is not None:
                        files.save_file(file_to_save=all_costs, file_name=args['save_file'])


                selected_function, required_length = cli_capm_equity_cost, 1


            ### FUNCTION: Capital Asset Pricing Model Beta
            elif opt in formatter.FUNC_DICT['capm_beta']:
                def cli_capm_beta():
                    all_betas = {}
                    for arg in args['tickers']:
                        beta = markets.market_beta(ticker=arg, 
                                                    start_date=args['start_date'], 
                                                    end_date=args['end_date'], 
                                                    method=args['estimation'])
                        all_betas[arg] = beta

                        if print_format_to_screen(args):
                            outputter.scalar_result(f'{arg}_beta', beta, currency=False)

                    if print_json_to_screen(args):
                        print(json.loads(all_betas))

                    if args['save_file'] is not None:
                        files.save_file(file_to_save=all_betas, file_name=args['save_file'])

                selected_function, required_length = cli_capm_beta, 1

            ### FUNCTION: Last Close Price
            elif opt in formatter.FUNC_DICT["close"]:
                def cli_close():
                    all_prices = {}
                    for arg in args['tickers']:
                        price = services.get_daily_price_latest(arg)
                        all_prices[arg] = price

                        if print_format_to_screen(args):
                            outputter.scalar_result(calculation=f'Last {arg} close price', result=float(price))

                    if print_json_to_screen(args):
                        print(json.dumps(all_prices))

                    if args['save_file'] is not None:
                        files.save_file(file_to_save=all_prices, file_name=args['save_file'])
                selected_function, required_length = cli_close, 1
                    
            ### FUNCTION: Correlation Matrix
            elif opt in formatter.FUNC_DICT["correlation"]:
                def cli_correlation():
                    if args['estimation'] == static.keys['ESTIMATION']['LIKE']:
                        logger.comment('This calculation takes a while, strap in...')

                    matrix = statistics.correlation_matrix(tickers=args['tickers'],
                                                            start_date=args['start_date'], 
                                                            end_date=args['end_date'],
                                                            method=args['estimation'])
                    if print_format_to_screen(args):
                        outputter.correlation_matrix(tickers=args['tickers'], correlation_matrix=matrix)
    
                    elif print_json_to_screen(args):
                        print(json.dumps(matrix))

                    if args['save_file'] is not None:
                        files.save_file(file_to_save=matrix, file_name=args['save_file'])
                        
                selected_function, required_length = cli_correlation, 2

            ### FUNCTION: Correlation Time Series
            elif opt in formatter.FUNC_DICT['correlation_time_series']:
                def cli_correlation_series():
                    logger.comment('This calculation takes a while, strap in...')
                    ticker_1, ticker_2 = args['tickers'][0], args['tickers'][1]
                    result = statistics.calculate_moment_correlation_series(ticker_1=ticker_1,ticker_2=ticker_2,
                                                                            start_date=args['start_date'],
                                                                            end_date=args['end_date'])
                    if print_format_to_screen(args):
                        for date in result:
                            outputter.scalar_result(calculation=f'{date}_{ticker_1}_{ticker_2}_correlation', 
                                                result=float(result[date]), currency=False)
                    elif print_json_to_screen(args):
                        print(json.dumps(result))

                    if args['save_file'] is not None:
                        files.save_file(file_to_save=result, file_name=args['save_file'])
                    
                selected_function, required_length, exact = cli_correlation_series, 2, True

            ### FUNCTION: Discount Dividend Model
            elif opt in formatter.FUNC_DICT["discount_dividend"]:
                def cli_discount_dividend():
                    model_results = {}
                    for arg in args['tickers']:
                        dividends = services.get_dividend_history(arg)
                        if args['discount'] is None:
                            discount = markets.cost_of_equity(ticker=arg, method=args['estimation'])
                        else:
                            discount = args['discount']
                        model_results[f'{arg}_discount_dividend'] = Cashflow(sample=dividends, 
                                                                                discount_rate=discount).calculate_net_present_value()
                        if print_format_to_screen(args):
                            outputter.scalar_result(f'Net Present Value ({arg} dividends)', 
                                                    model_results[f'{arg}_discount_dividend'])

                    if print_json_to_screen(args):
                        print(json.dumps(model_results))

                    if args['save_file'] is not None:
                        files.save_file(file_to_save=model_results, file_name=args['save_file'])

                selected_function, required_length = cli_discount_dividend, 1

            elif opt in formatter.FUNC_DICT['dividends']:
                def cli_dividends():
                    all_dividends = {}
                    for arg in args['tickers']:
                        dividends = services.get_dividend_history(arg)
                        all_dividends[arg] = dividends
                        if print_format_to_screen(args):
                            for date in dividends:
                                outputter.scalar_result(calculation=f'{arg}_dividend({date})', result=dividends[date])
                
                    if print_json_to_screen(args):
                        print(json.dumps(all_dividends))
                
                selected_function, required_length = cli_dividends, 1

            ### FUNCTION: Efficient Frontier
            elif opt in formatter.FUNC_DICT['efficient_frontier']:
                def cli_efficient_frontier():
                    portfolio = Portfolio(tickers=args['tickers'], 
                                            start_date=args['start_date'], 
                                            end_date=args['end_date'],
                                            method=args['estimation'])
                    frontier = optimizer.calculate_efficient_frontier(portfolio=portfolio, 
                                                                        steps=args['steps'])

                    if args['suppress'] is None:
                        if args['json'] is None:
                            outputter.efficient_frontier(portfolio=portfolio, 
                                                            frontier=frontier,
                                                            investment=args['investment'])
                        else:
                            print(json.dumps(formatter.format_frontier(portfolio=portfolio, 
                                                                        frontier=frontier, 
                                                                        investment=args['investment'])))

                    if args['save_file'] is not None:
                        files.save_frontier(portfolio=portfolio, 
                                            frontier=frontier,
                                            investment=args['investment'], 
                                            file_name=args['save_file'])
                selected_function, required_length = cli_efficient_frontier, 2

            ### FUNCTION: Maximize Portfolio Return
            elif opt in formatter.FUNC_DICT['maximize_return']:
                def cli_maximize_return():
                    portfolio = Portfolio(tickers=args['tickers'], 
                                            start_date=args['start_date'], 
                                            end_date=args['end_date'],
                                            method=args['estimation'])
                    allocation = optimizer.maximize_portfolio_return(portfolio=portfolio)

                    if args['suppress'] is None:
                        if args['json'] is None:
                            outputter.optimal_result(portfolio=portfolio, 
                                                        allocation=allocation, 
                                                        investment=args['investment'])
                        else:
                            print(json.dumps(formatter.format_allocation(allocation=allocation, 
                                                                            portfolio=portfolio, 
                                                                            investment=args['investment'])))

                    if args['save_file'] is not None:
                        files.save_allocation(allocation=allocation, 
                                                portfolio=portfolio, 
                                                file_name=args['save_file'], 
                                                investment=args['investment'])
                selected_function, required_length = cli_maximize_return, 2

            ### FUNCTION: Moving Averages of Logarithmic Returns
            elif opt in formatter.FUNC_DICT['moving_averages']:
                def cli_moving_averages():
                    # TODO: moving averages with estimation techniques
                    # TODO: print results as json to screen and ability to save results
                    moving_averages = statistics.calculate_moving_averages(tickers=args['tickers'], 
                                                                            start_date=args['start_date'], 
                                                                            end_date=args['end_date'])
                    periods = [settings.MA_1_PERIOD, settings.MA_2_PERIOD, settings.MA_3_PERIOD]

                    outputter.moving_average_result(tickers=args['tickers'], averages_output=moving_averages, 
                                                    periods=periods, start_date=args['start_date'], 
                                                    end_date=args['end_date'])
                selected_function, required_length = cli_moving_averages, 1

            ### FUNCTION: Optimize Portfolio Variance/Volatility
            elif opt in formatter.FUNC_DICT['optimize_portfolio_variance']:
                def cli_optimize_portfolio_variance():
                    portfolio = Portfolio(tickers=args['tickers'], 
                                            start_date=args['start_date'], 
                                            end_date=args['end_date'],
                                            method=args['estimation'])

                    if args['optimize_sharpe']:
                        allocation = optimizer.maximize_sharpe_ratio(portfolio=portfolio, target_return=args['target'])
                    else:
                        allocation = optimizer.optimize_portfolio_variance(portfolio=portfolio, target_return=args['target'])   
                    
                    if args['suppress'] is None:
                        if args['json'] is None:
                            outputter.optimal_result(portfolio=portfolio, allocation=allocation, investment=args['investment'])
                        else:
                            print(json.dumps(formatter.format_allocation(allocation=allocation,portfolio=portfolio, investment=args['investment'])))
                    
                    if args['save_file'] is not None:
                        files.save_allocation(allocation=allocation, portfolio=portfolio, file_name=args['save_file'],
                                                investment=args['investment'])
                selected_function, required_length = cli_optimize_portfolio_variance, 2
            
            ### FUNCTION: Optimize Portfolio Conditional Value At Risk 
            elif opt in formatter.FUNC_DICT['optimize_portfolio_conditional_var']:
                def cli_optimize_conditional_value_at_risk():
                    portfolio = Portfolio(tickers=args['tickers'], 
                                            start_date=args['start_date'], 
                                            end_date=args['end_date'],
                                            method=args['estimation'])
                    allocation = optimizer.optimize_conditional_value_at_risk(portfolio=portfolio,
                                                                                prob=args['probability'],
                                                                                expiry=args['expiry'],
                                                                                target_return=args['target'])
                    if print_format_to_screen(args):
                        outputter.optimal_result(portfolio=portfolio, allocation=allocation, investment=args['investment'])

                    if print_json_to_screen(args):
                        print(json.dumps(formatter.format_allocation(allocation=allocation, portfolio=portfolio, investment=args['investment'])))
                    
                    if args['save_file'] is not None:
                        files.save_allocation(allocation=allocation, portfolio=portfolio, file_name=args['save_file'],
                                                investment=args['investment'])
                selected_function, required_length = cli_optimize_conditional_value_at_risk, 2

            ### FUNCTION: Plot Correlation Time Series
            elif opt in formatter.FUNC_DICT['plot_correlation']:
                def cli_plot_correlation():
                    logger.comment('This calculation takes a while, strap in...')
                    correlation_history = statistics.calculate_moment_correlation_series(ticker_1=args['tickers'][0], 
                                                                                        ticker_2=args['tickers'][1], 
                                                                                        start_date=args['start_date'],
                                                                                        end_date=args['end_date'])
                    plotter.plot_correlation_series(tickers=args['tickers'], series=correlation_history, savefile=args['save_file'])

                selected_function, required_length, exact = cli_plot_correlation, 2, True

            ### FUNCTION: Plot Dividend History With Linear Regression Model
            elif opt in formatter.FUNC_DICT['plot_dividends']:
                def cli_plot_dividends():
                    dividends = services.get_dividend_history(ticker=args['tickers'][0])
                    if args['discount'] is None:
                        args['discount'] = markets.cost_of_equity(ticker=args['tickers'][0],
                                                                        method=args['estimation'])
                    div_cashflow = Cashflow(sample=dividends, 
                                            discount_rate=args['discount'])
                    plotter.plot_cashflow(ticker=args['tickers'][0], 
                                            cashflow=div_cashflow, show=True, 
                                            savefile=args['save_file'])
                selected_function, required_length, exact = cli_plot_dividends, 1, True

            ### FUNCTION: Plot Efficient Frontier
            elif opt in formatter.FUNC_DICT['plot_frontier']:
                def cli_plot_frontier():
                    portfolio = Portfolio(tickers=args['tickers'], 
                                            start_date=args['start_date'], 
                                            end_date=args['end_date'],
                                            method=args['estimation'])
                    frontier = optimizer.calculate_efficient_frontier(portfolio=portfolio,
                                                                        steps=args['steps'])
                    plotter.plot_frontier(portfolio=Portfolio(args['tickers']), 
                                            frontier=frontier, 
                                            show=True, 
                                            savefile=args['save_file'])
                selected_function, required_length = cli_plot_frontier, 2

            ### FUNCTION: Plot Moving Averages of Logarithmic Returns
            elif opt in formatter.FUNC_DICT['plot_moving_averages']:
                def cli_plot_moving_averages():
                    # TODO: estimation techniques with moving averages
                    moving_averages = statistics.calculate_moving_averages(tickers=args['tickers'], 
                                                                            start_date=args['start_date'], 
                                                                            end_date=args['end_date'])
                    periods = [settings.MA_1_PERIOD, settings.MA_2_PERIOD, settings.MA_3_PERIOD]
                    plotter.plot_moving_averages(symbols=args['tickers'], 
                                                    averages_output=moving_averages, 
                                                    periods=periods, 
                                                    show=True, savefile=args['save_file'])
                selected_function, required_length = cli_plot_moving_averages, 1

            ### FUNCTION: Plot Return QQ Series
            elif opt in formatter.FUNC_DICT['plot_returns']:
                def cli_plot_returns():
                    asset_type = files.get_asset_type(symbol=args['tickers'][0])
                    prices = services.get_daily_price_history(ticker=args['tickers'][0], 
                                                                start_date=args['start_date'],
                                                                end_date=args['end_date'],
                                                                asset_type=asset_type)
                    returns = statistics.get_sample_of_returns(prices, asset_type)
                    qq_series = estimators.qq_series_for_sample(sample=returns)
                    plotter.plot_qq_series(ticker=args['tickers'][0], 
                                            sample=qq_series, 
                                            show=True, 
                                            savefile=args['save_file'])

                selected_function, required_length, exact = cli_plot_returns, 1, True

            ### FUNCTION: Plot Risk-Return Profile
            elif opt in formatter.FUNC_DICT['plot_risk_profile']:
                def cli_plot_risk_profile():
                    profiles = {}
                    for arg in args['tickers']:
                        profiles[arg]=statistics.calculate_risk_return(ticker=arg, 
                                                                        start_date=args['start_date'], 
                                                                        end_date=args['end_date'],
                                                                        method=args['estimation'])
                    plotter.plot_profiles(symbols=args['tickers'], 
                                            show=True,
                                            profiles=profiles, 
                                            savefile=args['save_file'], 
                                            subtitle=dater.format_date_range(start_date=args['start_date'], 
                                                                                end_date=args['end_date']))
                selected_function, required_length = cli_plot_risk_profile, 1

            elif opt in formatter.FUNC_DICT['plot_yield_curve']:
                def cli_plot_yield_curve():
                    yield_curve = {}
                    args['start_date'] = dater.get_next_business_date(args['start_date'])
                    start_date_string = dater.date_to_string(args['start_date'])
                    yield_curve[start_date_string] = []
                    for maturity in static.keys['YIELD_CURVE']:
                        rate = services.get_daily_interest_history(maturity=maturity, 
                                                                    start_date=args['start_date'],
                                                                    end_date=args['start_date'])
                        yield_curve[start_date_string].append(rate[start_date_string])
                
                    plotter.plot_yield_curve(yield_curve=yield_curve, show=True,
                                                savefile=args['save_file'])
                
                selected_function, required_length, exact = cli_plot_yield_curve, 0, True
            ### FUNCTION: Price History
            elif opt in formatter.FUNC_DICT['price_history']:
                def cli_price_history():
                    all_prices = {}
                    for arg in args['tickers']:
                        prices = services.get_daily_price_history(ticker=arg, 
                                                                    start_date=args['start_date'],
                                                                    end_date=args['end_date'])
                        all_prices[arg] = {}
                        for date in prices:
                            price = prices[date][static.keys['PRICES']['CLOSE']]
                            all_prices[arg][date] = price

                            if print_format_to_screen(args):
                                outputter.scalar_result(calculation=f'{arg}({date})', result = float(price))

                    if print_json_to_screen(args):
                        print(json.dumps(all_prices))

                    if args['save_file'] is not None:
                        files.save_file(file_to_save=all_prices, file_name=args['save_file'])

                selected_function, required_length = cli_price_history, 1

            ### FUNCTION: Interest Rate History
            elif opt in formatter.FUNC_DICT['interest_history']:
                def cli_interest_history():
                    all_rates = {}
                    for arg in args['tickers']:
                        all_rates[arg] = services.get_daily_interest_history(maturity=arg, 
                                                                                start_date=args['start_date'],
                                                                                end_date=args['end_date'])
                        for date in all_rates[arg]:
                            all_rates[arg][date] = all_rates[arg][date]/100
                            
                        if print_format_to_screen(args):
                            for date in all_rates[arg]:
                                outputter.scalar_result(calculation=f'{arg}_YIELD({date})', result=float(all_rates[arg][date])/100, currency=False)

                    if print_json_to_screen(args):
                        print(json.dumps(all_rates))

                    if args['save_file'] is not None:
                        files.save_file(file_to_save=all_rates, file_name=args['save_file'])
                
                selected_function, required_length = cli_interest_history, 1
            
            ### FUNCTION: Risk Free Rate
            elif opt in formatter.FUNC_DICT['risk_free_rate']:
                def cli_risk_free_rate():
                    rate = {}
                    rate[settings.RISK_FREE_RATE] = services.get_risk_free_rate()
                    if args['suppress'] is None:
                        if args['json'] is None:
                            outputter.title_line("Risk Free Rate")
                            outputter.scalar_result(calculation=formatter.RISK_FREE_TITLE.format(settings.RISK_FREE_RATE), 
                                                        result=rate[settings.RISK_FREE_RATE], currency=False)
                        else:
                            print(json.dumps(rate))

                    if args['save_file'] is not None:
                        files.save_file(file_to_save=rate, file_name=args['save_file'])

                selected_function, required_length, exact = cli_risk_free_rate, 0, True

            ### FUNCTION: Risk-Return Profile
            elif opt in formatter.FUNC_DICT["risk_profile"]:
                def cli_risk_return():
                    profiles = {}
                    for arg in args['tickers']:
                        profiles[arg] = statistics.calculate_risk_return(ticker=arg, 
                                                                            method = args['estimation'],
                                                                            start_date=args['start_date'], 
                                                                            end_date=args['end_date'])
                        profiles[arg]['sharpe_ratio'] = markets.sharpe_ratio(ticker=arg, 
                                                                            start_date=args['start_date'],
                                                                            end_date=args['end_date'], 
                                                                            ticker_profile=profiles[arg],
                                                                            method=args['estimation'])
                        profiles[arg]['asset_beta'] = markets.market_beta(ticker=arg, 
                                                                            start_date=args['start_date'],
                                                                            end_date=args['end_date'],
                                                                            ticker_profile=profiles[arg],
                                                                            method=args['estimation'])
                        profiles[arg]['equity_cost'] = markets.cost_of_equity(ticker=arg, 
                                                                            start_date=args['start_date'],
                                                                            end_date=args['end_date'], 
                                                                            method=args['estimation'])
                    
                    if args['suppress'] is None:
                        if args['json'] is None:
                            outputter.risk_profile(profiles=profiles)
                        else:
                            print(json.dumps(profiles))

                    if args['save_file'] is not None:
                        files.save_profiles(profiles=profiles, file_name=args['save_file'])


                selected_function, required_length = cli_risk_return, 1

            ### FUNCTION: Model Discount Screener 
            elif  opt in formatter.FUNC_DICT["screener"]:
                if args['model'] is None:
                    model = markets.MODEL_DDM
                results = markets.screen_for_discount(model=model, discount_rate=args['discount'])
                outputter.screen_results(info=results, model=model)

            ### FUNCTION: Sharpe Ratio
            elif opt in formatter.FUNC_DICT["sharpe_ratio"]:
                def cli_sharpe_ratio():
                    all_results = {}
                    for arg in args['tickers']:
                        result = markets.sharpe_ratio(ticker=arg, 
                                                        start_date=args['start_date'],
                                                        end_date=args['end_date'],
                                                        method=args['estimation'])
                        all_results[arg]=result
                        
                        if print_format_to_screen(args):
                            outputter.scalar_result(calculation=f'{arg}_sharpe_ratio', result=result, 
                                                    currency=False)

                    if print_json_to_screen(args):
                        print(json.dumps(all_results))

                    if args['save_file'] is not None:
                        files.save_file(file_to_save=all_results, file_name=args['save_file'])

                selected_function, required_length = cli_sharpe_ratio, 1

            ### FUNCTION: Get Latest Economic Statistic
            elif opt in formatter.FUNC_DICT["statistic"]:
                def cli_statistic():
                    all_stats = {}
                    for stat in args['tickers']:
                        result = services.get_daily_fred_latest(symbol=stat)
                        all_stats[stat] = result
                        if print_format_to_screen(args):
                            outputter.scalar_result(calculation=stat, result=result, currency=False)
    
                    if print_json_to_screen(args):
                        print(json.dumps(all_stats))

                    if args['save_file'] is not None:
                        files.save_file(file_to_save=all_stats, file_name=args['save_file'])

                selected_function, required_length = cli_statistic, 1
            
            ### FUNCTION: Statistic History
            elif opt in formatter.FUNC_DICT['statistic_history']:
                def cli_statistic_history():
                    all_stats = {}
                    for arg in args['tickers']:
                        stats = services.get_daily_fred_history(symbol=arg, 
                                                                start_date=args['start_date'],
                                                                end_date=args['end_date'])
                        all_stats[arg] = stats
                        if print_format_to_screen(args):
                            for date in stats:
                                outputter.scalar_result(calculation=f'{arg}({date})', 
                                                            result=stats[date], 
                                                            currency=False) 

                    if print_json_to_screen(args):
                        print(json.dumps(all_stats))
                    if args['save_file'] is not None:
                        files.save_file(file_to_save=all_stats, file_name=args['save_file'])
                        
                selected_function, required_length = cli_statistic_history, 1

            ### FUNCTION: Set Watchlist
            elif opt in formatter.FUNC_DICT["watchlist"]:
                def cli_watchlist():
                    files.add_watchlist(new_tickers=args['tickers'])
                    logger.comment("Watchlist saved. Use -ls option to print watchlist.")
                selected_function, required_length = cli_watchlist, 1
    
            ### FUNCTION: Yield Curve
            elif opt in formatter.FUNC_DICT['yield_curve']:
                yield_curve = {}
                for maturity in static.keys['YIELD_CURVE']:
                    curve_rate = services.get_daily_interest_latest(maturity=maturity)
                    yield_curve[maturity] = curve_rate/100

                    if print_format_to_screen(args):
                        outputter.scalar_result(calculation=maturity, result=curve_rate/100, currency=False)

                if print_json_to_screen(args):
                    print(json.dumps(yield_curve))
                    
                if args['save_file'] is not None:
                    files.save_file(file_to_save=yield_curve, file_name=args['save_file'])

            else:
                logger.comment('No function supplied. Please review Function Summary below and re-execute with appropriate arguments.')
                outputter.help_msg()
            
            if selected_function is not None:
                validate_function_usage(selection=opt, 
                                            args=args['tickers'],
                                            wrapper_function=selected_function, 
                                            required_length=required_length, 
                                            exact=exact)
    
            if print_format_to_screen(args):
                outputter.print_line()
    else:
        logger.comment('No arguments Supplied. Please review function summary below and re-execute with appropriate arguments.')
        outputter.help_msg()

if __name__ == "__main__": 
    do_program()