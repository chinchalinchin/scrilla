import argparse

from scrilla.static import constants, definitions
from scrilla.util.helper import significant_digits, exceeds_accuracy

formats = {
    'separator': '-',
    'TAB': '     ',
    'LINE_LENGTH': 100,
    'BAR_WIDTH': 0.10,
    'INDENT': 10,
    'RISK_FREE_TITLE': "{} US Treasury",
    'BINS': 20
}


def format_float_number(decimal: float) -> str:
    if exceeds_accuracy(decimal):
        return '0'
    accuracy = f'.{constants.constants["ACCURACY"]}f'
    sigfigs = format(significant_digits(
        decimal, constants.constants["SIG_FIGS"]), accuracy)
    return sigfigs.rstrip('0').rstrip('.')


def format_float_percent(decimal: float) -> str:
    if exceeds_accuracy(decimal):
        return "0%"
    accuracy = f'.{constants.constants["ACCURACY"]}f'
    sigfigs = format(100*significant_digits(decimal,
                     constants.constants['SIG_FIGS']), accuracy)
    return sigfigs.rstrip('0').rstrip('.') + '%'


def format_dict_percent(this_dict: dict, which_key: str) -> dict:
    buffer_dict = this_dict.copy()
    buffer_dict[which_key] = format_float_percent(this_dict[which_key])
    return buffer_dict


def format_dict_number(this_dict: dict, which_key: str) -> dict:
    buffer_dict = this_dict.copy()
    buffer_dict[which_key] = format_float_number(this_dict[which_key])
    return buffer_dict


def format_allocation(allocation, portfolio, investment=None, latest_prices=None):
    allocation_format = []

    if investment is not None:
        shares = portfolio.calculate_approximate_shares(
            x=allocation, total=investment, latest_prices=latest_prices)
        total = portfolio.calculate_actual_total(
            x=allocation, total=investment, latest_prices=latest_prices)

    annual_volatility = portfolio.volatility_function(x=allocation)
    annual_return = portfolio.return_function(x=allocation)

    for j, item in enumerate(portfolio.tickers):
        holding = {'ticker': item, 'allocation': round(allocation[j], constants['ACCURACY']), 'annual_return': round(
            portfolio.mean_return[j], constants['ACCURACY']), 'annual_volatility': round(
            portfolio.sample_vol[j], constants['ACCURACY'])}
        if investment is not None:
            holding['shares'] = float(shares[j])
        allocation_format.append(holding)

    json_format = {'holdings': allocation_format,
                   'portfolio_return': annual_return, 'portfolio_volatility': annual_volatility}

    if investment is not None:
        json_format['total'] = float(total)

    return json_format


def format_frontier(portfolio, frontier, investment=None, latest_prices=None):
    json_format = []
    for item in frontier:
        json_format.append(format_allocation(allocation=item, portfolio=portfolio,
                                             investment=investment, latest_prices=latest_prices))
    return json_format


def format_correlation_matrix(tickers, correlation_matrix):
    response = []
    for i in range(0, len(tickers)-1):
        subresponse = {}
        for j in range(i+1, len(tickers)):
            subresponse[f'{tickers[i]}_{tickers[j]}_correlation'] = correlation_matrix[j][i]
        response.append(subresponse)
    return response


def format_args(args, default_estimation_method) -> argparse.Namespace:
    parser = argparse.ArgumentParser()

    choices = []
    for func in definitions.FUNC_DICT:
        choices.append(definitions.FUNC_DICT[func]['values'][0])
        choices.append(definitions.FUNC_DICT[func]['values'][1])

    parser.add_argument('function_arg', choices=choices)

    groups = [parser.add_mutually_exclusive_group()
              for _ in definitions.ARG_META_DICT['groups']]

    for arg in definitions.ARG_DICT:
        if definitions.ARG_DICT[arg]['format'] not in ('group', bool):
            parser.add_argument(definitions.ARG_DICT[arg]['values'][0],
                                definitions.ARG_DICT[arg]['values'][1],
                                definitions.ARG_DICT[arg]['values'][2],
                                definitions.ARG_DICT[arg]['values'][3],
                                default=None,
                                type=definitions.ARG_DICT[arg]['format'],
                                dest=arg)
        elif definitions.ARG_DICT[arg]['format'] == 'group':
            group_index = definitions.ARG_META_DICT['groups'].index(
                definitions.ARG_DICT[arg]['group'])
            groups[group_index].add_argument(definitions.ARG_DICT[arg]['values'][0],
                                             definitions.ARG_DICT[arg]['values'][1],
                                             definitions.ARG_DICT[arg]['values'][2],
                                             definitions.ARG_DICT[arg]['values'][3],
                                             action='store_const',
                                             dest=definitions.ARG_DICT[arg]['group'],
                                             const=arg)
        # NOTE: 'format' == group AND 'format' == bool => Empty Set, so only other alternative is
        # 'format' == bool
        else:
            parser.add_argument(definitions.ARG_DICT[arg]['values'][0],
                                definitions.ARG_DICT[arg]['values'][1],
                                definitions.ARG_DICT[arg]['values'][2],
                                definitions.ARG_DICT[arg]['values'][3],
                                action='store_true',
                                dest=arg)

    parser.set_defaults(estimation_method=default_estimation_method)
    parser.add_argument('tickers', nargs='*', type=str)
    return vars(parser.parse_args(args))
