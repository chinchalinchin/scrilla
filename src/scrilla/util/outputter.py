import datetime

from scrilla.static import constants, formats, definitions

### GENERAL OUTPUT FUNCTIONS
def title_line(title, line_length=formats.LINE_LENGTH, separater=formats.SEPARATER):
    buff = int((line_length - len(title))/2)
    print(separater*buff, title, separater*buff) 
    
def print_separator_line(line_length=formats.LINE_LENGTH, separater=formats.SEPARATER):
    print(separater*line_length)

def break_lines(msg, line_length=formats.LINE_LENGTH):
    if len(msg)>line_length:
        return [msg[i:i+line_length] for i in range(0,len(msg), line_length)]
    return [msg]

def center(this_line, line_length=formats.LINE_LENGTH):
    buff = int((line_length - len(this_line))/2)
    print(' '*buff, this_line, ' '*buff)

def print_list(list_to_print, indent=formats.INDENT):
    for i, item in enumerate(list_to_print):
        print(' '*indent, f'{i}. {item}')

def string_result(operation, result, indent=formats.INDENT):
    print(' '*indent, operation, ' = ', result)
        
def scalar_result(calculation, result, currency=True, indent=formats.INDENT):
    if currency:
        print(' '*indent, calculation, ' = $', round(float(result), 2))
    else:
        print(' '*indent, calculation, ' = ', round(float(result), 4))

def percent_result(calculation, result, indent=formats.INDENT):
    print(' '*indent, calculation, ' = ', round(float(result), 4), '%')

def equivalent_result(right_hand, left_hand, value, indent=formats.INDENT):
    print(' '*indent, f'{right_hand} = {left_hand} = {value}')

def function_option():
    pass

def function_summary():
    pass

def help_msg():
    func_dict = definitions.FUNC_DICT
    arg_dict = definitions.ARG_DICT

    for func_name in func_dict:
        proper_func_name = func_dict[func_name]['name']
        description = func_dict[func_name]['description']
        for arg_name in func_dict[func_name]['values']:
            proper_arg_name = arg_dict[arg_name]['name']
            arg_values = arg_dict[arg_name]['values']
            arg_description = arg_dict[arg_name]['description']

        pass

    pass

### ANALYSIS SPECIFIC OUTPUT FUNCTIONS
def portfolio_percent_result(result, tickers,indent=formats.INDENT):
    for i, item in enumerate(tickers):
        print(' '*indent, f'{item} =', round(100*result[i], 2), '%')

def portfolio_shares_result(result, tickers, indent=formats.INDENT):
    for i, item in enumerate(tickers):
        print(' '*indent, f'{item} =', result[i])

def spot_price(ticker, this_spot_price):
    formatted_price = round(float(this_spot_price), 2)
    scalar_result(f'{ticker} spot price', formatted_price)
    
def model_price(ticker, this_model_price, model):
    formatted_price = round(float(this_model_price),2)
    scalar_result(f'{ticker} {str(model).upper()} price', formatted_price)

def risk_profile(profiles):
    for key, value in profiles.items():
        title_line(f'{key} Risk Profile')
        for subkey, subvalue in value.items():
            scalar_result(f'{subkey}', f'{subvalue}', currency=False)

def moving_average_result(tickers, averages_output, periods, start_date = None, end_date = None):
    averages, dates = averages_output
    MA1_prefix, MA2_prefix, MA3_prefix = f'MA({periods[0]})', f'MA({periods[1]})', f'MA({periods[2]})'
    if start_date is None and end_date is None:
        for i, item in enumerate(tickers):
            title = f'{item} Moving Average of Daily Return for {periods[0]}, {periods[1]} & {periods[0]} Days'
            title_line(title)

            MA1_title, MA2_title, MA3_title = f'{MA1_prefix}_{item}', f'{MA2_prefix}_{item}', f'{MA3_prefix}_{item}'
            scalar_result(MA1_title, round(averages[i][0], 2))
            scalar_result(MA2_title, round(averages[i][1], 2))
            scalar_result(MA3_title, round(averages[i][2], 2))
    else:
        for i, item in enumerate(tickers):

            title = f'{item} Moving Average of Daily Return for {periods[0]}, {periods[1]} & {periods[0]} Days'
            title_line(title)

            MA1_title, MA2_title, MA3_title = f'{MA1_prefix}_{item}', f'{MA2_prefix}_{item}', f'{MA3_prefix}_{item}'
            for j, item in enumerate(dates):
                msg_1 = f'{item} : {MA1_title}'
                scalar_result(msg_1, round(averages[i][0][j], 2))
            for j, item in enumerate(dates):
                msg_2 = f'{item} : {MA2_title}'
                scalar_result(msg_2, round(averages[i][1][j], 2))
            for j, item in enumerate(dates):  
                msg_3 = f'{item} : {MA3_title}'
                scalar_result(msg_3, round(averages[i][2][j], 2))      

