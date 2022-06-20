from scrilla.static import constants
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
        holding = {}
        holding['ticker'] = item
        holding['allocation'] = round(allocation[j], constants['ACCURACY'])
        if investment is not None:
            holding['shares'] = float(shares[j])
        holding['annual_return'] = round(
            portfolio.mean_return[j], constants['ACCURACY'])
        holding['annual_volatility'] = round(
            portfolio.sample_vol[j], constants['ACCURACY'])
        allocation_format.append(holding)

    json_format = {}
    json_format['holdings'] = allocation_format

    if investment is not None:
        json_format['total'] = float(total)

    json_format['portfolio_return'] = annual_return
    json_format['portfolio_volatility'] = annual_volatility

    return json_format


def format_frontier(portfolio, frontier, investment=None, latest_prices=None):
    json_format = []
    for item in frontier:
        json_format.append(format_allocation(allocation=item, portfolio=portfolio,
                                             investment=investment, latest_prices=latest_prices))
    return json_format


def format_correlation_matrix(tickers, correlation_matrix):
    response = []
    for i, item in enumerate(tickers):
        # correlation_matrix[i][i]
        for j in range(i+1, len(tickers)):
            subresponse = {}
            subresponse[f'{item}_{tickers[j]}_correlation'] = correlation_matrix[j][i]
            response.append(subresponse)
    return response
