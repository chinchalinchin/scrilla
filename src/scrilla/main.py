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

import time
from datetime import date
from typing import Callable, Dict, List, Union

from scrilla.settings import LOG_LEVEL, ESTIMATION_METHOD
from scrilla.static import definitions
from scrilla.errors import InputValidationError
from scrilla.files import init_static_data
from scrilla.util.helper import format_args
from scrilla.util.outputter import Logger

# TODO: conditional imports based on value of ANALYSIS_MODE

logger = Logger('main', LOG_LEVEL)


def validate_function_usage(selection: str, args: List[str], wrapper_function: Callable, required_length: int = 1, exact: bool = False) -> None:
    """
    Parameters
    ----------
    1. **selection** : ``str``
    2. **args**: ``list``
        List of ticker/statistic symbols whose length is be to validated.
    3. **wrapper_function** : ``func()``
    4. **required_length** : ``int``
        The number of tickers required for the function.
    5. **exact** : ``bool``
        *Optional*. If the required length constraint is an equality, set to `True`. If the constraint is an inequality, set to `False`. Defaults to `False`. 
    """

    start_time = time.time()
    if(not exact and (len(args) > (required_length-1))) or (exact and (len(args) == required_length)):
        wrapper_function()
    elif exact:
        raise InputValidationError(
            f'Invalid number of arguments for \'{selection}\' function. Function requires {required_length} arguments.')
    else:
        raise InputValidationError(
            f'Invalid number of arguments for \'{selection}\' function. Function requires more than {required_length} arguments.')
    end_time = time.time()
    logger.info(f'Total execution time: {end_time - start_time}s')


def print_format_to_screen(args: Dict[str, Union[str, date, float, None, bool]]) -> bool:
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
    return not args['json'] and not args['suppress_output']


def print_json_to_screen(args: Dict[str, Union[str, date, float, None, bool]]) -> bool:
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
    return args['json'] and not args['suppress_output']