def screen_results(info, model):
    for ticker in info:
        title_line(f'{ticker} {str(model).upper()} Model vs. Spot Price ')
        spot_price(ticker=ticker, this_spot_price=info[ticker]['spot_price'])
        model_price(ticker=ticker, this_model_price=info[ticker]['model_price'], model=model)
        scalar_result(f'{ticker} discount', info[ticker]['discount'])
        print_separator_line()

# TODO: can probably combine optimal_result and efficient_frontier into a single function
#         by wrapping the optimal_results in an array so when it iterates through frontier
#         in efficient_frontier, it will only pick up the single allocation array for the
#         optimal result.
def optimal_result(portfolio, allocation, investment=None):
    title_line('Optimal Percentage Allocation')
    portfolio_percent_result(allocation, portfolio.tickers)
    print_separator_line()

    if investment is not None:
        shares = portfolio.calculate_approximate_shares(allocation, investment)
        total = portfolio.calculate_actual_total(allocation, investment)
        
        print_separator_line()
        title_line('Optimal Share Allocation')
        portfolio_shares_result(shares, portfolio.tickers)
        title_line('Optimal Portfolio Value')
        scalar_result('Total', round(total,2))

    title_line('Risk-Return Profile')
    scalar_result(calculation='Return', result=portfolio.return_function(allocation), currency=False)
    scalar_result(calculation='Volatility', result=portfolio.volatility_function(allocation), currency=False)

def efficient_frontier(portfolio, frontier, investment=None):
    title_line('(Annual Return %, Annual Volatility %) Portfolio')

    # TODO: edit title to include dates

    for allocation in frontier:
        print_separator_line()
        return_string=str(round(round(portfolio.return_function(allocation),4)*100,2))
        vol_string=str(round(round(portfolio.volatility_function(allocation),4)*100,2))
        title_line(f'({return_string} %, {vol_string}%) Portfolio')
        print_separator_line()

        title_line('Optimal Percentage Allocation')
        portfolio_percent_result(allocation, portfolio.tickers)
        
        if investment is not None:
            shares = portfolio.calculate_approximate_shares(allocation, investment)
            total = portfolio.calculate_actual_total(allocation, investment)
        
            title_line('Optimal Share Allocation')
            portfolio_shares_result(shares, portfolio.tickers)
            title_line('Optimal Portfolio Value')
            scalar_result('Total', round(total,2))
        
        title_line('Risk-Return Profile')
        scalar_result('Return', portfolio.return_function(allocation), currency=False)
        scalar_result('Volatility', portfolio.volatility_function(allocation), currency=False)
        print('\n')

def correlation_matrix(tickers, correlation_matrix):
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
    
    Output
    ------
    A correlation matrix string formatted with new lines and spaces.
    """
    entire_formatted_result, formatted_title = "", ""

    line_length, first_symbol_length = 0, 0
    new_line=""
    no_symbols = len(tickers)

    for i in range(no_symbols):
        this_symbol = tickers[i]
        symbol_string = ' '*formats.INDENT + f'{this_symbol} '

        if i != 0:
            this_line = symbol_string + ' '*(line_length - len(symbol_string) - 7*(no_symbols - i))
            # NOTE: seven is number of chars in ' 100.0%'
        else: 
            this_line = symbol_string
            first_symbol_length = len(this_symbol)

        new_line = this_line
        
        for j in range(i, no_symbols):
            if j == i:
                new_line += " 100.0%"
            
            else:
                result = correlation_matrix[i][j]
                formatted_result = str(100*result)[:constants['SIG_FIGS']]
                new_line += f' {formatted_result}%'

        entire_formatted_result += new_line + '\n'
        
        if i == 0:
            line_length = len(new_line)

    formatted_title += ' '*(formats.INDENT + first_symbol_length+1)
    for symbol in tickers:
        sym_len = len(symbol)
        formatted_title += f' {symbol}'+ ' '*(7-sym_len)
        # NOTE: seven is number of chars in ' 100.0%'
    formatted_title += '\n'

    whole_thing = formatted_title + entire_formatted_result

    print(f'\n{whole_thing}')

class Logger():

    def __init__(self, location, log_level="info"):
        self.location = location
        self.log_level = log_level
    
    # LOGGING FUNCTIONS
    def comment(self, msg):
        now = datetime.datetime.now()
        dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
        print(dt_string, ' :' , self.location, ' : ',msg)

    def info(self, msg):
        if self.log_level in [constants['LOG_LEVEL']['INFO'], 
                                constants['LOG_LEVEL']['DEBUG'], 
                                constants['LOG_LEVEL']['VERBOSE']]:
            self.comment(msg)

    def debug(self, msg):
        if self.log_level in [constants['LOG_LEVEL']['DEBUG'], 
                                constants['LOG_LEVEL']['VERBOSE']]:
            self.comment(msg)

    def verbose(self, msg):
        if self.log_level == constants['LOG_LEVEL']['VERBOSE']:
            self.comment(msg)
