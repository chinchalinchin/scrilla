import datetime
from typing import Dict, List, Tuple, Union

from scrilla.static import constants, formats, definitions


# GENERAL OUTPUT FUNCTIONS
def space(n: int):
    print('\n'*n)


def title_line(title: str, line_length: int = formats.formats['LINE_LENGTH'], separator: str = formats.formats['separator'],
               display: bool = True):
    buff = int((line_length - len(title))/2)
    result = separator*buff + title + separator*buff
    if display:
        print(result)
    return result


def separator_line(line_length=formats.formats['LINE_LENGTH'], separator=formats.formats['separator'], display=True) -> str:
    if display:
        print(separator*line_length)
    return separator*line_length


def break_lines(msg: str, line_length: int = formats.formats['LINE_LENGTH']) -> List[str]:
    """
    Generates a list of strings where each string is less than or equal to a specified line length. All elements in the array will be equal length except the last element; in other words, the inputted string will be read into an array, line by line, until there is nothing left to be read.

    Parameters
    ----------
    1. ``msg``: ``str``
        String to be broken into an array with each string no longer than `line_length`.
    2. **line_length**: ``int``
        *Optional*. Defaults to the value set by `static.formats.formats['LINE_LENGTH]`. The maximum length of a line. 

    Returns
    -------
    `list[str]`
        A list of `line`'s with `len(line)<line_length or len(line)==line_length`.
    """

    if len(msg) > line_length:
        return [msg[i:i+line_length] for i in range(0, len(msg), line_length)]
    return [msg]


def center(this_line: str, line_length: int = formats.formats['LINE_LENGTH'], display: bool = True) -> str:
    """
    Centers an inputted line relative to the line length. 

    Parameters
    ----------
    1. **this_line**: ``str``
        the string to centered.
    2. **line_length**: ``int``
        *Optional*. Defaults to the value set by `static.formats.formats['LINE_LENGTH]`. The length of the line that is being centered over. 
    3. **display**: ``bool``
        *Optional*. Defaults to `True`. If set to `True`, function will print result to screen. If set to `False`, the function will return the value as a string.

    Returns
    -------
    `str`
        The line with the difference between `line_length` and `this_line` distributed evenly on either side of the content as white space. 

    Raises
    ------
    1. **ValueError**
        If the inputted line is larged than the line length, this error will be thrown.
    """

    if len(this_line) > line_length:
        raise ValueError(
            'Line to be centered is larger than length being centered over.')

    buff = int((line_length - len(this_line))/2)
    output = ' '*buff + this_line + ' '*buff
    if display:
        print(output)
        return
    return output


def print_list(list_to_print, indent=formats.formats['INDENT']):
    for i, item in enumerate(list_to_print):
        print(' '*indent, f'{i}. {item}')


def string_result(operation, result, indent=formats.formats['INDENT'], display=True):
    output = ' '*indent + operation + ' = ' + result
    if display:
        print(output)
        return
    return output


def scalar_result(calculation, result, currency=True, indent=formats.formats['INDENT']):
    if currency:
        print(' '*indent, calculation, ' = $', round(float(result), 2))
    else:
        print(' '*indent, calculation, ' = ', round(float(result), 4))


def percent_result(calculation, result, indent=formats.formats['INDENT']):
    print(' '*indent, calculation, ' = ', round(float(result), 4), '%')


def equivalent_result(right_hand, left_hand, value, indent=formats.formats['INDENT']):
    print(' '*indent, f'{right_hand} = {left_hand} = {value}')


def help_msg(indent=formats.formats['INDENT']):
    func_dict, arg_dict = definitions.FUNC_DICT, definitions.ARG_DICT

    title_line('scrilla')
    space(1)

    for paragraph in definitions.HELP_MSG:
        for line in break_lines(paragraph):
            center(line)
        space(1)

    title_line('SYNTAX')
    center(definitions.SYNTAX)
    space(1)

    for func_name in func_dict:
        title_line(func_dict[func_name]['name'])
        for line in break_lines(func_dict[func_name]['description']):
            center(line)
        separator_line()

        commands = func_dict[func_name]['values']
        print(' ', f'COMMAND: {commands[0]}, {commands[1]}')

        if func_dict[func_name]['args'] is not None:
            for arg_name in func_dict[func_name]['args']:
                aliases = arg_dict[arg_name]['values']

                print(
                    ' '*indent, f'OPTION: {aliases[0]}, {aliases[1]}, {aliases[2]}, {aliases[3]}')

                if arg_dict[arg_name]['required']:
                    print(' '*2*indent, 'REQUIRED')

                print(' '*2*indent, f'NAME: {arg_dict[arg_name]["name"]}')

                if arg_dict[arg_name]['default'] is not None:
                    print(' '*2*indent,
                          f'DEFAULT: {arg_dict[arg_name]["default"]}')

                if arg_dict[arg_name]['syntax'] is not None:
                    print(' '*2*indent,
                          f'FORMAT: {arg_dict[arg_name]["syntax"]}')
        separator_line()