def do_program(cli_args: List[str]) -> None:
    """
    Parses command line arguments and passes the formatted arguments to appropriate function from the library.
    """
    init_static_data()
    args = format_args(cli_args, ESTIMATION_METHOD)
    exact, selected_function = False, None

    # START CLI FUNCTION DEFINITIONS

    # NO ARGUMENT FUNCTIONS
    # FUNCTION: Help Message
    if args['function_arg'] in definitions.FUNC_DICT["help"]['values']:
        def cli_help():
            from scrilla.util.outputter import help_msg
            help_msg()
        selected_function, required_length = cli_help, 0

    # FUNCTION: Clear Cache
    elif args['function_arg'] in definitions.FUNC_DICT["clear_cache"]['values']:
        def cli_clear_cache():
            from scrilla.files import clear_directory
            from scrilla.settings import CACHE_DIR
            logger.comment(f'Clearing {CACHE_DIR}')
            clear_directory(directory=CACHE_DIR, retain=True)
        selected_function, required_length = cli_clear_cache, 0

    # FUNCTION: Clear Static
    elif args['function_arg'] in definitions.FUNC_DICT["clear_static"]['values']:
        def cli_clear_static():
            from scrilla.files import clear_directory
            from scrilla.settings import STATIC_DIR
            logger.comment(f'Clearing {STATIC_DIR}')
            clear_directory(directory=STATIC_DIR, retain=True)
        selected_function, required_length = cli_clear_static, 0

    # FUNCTION: Clear Common
    elif args['function_arg'] in definitions.FUNC_DICT["clear_common"]['values']:
        def cli_clear_common():
            from scrilla.files import clear_directory
            from scrilla.settings import COMMON_DIR
            logger.comment(f'Clearing {COMMON_DIR}')
            clear_directory(directory=COMMON_DIR, retain=True)
        selected_function, required_length = cli_clear_common, 0

    # FUNCTION: Print Stock Watchlist
    elif args['function_arg'] in definitions.FUNC_DICT['list_watchlist']['values']:
        def cli_watchlist():
            from scrilla.files import get_watchlist
            from scrilla.util.outputter import title_line, print_list
            tickers = get_watchlist()
            title_line("Stock Watchlist")
            print_list(tickers)
        selected_function, required_length = cli_watchlist, 0
    # FUNCTION: Purge Data Directories
    elif args['function_arg'] in definitions.FUNC_DICT["purge"]['values']:
        def cli_purge():
            from scrilla.files import clear_directory
            from scrilla.settings import CACHE_DIR, STATIC_DIR, COMMON_DIR
            logger.comment(
                f'Clearing {STATIC_DIR}, {CACHE_DIR} and {COMMON_DIR}')
            clear_directory(directory=STATIC_DIR, retain=True)
            clear_directory(directory=CACHE_DIR, retain=True)
            clear_directory(directory=COMMON_DIR, retain=True)
        selected_function, required_length = cli_purge, 0

    # FUNCTION: Display Version
    elif args['function_arg'] in definitions.FUNC_DICT["version"]['values']:
        def cli_version():
            from scrilla.settings import APP_DIR
            from os.path import join
            version_file = join(APP_DIR, 'version.txt')
            with open(version_file, 'r') as f:
                print(f.read())
        selected_function, required_length = cli_version, 0

    # FUNCTION: Yield Curve
    elif args['function_arg'] in definitions.FUNC_DICT['yield_curve']['values']:
        def cli_yield_curve():
            from scrilla.static.keys import keys
            from scrilla.services import get_daily_interest_history
            yield_curve = {}
            for maturity in keys['YIELD_CURVE']:
                curve_rate = get_daily_interest_history(maturity=maturity,
                                                        start_date=args['start_date'],
                                                        end_date=args['start_date'])
                yield_curve[maturity] = curve_rate[list(
                    curve_rate.keys())[0]]/100

                if print_format_to_screen(args):
                    from scrilla.util.outputter import scalar_result
                    scalar_result(calculation=maturity,
                                  result=yield_curve[maturity], currency=False)

            if print_json_to_screen(args):
                from json import dumps
                print(dumps(yield_curve))

            if args['save_file'] is not None:
                from scrilla.files import save_file
                save_file(file_to_save=yield_curve,
                          file_name=args['save_file'])
        selected_function, required_length = cli_yield_curve, 0

    # ARGUMENT FUNCTIONS
    # FUNCTION: Asset Grouping

    elif args['function_arg'] in definitions.FUNC_DICT['asset_type']['values']:
        def cli_asset_type():
            from scrilla.files import get_asset_type
            from scrilla.util.outputter import string_result
            for arg in args['tickers']:
                asset_type = get_asset_type(arg)
                string_result(f'asset_type({arg})', asset_type)
        selected_function, required_length = cli_asset_type, 1

    # FUNCTION: Black-Scholes Value At Risk
    elif args['function_arg'] in definitions.FUNC_DICT['var']['values']:
        def cli_var():
            from scrilla.analysis.models.geometric.statistics import calculate_risk_return
            from scrilla.analysis.models.geometric.probability import percentile
            from scrilla.services import get_daily_price_history
            from scrilla.util.helper import get_first_json_key
            from scrilla.static.keys import keys

            all_vars = {}
            for arg in args['tickers']['values']:
                prices = get_daily_price_history(ticker=arg,
                                                 start_date=args['start_date'],
                                                 end_date=args['end_date'])
                latest_price = prices[get_first_json_key(
                    prices)][keys['PRICES']['CLOSE']]
                profile = calculate_risk_return(ticker=arg,
                                                sample_prices=prices,
                                                method=args['estimation_method'])
                valueatrisk = percentile(S0=latest_price,
                                         vol=profile['annual_volatility'],
                                         ret=profile['annual_return'],
                                         expiry=args['expiry'],
                                         prob=args['probability'])

                all_vars[arg] = valueatrisk

                if print_format_to_screen(args):
                    from scrilla.util.outputter import scalar_result
                    scalar_result(f'{arg}_VaR', valueatrisk)

            if print_json_to_screen(args):
                from json import dumps
                print(dumps(all_vars))

            if args['save_file'] is not None:
                from scrilla.files import save_file
                save_file(file_to_save=all_vars, file_name=args['save_file'])

        selected_function, required_length = cli_var, 2

    # FUNCTION: Black-Scholes Conditional Value At Risk
    elif args['function_arg'] in definitions.FUNC_DICT['cvar']['values']:
        def cli_cvar():
            from scrilla.services import get_daily_price_history
            from scrilla.static.keys import keys
            from scrilla.analysis.models.geometric.statistics import calculate_risk_return
            from scrilla.analysis.models.geometric.probability import percentile, conditional_expected_value
            from scrilla.util.helper import get_first_json_key
            all_cvars = {}
            for arg in args['tickers']:
                prices = get_daily_price_history(ticker=arg,
                                                 start_date=args['start_date'],
                                                 end_date=args['end_date'])
                latest_price = prices[get_first_json_key(
                    prices)][keys['PRICES']['CLOSE']]
                profile = calculate_risk_return(ticker=arg,
                                                sample_prices=prices,
                                                method=args['estimation_method'])
                valueatrisk = percentile(S0=latest_price,
                                         vol=profile['annual_volatility'],
                                         ret=profile['annual_return'],
                                         expiry=args['expiry'],
                                         prob=args['probability'])
                cvar = conditional_expected_value(S0=latest_price,
                                                  vol=profile['annual_volatility'],
                                                  ret=profile['annual_return'],
                                                  expiry=args['expiry'],
                                                  conditional_value=valueatrisk)
                all_cvars[arg] = cvar

                if print_format_to_screen(args):
                    from scrilla.util.outputter import scalar_result
                    scalar_result(
                        f'{arg}_conditional_value_at_risk', valueatrisk)

            if print_json_to_screen(args):
                from json import dumps
                print(dumps(all_cvars))

            if args['save_file'] is not None:
                from scrilla.files import save_file
                save_file(file_to_save=all_cvars, file_name=args['save_file'])

        selected_function, required_length = cli_cvar, 2

    # FUNCTION: Capital Asset Pricing Model Cost of Equity
    elif args['function_arg'] in definitions.FUNC_DICT['capm_equity_cost']['values']:
        def cli_capm_equity_cost():
            from scrilla.analysis.markets import cost_of_equity
            all_costs = {}
            for arg in args['tickers']:
                equity_cost = cost_of_equity(ticker=arg,
                                             start_date=args['start_date'],
                                             end_date=args['end_date'],
                                             method=args['estimation_method'])
                all_costs[arg] = equity_cost

                if print_format_to_screen(args):
                    from scrilla.util.outputter import scalar_result
                    scalar_result(f'{arg}_equity_cost',
                                  equity_cost, currency=False)

            if print_json_to_screen(args):
                from json import dumps
                print(dumps(all_costs))

            if args['save_file'] is not None:
                from scrilla.files import save_file
                save_file(file_to_save=all_costs, file_name=args['save_file'])

        selected_function, required_length = cli_capm_equity_cost, 1

    # FUNCTION: Capital Asset Pricing Model Beta
    elif args['function_arg'] in definitions.FUNC_DICT['capm_beta']['values']:
        def cli_capm_beta():
            from scrilla.analysis.markets import market_beta
            all_betas = {}
            for arg in args['tickers']:
                beta = market_beta(ticker=arg,
                                   start_date=args['start_date'],
                                   end_date=args['end_date'],
                                   method=args['estimation_method'])
                all_betas[arg] = beta

                if print_format_to_screen(args):
                    from scrilla.util.outputter import scalar_result
                    scalar_result(f'{arg}_beta', beta, currency=False)

            if print_json_to_screen(args):
                from json import dumps
                print(dumps(all_betas))

            if args['save_file'] is not None:
                from scrilla.files import save_file
                save_file(file_to_save=all_betas, file_name=args['save_file'])
        selected_function, required_length = cli_capm_beta, 1

    # FUNCTION: Last Close Price
    elif args['function_arg'] in definitions.FUNC_DICT["close"]['values']:
        def cli_close():
            from scrilla.services import get_daily_price_latest

            all_prices = {}
            for arg in args['tickers']:
                price = get_daily_price_latest(arg)
                all_prices[arg] = price

                if print_format_to_screen(args):
                    from scrilla.util.outputter import scalar_result
                    scalar_result(
                        calculation=f'Last {arg} close price', result=float(price))

            if print_json_to_screen(args):
                from json import dumps
                print(dumps(all_prices))

            if args['save_file'] is not None:
                from scrilla.files import save_file
                save_file(file_to_save=all_prices, file_name=args['save_file'])
        selected_function, required_length = cli_close, 1

    # FUNCTION: Correlation Matrix
    elif args['function_arg'] in definitions.FUNC_DICT["correlation"]['values']:
        def cli_correlation():
            from scrilla.static.keys import keys
            from scrilla.analysis.models.geometric.statistics import correlation_matrix

            if args['estimation_method'] == keys['ESTIMATION']['LIKE']:
                logger.comment('This calculation takes a while, strap in...')

            matrix = correlation_matrix(tickers=args['tickers'],
                                        start_date=args['start_date'],
                                        end_date=args['end_date'],
                                        method=args['estimation_method'])

            if print_format_to_screen(args):
                from scrilla.util.outputter import correlation_matrix as correlation_output
                correlation_output(
                    tickers=args['tickers'], correl_matrix=matrix)

            elif print_json_to_screen(args):
                from json import dumps
                print(dumps(matrix))

            if args['save_file'] is not None:
                from scrilla.files import save_file
                save_file(file_to_save=matrix, file_name=args['save_file'])

        selected_function, required_length = cli_correlation, 2

    # FUNCTION: Correlation Time Series
    elif args['function_arg'] in definitions.FUNC_DICT['correlation_time_series']['values']:
        def cli_correlation_series():
            from scrilla.analysis.models.geometric.statistics import calculate_moment_correlation_series
            if print_format_to_screen(args):
                from scrilla.util.outputter import scalar_result

            logger.comment('This calculation takes a while, strap in...')
            ticker_1, ticker_2 = args['tickers'][0], args['tickers'][1]
            result = calculate_moment_correlation_series(ticker_1=ticker_1,
                                                         ticker_2=ticker_2,
                                                         start_date=args['start_date'],
                                                         end_date=args['end_date'])
            if print_format_to_screen(args):
                for this_date in result:
                    scalar_result(calculation=f'{this_date}_{ticker_1}_{ticker_2}_correlation',
                                  result=float(result[this_date]), currency=False)
            elif print_json_to_screen(args):
                from json import dumps
                print(dumps(result))

            if args['save_file'] is not None:
                from scrilla.files import save_file
                save_file(file_to_save=result, file_name=args['save_file'])
        selected_function, required_length, exact = cli_correlation_series, 2, True

    # FUNCTION: Discount Dividend Model
    elif args['function_arg'] in definitions.FUNC_DICT["discount_dividend"]['values']:
        def cli_discount_dividend():
            from scrilla.services import get_dividend_history
            from scrilla.analysis.objects.cashflow import Cashflow
            model_results = {}

            for arg in args['tickers']:
                dividends = get_dividend_history(arg)
                if args['discount'] is None:
                    from scrilla.analysis.markets import cost_of_equity
                    discount = cost_of_equity(
                        ticker=arg, method=args['estimation_method'])
                else:
                    discount = args['discount']
                model_results[f'{arg}_discount_dividend'] = Cashflow(sample=dividends,
                                                                     discount_rate=discount).calculate_net_present_value()
                if print_format_to_screen(args):
                    from scrilla.util.outputter import scalar_result
                    scalar_result(f'Net Present Value ({arg} dividends)',
                                  model_results[f'{arg}_discount_dividend'])

            if print_json_to_screen(args):
                from json import dumps
                print(dumps(model_results))

            if args['save_file'] is not None:
                from scrilla.files import save_file
                save_file(file_to_save=model_results,
                          file_name=args['save_file'])
        selected_function, required_length = cli_discount_dividend, 1

    elif args['function_arg'] in definitions.FUNC_DICT['dividends']['values']:
        def cli_dividends():
            from scrilla.services import get_dividend_history
            if print_format_to_screen(args):
                from scrilla.util.outputter import scalar_result

            all_dividends = {}
            for arg in args['tickers']:
                dividends = get_dividend_history(arg)
                all_dividends[arg] = dividends

                if print_format_to_screen(args):
                    for this_date in dividends:
                        scalar_result(
                            calculation=f'{arg}_dividend({this_date})', result=dividends[this_date])

            if print_json_to_screen(args):
                from json import dumps
                print(dumps(all_dividends))

        selected_function, required_length = cli_dividends, 1

    # FUNCTION: Efficient Frontier
    elif args['function_arg'] in definitions.FUNC_DICT['efficient_frontier']['values']:
        def cli_efficient_frontier():
            from scrilla.analysis.objects.portfolio import Portfolio
            from scrilla.analysis.optimizer import calculate_efficient_frontier

            portfolio = Portfolio(tickers=args['tickers'],
                                  start_date=args['start_date'],
                                  end_date=args['end_date'],
                                  method=args['estimation_method'])
            frontier = calculate_efficient_frontier(portfolio=portfolio,
                                                    steps=args['steps'])

            if args['investment'] is not None:
                from scrilla.services import get_daily_prices_latest
                prices = get_daily_prices_latest(
                    tickers=args['tickers'])
            else:
                prices = None

            if print_format_to_screen(args):
                from scrilla.util.outputter import efficient_frontier as frontier_output
                frontier_output(portfolio=portfolio,
                                frontier=frontier,
                                investment=args['investment'],
                                latest_prices=prices)
            if print_json_to_screen(args):
                from json import dumps
                from scrilla.static.formats import format_frontier
                print(dumps(format_frontier(portfolio=portfolio,
                                            frontier=frontier,
                                            investment=args['investment'],
                                            latest_prices=prices)))

            if args['save_file'] is not None:
                from scrilla.files import save_frontier
                save_frontier(portfolio=portfolio,
                              frontier=frontier,
                              investment=args['investment'],
                              file_name=args['save_file'],
                              latest_prices=prices)
        selected_function, required_length = cli_efficient_frontier, 2

    # FUNCTION: Maximize Portfolio Return
    elif args['function_arg'] in definitions.FUNC_DICT['maximize_return']['values']:
        def cli_maximize_return():
            from scrilla.analysis.objects.portfolio import Portfolio
            from scrilla.analysis.optimizer import maximize_portfolio_return

            portfolio = Portfolio(tickers=args['tickers'],
                                  start_date=args['start_date'],
                                  end_date=args['end_date'],
                                  method=args['estimation_method'])

            allocation = maximize_portfolio_return(
                portfolio=portfolio)

            if args['investment'] is not None:
                from scrilla.services import get_daily_prices_latest
                prices = get_daily_prices_latest(
                    tickers=args['tickers'])
            else:
                prices = None

            if print_format_to_screen(args):
                from scrilla.util.outputter import optimal_result
                optimal_result(portfolio=portfolio,
                               allocation=allocation,
                               investment=args['investment'],
                               latest_prices=prices)

            if print_json_to_screen(args):
                from json import dumps
                from scrilla.static.formats import format_allocation
                print(dumps(format_allocation(allocation=allocation,
                                              portfolio=portfolio,
                                              investment=args['investment'],
                                              latest_prices=prices)))

            if args['save_file'] is not None:
                from scrilla.files import save_allocation
                save_allocation(allocation=allocation,
                                portfolio=portfolio,
                                file_name=args['save_file'],
                                investment=args['investment'],
                                latest_prices=prices)
        selected_function, required_length = cli_maximize_return, 2

    # FUNCTION: Moving Averages of Logarithmic Returns
    elif args['function_arg'] in definitions.FUNC_DICT['moving_averages']['values']:
        def cli_moving_averages():
            from scrilla.analysis.models.geometric.statistics import calculate_moving_averages
            # TODO: moving averages with estimation techniques

            moving_averages = calculate_moving_averages(ticker=args['tickers'][0],
                                                        start_date=args['start_date'],
                                                        end_date=args['end_date'],
                                                        method=args['estimation_method'])

            if print_format_to_screen(args):
                from scrilla.util.outputter import moving_average_result
                moving_average_result(
                    ticker=args['tickers'][0], averages=moving_averages)

            if print_json_to_screen(args):
                from json import dumps
                print(dumps(moving_averages))

            if args['save_file'] is not None:
                from scrilla.files import save_file
                save_file(file_to_save=moving_averages,
                          file_name=args['save_file'])

        selected_function, required_length = cli_moving_averages, 1

    # FUNCTION: Optimize Portfolio Variance/Volatility
    elif args['function_arg'] in definitions.FUNC_DICT['optimize_portfolio']['values']:
        def cli_optimize_portfolio_variance():
            from scrilla.analysis.objects.portfolio import Portfolio

            portfolio = Portfolio(tickers=args['tickers'],
                                  start_date=args['start_date'],
                                  end_date=args['end_date'],
                                  method=args['estimation_method'])

            if args['optimize_sharpe']:
                from scrilla.analysis.optimizer import maximize_sharpe_ratio
                allocation = maximize_sharpe_ratio(
                    portfolio=portfolio, target_return=args['target'])
            else:
                from scrilla.analysis.optimizer import optimize_portfolio_variance
                allocation = optimize_portfolio_variance(
                    portfolio=portfolio, target_return=args['target'])

            if args['investment'] is not None:
                from scrilla.services import get_daily_prices_latest
                prices = get_daily_prices_latest(
                    tickers=args['tickers'])
            else:
                prices = None

            if print_format_to_screen(args):
                from scrilla.util.outputter import optimal_result
                optimal_result(
                    portfolio=portfolio, allocation=allocation, investment=args['investment'])

            if print_json_to_screen(args):
                from scrilla.static.formats import format_allocation
                from json import dumps
                print(dumps(format_allocation(allocation=allocation,
                                              portfolio=portfolio,
                                              investment=args['investment'],
                                              latest_prices=prices)))

            if args['save_file'] is not None:
                from scrilla.files import save_allocation
                save_allocation(allocation=allocation,
                                portfolio=portfolio,
                                file_name=args['save_file'],
                                investment=args['investment'],
                                latest_prices=prices)

        selected_function, required_length = cli_optimize_portfolio_variance, 2

    # FUNCTION: Optimize Portfolio Conditional Value At Risk
    elif args['function_arg'] in definitions.FUNC_DICT['optimize_portfolio_conditional_var']['values']:
        def cli_optimize_conditional_value_at_risk():
            from scrilla.analysis.optimizer import optimize_conditional_value_at_risk
            from scrilla.analysis.objects.portfolio import Portfolio

            portfolio = Portfolio(tickers=args['tickers'],
                                  start_date=args['start_date'],
                                  end_date=args['end_date'],
                                  method=args['estimation_method'])
            allocation = optimize_conditional_value_at_risk(portfolio=portfolio,
                                                            prob=args['probability'],
                                                            expiry=args['expiry'],
                                                            target_return=args['target'])
            if args['investment'] is not None:
                from scrilla.services import get_daily_prices_latest
                prices = get_daily_prices_latest(
                    tickers=args['tickers'])
            else:
                prices = None

            if print_format_to_screen(args):
                from scrilla.util.outputter import optimal_result
                optimal_result(portfolio=portfolio,
                               allocation=allocation,
                               investment=args['investment'],
                               latest_prices=prices)

            if print_json_to_screen(args):
                from scrilla.static.formats import format_allocation
                from json import dumps
                print(dumps(format_allocation(allocation=allocation,
                                              portfolio=portfolio,
                                              investment=args['investment'],
                                              latest_prices=prices)))

            if args['save_file'] is not None:
                from scrilla.files import save_allocation
                save_allocation(allocation=allocation,
                                portfolio=portfolio,
                                file_name=args['save_file'],
                                investment=args['investment'],
                                latest_prices=prices)
        selected_function, required_length = cli_optimize_conditional_value_at_risk, 2

    # FUNCTION: Plot Correlation Time Series
    elif args['function_arg'] in definitions.FUNC_DICT['plot_correlation']['values']:
        def cli_plot_correlation():
            from scrilla.analysis.models.geometric.statistics import calculate_moment_correlation_series
            from scrilla.analysis.plotter import plot_correlation_series

            logger.comment('This calculation takes a while, strap in...')

            correlation_history = calculate_moment_correlation_series(ticker_1=args['tickers'][0],
                                                                      ticker_2=args['tickers'][1],
                                                                      start_date=args['start_date'],
                                                                      end_date=args['end_date'])
            plot_correlation_series(tickers=args['tickers'],
                                    series=correlation_history,
                                    savefile=args['save_file'])

        selected_function, required_length, exact = cli_plot_correlation, 2, True

    # FUNCTION: Plot Dividend History With Linear Regression Model
    elif args['function_arg'] in definitions.FUNC_DICT['plot_dividends']['values']:
        def cli_plot_dividends():
            from scrilla.services import get_dividend_history
            from scrilla.analysis.objects.cashflow import Cashflow
            from scrilla.analysis.plotter import plot_cashflow

            dividends = get_dividend_history(ticker=args['tickers'][0])
            if args['discount'] is None:
                from scrilla.analysis.markets import cost_of_equity
                args['discount'] = cost_of_equity(ticker=args['tickers'][0],
                                                  method=args['estimation_method'])
            div_cashflow = Cashflow(sample=dividends,
                                    discount_rate=args['discount'])
            plot_cashflow(ticker=args['tickers'][0],
                          cashflow=div_cashflow, show=True,
                          savefile=args['save_file'])

        selected_function, required_length, exact = cli_plot_dividends, 1, True

    # FUNCTION: Plot Efficient Frontier
    elif args['function_arg'] in definitions.FUNC_DICT['plot_frontier']['values']:
        def cli_plot_frontier():
            from scrilla.analysis.objects.portfolio import Portfolio
            from scrilla.analysis.optimizer import calculate_efficient_frontier
            from scrilla.analysis.plotter import plot_frontier

            portfolio = Portfolio(tickers=args['tickers'],
                                  start_date=args['start_date'],
                                  end_date=args['end_date'],
                                  method=args['estimation_method'])

            frontier = calculate_efficient_frontier(portfolio=portfolio,
                                                    steps=args['steps'])

            plot_frontier(portfolio=portfolio,
                          frontier=frontier,
                          show=True,
                          savefile=args['save_file'])

        selected_function, required_length = cli_plot_frontier, 2

    # FUNCTION: Plot Moving Averages of Logarithmic Returns
    elif args['function_arg'] in definitions.FUNC_DICT['plot_moving_averages']['values']:
        def cli_plot_moving_averages():
            from scrilla.analysis.models.geometric.statistics import calculate_moving_averages
            from scrilla.analysis.plotter import plot_moving_averages
            # TODO: estimation techniques with moving averages
            moving_averages = calculate_moving_averages(ticker=args['tickers'][0],
                                                        start_date=args['start_date'],
                                                        end_date=args['end_date'],
                                                        method=args['estimation_method'])

            plot_moving_averages(ticker=args['tickers'][0],
                                 averages=moving_averages,
                                 show=True, savefile=args['save_file'])

        selected_function, required_length, exact = cli_plot_moving_averages, 1, True

    # FUNCTION: Plot Return QQ Series
    elif args['function_arg'] in definitions.FUNC_DICT['plot_return_qq']['values']:
        def cli_plot_qq_returns():
            from scrilla.analysis.models.geometric.statistics import get_sample_of_returns
            from scrilla.analysis.estimators import qq_series_for_sample
            from scrilla.analysis.plotter import plot_qq_series

            returns = get_sample_of_returns(ticker=args['tickers'][0],
                                            start_date=args['start_date'],
                                            end_date=args['end_date'],
                                            daily=True)

            qq_series = qq_series_for_sample(sample=returns)

            plot_qq_series(ticker=args['tickers'][0],
                           qq_series=qq_series,
                           show=True,
                           savefile=args['save_file'])

        selected_function, required_length, exact = cli_plot_qq_returns, 1, True

    # FUNCTION: Plot Histogram of Returns
    elif args['function_arg'] in definitions.FUNC_DICT['plot_return_dist']['values']:
        def cli_plot_dist_returns():
            from scrilla.analysis.models.geometric.statistics import get_sample_of_returns
            from scrilla.analysis.plotter import plot_return_histogram

            returns = get_sample_of_returns(ticker=args['tickers'][0],
                                            start_date=args['start_date'],
                                            end_date=args['end_date'],
                                            daily=True)
            plot_return_histogram(ticker=args['tickers'][0],
                                  sample=returns,
                                  show=True,
                                  savefile=args['save_file'])
        selected_function, required_length, exact = cli_plot_dist_returns, 1, True

    # FUNCTION: Plot Risk-Return Profile
    elif args['function_arg'] in definitions.FUNC_DICT['plot_risk_profile']['values']:
        def cli_plot_risk_profile():
            from scrilla.analysis.models.geometric.statistics import calculate_risk_return
            from scrilla.analysis.plotter import plot_profiles
            from scrilla.util.dater import format_date_range
            profiles = {}
            for arg in args['tickers']:
                profiles[arg] = calculate_risk_return(ticker=arg,
                                                      start_date=args['start_date'],
                                                      end_date=args['end_date'],
                                                      method=args['estimation_method'])

            plot_profiles(symbols=args['tickers'],
                          show=True,
                          profiles=profiles,
                          savefile=args['save_file'],
                          subtitle=format_date_range(start_date=args['start_date'],
                                                     end_date=args['end_date']))
        selected_function, required_length = cli_plot_risk_profile, 1

    elif args['function_arg'] in definitions.FUNC_DICT['plot_yield_curve']['values']:
        def cli_plot_yield_curve():
            from scrilla.util.dater import get_next_business_date, to_string
            from scrilla.static.keys import keys
            from scrilla.services import get_daily_interest_history
            from scrilla.analysis.plotter import plot_yield_curve
            yield_curve = {}
            args['start_date'] = get_next_business_date(args['start_date'])
            start_date_string = to_string(args['start_date'])
            yield_curve[start_date_string] = []
            for maturity in keys['YIELD_CURVE']:
                rate = get_daily_interest_history(maturity=maturity,
                                                  start_date=args['start_date'],
                                                  end_date=args['start_date'])
                yield_curve[start_date_string].append(rate[start_date_string])

            plot_yield_curve(yield_curve=yield_curve,
                             show=True,
                             savefile=args['save_file'])
        selected_function, required_length, exact = cli_plot_yield_curve, 0, True
    # FUNCTION: Price History
    elif args['function_arg'] in definitions.FUNC_DICT['price_history']['values']:
        def cli_price_history():
            from scrilla.services import get_daily_price_history
            from scrilla.static.keys import keys
            if print_format_to_screen(args):
                from scrilla.util.outputter import scalar_result

            all_prices = {}
            for arg in args['tickers']:
                prices = get_daily_price_history(ticker=arg,
                                                 start_date=args['start_date'],
                                                 end_date=args['end_date'])
                all_prices[arg] = {}
                for this_date in prices:
                    price = prices[this_date][keys['PRICES']['CLOSE']]
                    all_prices[arg][this_date] = price

                    if print_format_to_screen(args):
                        scalar_result(
                            calculation=f'{arg}({this_date})', result=float(price))

            if print_json_to_screen(args):
                from json import dumps
                print(dumps(all_prices))

            if args['save_file'] is not None:
                from scrilla.files import save_file
                save_file(file_to_save=all_prices, file_name=args['save_file'])
        selected_function, required_length = cli_price_history, 1

    # FUNCTION: Interest Rate History
    elif args['function_arg'] in definitions.FUNC_DICT['interest_history']['values']:
        def cli_interest_history():
            from scrilla.services import get_daily_interest_history
            if print_format_to_screen(args):
                from scrilla.util.outputter import scalar_result

            all_rates = {}
            for arg in args['tickers']:
                all_rates[arg] = get_daily_interest_history(maturity=arg,
                                                            start_date=args['start_date'],
                                                            end_date=args['end_date'])
                for this_date in all_rates[arg]:
                    all_rates[arg][this_date] = all_rates[arg][this_date]

                if print_format_to_screen(args):
                    for this_date in all_rates[arg]:
                        scalar_result(calculation=f'{arg}_YIELD({this_date})', result=float(
                            all_rates[arg][this_date])/100, currency=False)

            if print_json_to_screen(args):
                from json import dumps
                print(dumps(all_rates))

            if args['save_file'] is not None:
                from scrilla.files import save_file
                save_file(file_to_save=all_rates,
                          file_name=args['save_file'])
        selected_function, required_length = cli_interest_history, 1

    # FUNCTION: Risk Free Rate
    elif args['function_arg'] in definitions.FUNC_DICT['risk_free_rate']['values']:
        def cli_risk_free_rate():
            from scrilla.services import get_risk_free_rate
            from scrilla.settings import RISK_FREE_RATE
            rate = {}
            rate[RISK_FREE_RATE] = get_risk_free_rate()

            if print_format_to_screen(args):
                from scrilla.util.outputter import title_line, scalar_result
                from scrilla.static.formats import formats
                title_line("Risk Free Rate")
                scalar_result(calculation=formats['RISK_FREE_TITLE'].format(RISK_FREE_RATE),
                              result=rate[RISK_FREE_RATE], currency=False)
            if print_json_to_screen(args):
                from json import dumps
                print(dumps(rate))

            if args['save_file'] is not None:
                from scrilla.files import save_file
                save_file(file_to_save=rate, file_name=args['save_file'])
        selected_function, required_length, exact = cli_risk_free_rate, 0, True

    # FUNCTION: Risk-Return Profile
    elif args['function_arg'] in definitions.FUNC_DICT["risk_profile"]['values']:
        def cli_risk_return():
            from scrilla.analysis.models.geometric.statistics import calculate_risk_return
            from scrilla.analysis.markets import sharpe_ratio, market_beta, cost_of_equity
            profiles = {}
            for arg in args['tickers']:
                profiles[arg] = calculate_risk_return(ticker=arg,
                                                      method=args['estimation_method'],
                                                      start_date=args['start_date'],
                                                      end_date=args['end_date'])
                profiles[arg]['sharpe_ratio'] = sharpe_ratio(ticker=arg,
                                                             start_date=args['start_date'],
                                                             end_date=args['end_date'],
                                                             ticker_profile=profiles[arg],
                                                             method=args['estimation_method'])
                profiles[arg]['asset_beta'] = market_beta(ticker=arg,
                                                          start_date=args['start_date'],
                                                          end_date=args['end_date'],
                                                          ticker_profile=profiles[arg],
                                                          method=args['estimation_method'])
                profiles[arg]['equity_cost'] = cost_of_equity(ticker=arg,
                                                              start_date=args['start_date'],
                                                              end_date=args['end_date'],
                                                              method=args['estimation_method'])

            if print_format_to_screen(args):
                from scrilla.util.outputter import risk_profile
                risk_profile(profiles=profiles)

            if print_json_to_screen(args):
                from json import dumps
                print(dumps(profiles))

            if args['save_file'] is not None:
                from scrilla.files import save_file
                save_file(file_to_save=profiles, file_name=args['save_file'])

        selected_function, required_length = cli_risk_return, 1

    # FUNCTION: Model Discount Screener
    elif args['function_arg'] in definitions.FUNC_DICT["screener"]['values']:
        def cli_screener():
            from scrilla.analysis.markets import screen_for_discount
            from scrilla.static.keys import keys
            from scrilla.util.outputter import screen_results
            if args['model'] is None:
                model = keys['MODELS']['DDM']
            results = screen_for_discount(
                model=model, discount_rate=args['discount'])
            screen_results(info=results, model=model)
        selected_function, required_length = cli_screener, 0

    # FUNCTION: Sharpe Ratio
    elif args['function_arg'] in definitions.FUNC_DICT["sharpe_ratio"]['values']:
        def cli_sharpe_ratio():
            from scrilla.analysis.markets import sharpe_ratio
            all_results = {}
            for arg in args['tickers']:
                result = sharpe_ratio(ticker=arg,
                                      start_date=args['start_date'],
                                      end_date=args['end_date'],
                                      method=args['estimation_method'])
                all_results[arg] = result

                if print_format_to_screen(args):
                    from scrilla.util.outputter import scalar_result
                    scalar_result(calculation=f'{arg}_sharpe_ratio', result=result,
                                  currency=False)

            if print_json_to_screen(args):
                from json import dumps
                print(dumps(all_results))

            if args['save_file'] is not None:
                from scrilla.files import save_file
                save_file(file_to_save=all_results,
                          file_name=args['save_file'])
        selected_function, required_length = cli_sharpe_ratio, 1

   # FUNCTION: Store Key
    elif args['function_arg'] in definitions.FUNC_DICT['store']['values']:
        def cli_store():
            from scrilla.files import set_credentials
            set_credentials(value=args['value'], which_key=args['key'])
        selected_function, required_length = cli_store, 0

    # FUNCTION: Get Latest Economic Statistic
    elif args['function_arg'] in definitions.FUNC_DICT["statistic"]['values']:
        def cli_statistic():
            from scrilla.services import get_daily_fred_latest
            all_stats = {}
            for stat in args['tickers']:
                result = get_daily_fred_latest(symbol=stat)
                all_stats[stat] = result

                if print_format_to_screen(args):
                    from scrilla.util.outputter import scalar_result
                    scalar_result(calculation=stat,
                                  result=result, currency=False)

            if print_json_to_screen(args):
                from json import dumps
                print(dumps(all_stats))

            if args['save_file'] is not None:
                from scrilla.files import save_file
                save_file(file_to_save=all_stats, file_name=args['save_file'])

        selected_function, required_length = cli_statistic, 1

    # FUNCTION: Statistic History
    elif args['function_arg'] in definitions.FUNC_DICT['statistic_history']['values']:
        def cli_statistic_history():
            from scrilla.services import get_daily_fred_history
            if print_format_to_screen(args):
                from scrilla.util.outputter import scalar_result

            all_stats = {}
            for arg in args['tickers']:
                stats = get_daily_fred_history(symbol=arg,
                                               start_date=args['start_date'],
                                               end_date=args['end_date'])
                all_stats[arg] = stats
                if print_format_to_screen(args):
                    for this_date in stats:
                        scalar_result(calculation=f'{arg}({this_date})',
                                      result=stats[this_date],
                                      currency=False)

            if print_json_to_screen(args):
                from json import dumps
                print(dumps(all_stats))

            if args['save_file'] is not None:
                from scrilla.files import save_file
                save_file(file_to_save=all_stats, file_name=args['save_file'])
        selected_function, required_length = cli_statistic_history, 1

    # FUNCTION: Set Watchlist
    elif args['function_arg'] in definitions.FUNC_DICT["watchlist"]['values']:
        def cli_watchlist():
            from scrilla.files import add_watchlist
            add_watchlist(new_tickers=args['tickers'])
            logger.comment(
                "Watchlist saved. Use -ls option to print watchlist.")
        selected_function, required_length = cli_watchlist, 1

    else:
        def cli_help():
            from scrilla.util.outputter import help_msg
            help_msg()
        selected_function, required_length = cli_help, 0

    # END CLI FUNCTION DEFINITIONS

    if selected_function is not None:
        validate_function_usage(selection=args['function_arg'],
                                args=args['tickers'],
                                wrapper_function=selected_function,
                                required_length=required_length,
                                exact=exact)


def scrilla():
    import sys

    do_program(sys.argv[1:])


if __name__ == "__main__":
    import sys

    do_program(sys.argv[1:])