# ANALYSIS SPECIFIC OUTPUT FUNCTIONS


def portfolio_percent_result(result, tickers, indent=formats.formats['INDENT']):
    for i, item in enumerate(tickers):
        print(' '*indent, f'{item} =', round(100*result[i], 2), '%')


def portfolio_shares_result(result, tickers, indent=formats.formats['INDENT']):
    for i, item in enumerate(tickers):
        print(' '*indent, f'{item} =', result[i])


def spot_price(ticker, this_spot_price):
    formatted_price = round(float(this_spot_price), 2)
    scalar_result(f'{ticker} spot price', formatted_price)


def model_price(ticker: str, this_model_price: Union[str, float], model: str) -> None:
    formatted_price = round(float(this_model_price), 2)
    scalar_result(f'{ticker} {str(model).upper()} price', formatted_price)


def risk_profile(profiles: Dict[str, Dict[str, float]]) -> None:
    for key, value in profiles.items():
        title_line(f'{key} Risk Profile')
        for subkey, subvalue in value.items():
            scalar_result(f'{subkey}', f'{subvalue}', currency=False)


def moving_average_result(ticker: str, averages: Dict[str, Dict[str, float]]) -> None:
    """
    Prints the results of `scrilla.analysis.models.geometric.statistics.calculate_moving_averages` or `scrilla.analysis.models.reversion.statistics.calculate_moving_averages` to *stdout*.

    Parameters
    ----------
    1. **averages**: ``Dict[str, Dict[str,float]]``
        The dictionary returned from a call to `scrilla.analysis.models.geometric.statistics.calculate_moving_averages` or `scrilla.analysis.models.reversion.statistics.calculate_moving_averages`.
    """
    title_line(f'{ticker} Moving Averages')
    for this_date, average_dict in averages.items():
        center(this_date)
        for avg_key, average in average_dict.items():
            scalar_result(calculation=avg_key, result=average, currency=False)


def screen_results(info, model):
    for ticker in info:
        title_line(f'{ticker} {str(model).upper()} Model vs. Spot Price ')
        spot_price(ticker=ticker, this_spot_price=info[ticker]['spot_price'])
        model_price(ticker=ticker,
                    this_model_price=info[ticker]['model_price'], model=model)
        scalar_result(f'{ticker} discount', info[ticker]['discount'])
        separator_line()

# TODO: can probably combine optimal_result and efficient_frontier into a single function
#         by wrapping the optimal_results in an array so when it iterates through frontier
#         in efficient_frontier, it will only pick up the single allocation array for the
#         optimal result.


def optimal_result(portfolio, allocation, investment=None, latest_prices=None):
    title_line('Optimal Percentage Allocation')
    portfolio_percent_result(allocation, portfolio.tickers)

    if investment is not None:
        shares = portfolio.calculate_approximate_shares(
            allocation, investment, latest_prices)
        total = portfolio.calculate_actual_total(
            allocation, investment, latest_prices)

        title_line('Optimal Share Allocation')
        portfolio_shares_result(shares, portfolio.tickers)
        title_line('Optimal Portfolio Value')
        scalar_result('Total', round(total, 2))

    title_line('Risk-Return Profile')
    scalar_result(calculation='Return', result=portfolio.return_function(
        allocation), currency=False)
    scalar_result(calculation='Volatility', result=portfolio.volatility_function(
        allocation), currency=False)


def efficient_frontier(portfolio, frontier, investment=None, latest_prices=None):
    title_line('(Annual Return %, Annual Volatility %) Portfolio')

    # TODO: edit title to include dates

    for allocation in frontier:
        separator_line()
        return_string = str(
            round(round(portfolio.return_function(allocation), 4)*100, 2))
        vol_string = str(
            round(round(portfolio.volatility_function(allocation), 4)*100, 2))
        title_line(f'({return_string} %, {vol_string}%) Portfolio')
        separator_line()

        title_line('Optimal Percentage Allocation')
        portfolio_percent_result(allocation, portfolio.tickers)

        if investment is not None:
            shares = portfolio.calculate_approximate_shares(
                allocation, investment, latest_prices)
            total = portfolio.calculate_actual_total(
                allocation, investment, latest_prices)

            title_line('Optimal Share Allocation')
            portfolio_shares_result(shares, portfolio.tickers)
            title_line('Optimal Portfolio Value')
            scalar_result('Total', round(total, 2))

        title_line('Risk-Return Profile')
        scalar_result('Return', portfolio.return_function(
            allocation), currency=False)
        scalar_result('Volatility', portfolio.volatility_function(
            allocation), currency=False)
        print('\n')


def correlation_matrix(tickers: List[str], correl_matrix: List[List[float]], display: bool = True):
    """
    Parameters
    ----------
    1. **tickers**: ``list``
        Array of tickers for which the correlation matrix was calculated and formatted.
    2. **indent**: ``int``
        Amount of indent on each new line of the correlation matrix.
    3. **start_date**: ``datetime.date`` 
        Start date of the time period over which correlation was calculated. 
    4. **end_date**: ``datetime.date`` 
        End date of the time period over which correlation was calculated. 

    Returns
    ------
    A correlation matrix string formatted with new lines and spaces.
    """
    entire_formatted_result, formatted_subtitle, formatted_title = "", "", ""

    line_length, first_symbol_length = 0, 0
    new_line = ""
    no_symbols = len(tickers)

    for i in range(no_symbols):
        this_symbol = tickers[i]
        symbol_string = ' '*formats.formats['INDENT'] + f'{this_symbol} '

        if i != 0:
            this_line = symbol_string + ' ' * \
                (line_length - len(symbol_string) - 7*(no_symbols - i))
            # NOTE: seven is number of chars in ' 100.0%'
        else:
            this_line = symbol_string
            first_symbol_length = len(this_symbol)

        new_line = this_line

        for j in range(i, no_symbols):
            if j == i:
                new_line += " 100.0%"

            else:
                result = correl_matrix[i][j]
                formatted_result = str(
                    100*result)[:constants.constants['SIG_FIGS']]
                new_line += f' {formatted_result}%'

        entire_formatted_result += new_line + '\n'

        if i == 0:
            line_length = len(new_line)

    formatted_subtitle += ' ' * \
        (formats.formats['INDENT'] + first_symbol_length+1)
    for i, ticker in enumerate(tickers):
        sym_len = len(ticker)
        formatted_subtitle += f' {ticker}' + ' '*(7-sym_len)
        # NOTE: seven is number of chars in ' 100.0%'
        if i == 0:
            formatted_title += f'({ticker},'
        elif i < len(tickers)-1:
            formatted_title += f'{ticker},'
        else:
            formatted_title += f'{ticker}) correlation matrix'

    formatted_subtitle += '\n'

    whole_thing = formatted_subtitle + entire_formatted_result

    if display:
        title_line(formatted_title)
        print(f'\n{whole_thing}')
        return

    return whole_thing


class Logger():

    def __init__(self, location, log_level="info"):
        self.location = location
        self.log_level = log_level

    # LOGGING FUNCTIONS
    def comment(self, msg):
        now = datetime.datetime.now()
        dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
        print(dt_string, ' :', self.location, ' : ', msg)

    def info(self, msg):
        if self.log_level in [constants.constants['LOG_LEVEL']['INFO'],
                              constants.constants['LOG_LEVEL']['DEBUG'],
                              constants.constants['LOG_LEVEL']['VERBOSE']]:
            self.comment(msg)

    def debug(self, msg):
        if self.log_level in [constants.constants['LOG_LEVEL']['DEBUG'],
                              constants.constants['LOG_LEVEL']['VERBOSE']]:
            self.comment(msg)

    def verbose(self, msg):
        if self.log_level == constants.constants['LOG_LEVEL']['VERBOSE']:
            self.comment(msg)
