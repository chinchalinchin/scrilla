import datetime, sys

import  util.helper as helper
import  util.formatter as formatter

LOG_LEVEL_NONE = "none"
LOG_LEVEL_INFO = "info"
LOG_LEVEL_DEBUG = "debug"
LOG_LEVEL_VERBOSE = "verbose"

def print_below_new_line(msg):
    print(f'\n{msg}')

def title_line(title):
    buff = int((formatter.LINE_LENGTH - len(title))/2)
    print(formatter.SEPARATER*buff, title, formatter.SEPARATER*buff) 
    
def print_line():
    print(formatter.SEPARATER*formatter.LINE_LENGTH)

def return_line():
    print('\n')

def break_lines(msg):
    if len(msg)>formatter.LINE_LENGTH:
        return [msg[i:i+formatter.LINE_LENGTH] for i in range(0,len(msg), formatter.LINE_LENGTH)]
    return [msg]

def center(this_line):
    buff = int((formatter.LINE_LENGTH - len(this_line))/2)
    print(' '*buff, this_line, ' '*buff)

def print_list(list_to_print):
    for i, item in enumerate(list_to_print):
        print(formatter.TAB, f'{i}. {item}')

def string_result(operation, result):
    print(' '*formatter.INDENT, '>>', operation, ' = ', result)
        
def scalar_result(calculation, result, currency=True):
    if currency:
        print(' '*formatter.INDENT, '>>', calculation, ' = $', round(result, 2))
    else:
        print(' '*formatter.INDENT, '>>', calculation, ' = ', round(result, 4))

def equivalent_result(right_hand, left_hand, value):
    print(' '*formatter.INDENT, '>>', f'{right_hand} = {left_hand} = {value}')

def portfolio_percent_result(result, tickers):
    for i, item in enumerate(tickers):
        print(' '*formatter.INDENT, f'{item} =', round(100*result[i], 2), '%')

def portfolio_shares_result(result, tickers):
    for i, item in enumerate(tickers):
        print(' '*formatter.INDENT, f'{item} =', result[i])

def example(ex_no, ex, explanation):
    print(' '*formatter.INDENT, f'#{ex_no}:', ex)
    for l in break_lines(explanation):
        print(' '*2*formatter.INDENT, '-', l)

def examples():
    index = 1
    for ex in formatter.EXAMPLES:
        example(index, ex, formatter.EXAMPLES[ex])
        return_line()
        index += 1
    
def option(opt, explanation):
    print(' '*formatter.INDENT, opt, " :")
    exp_array = explanation.split('__')
    for l in break_lines(exp_array[0]):
        print(' '*formatter.INDENT*2, l)
    if len(exp_array) > 1:
        print(exp_array[1])

def help_msg():
    title_line(formatter.APP_NAME)
    explanation=break_lines(formatter.HELP_MSG)
    for l in explanation:
        center(l)
    return_line()

    title_line('SYNTAX')
    center(formatter.SYNTAX)
    return_line()

    title_line('FUNCTIONS')
    options = formatter.FUNC_ARG_DICT.keys()
    for opt in options:
        option(formatter.FUNC_ARG_DICT[opt], formatter.FUNC_DICT[opt])
        return_line()
        
 # APPLICATION SPECIFIC FORMATTING FUNCTIONS

def spot_price(ticker, this_spot_price):
    formatted_price = round(float(this_spot_price), 2)
    scalar_result(f'{ticker} spot price', formatted_price)
    
def model_price(ticker, this_model_price, model):
    formatted_price = round(float(this_model_price),2)
    scalar_result(f'{ticker} {str(model).upper()} price', formatted_price)

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
        print_line()

# TODO: can probably combine optimal_result and efficient_frontier into a single function
#         by wrapping the optimal_results in an array so when it iterates through frontier
#         in efficient_frontier, it will only pick up the single allocation array for the
#         optimal result.
def optimal_result(portfolio, allocation, investment=None):
    title_line('Optimal Percentage Allocation')
    portfolio_percent_result(allocation, portfolio.tickers)
    print_line()

    if investment is not None:
        shares = portfolio.calculate_approximate_shares(allocation, investment)
        total = portfolio.calculate_actual_total(allocation, investment)
        
        print_line()
        title_line('Optimal Share Allocation')
        portfolio_shares_result(shares, portfolio.tickers)
        title_line('Optimal Portfolio Value')
        scalar_result('Total', round(total,2))

    title_line('Risk-Return Profile')
    scalar_result(calculation='Return', result=portfolio.return_function(allocation), currency=False)
    scalar_result(calculation='Volatility', result=portfolio.volatility_function(allocation), currency=False)

def efficient_frontier(portfolio, frontier, investment=None, save_file=None):
    title_line('(Annual Return %, Annual Volatility %) Portfolio')

    # TODO: edit title to include dates

    for allocation in frontier:
        print_line()
        return_string=str(round(round(portfolio.return_function(allocation),4)*100,2))
        vol_string=str(round(round(portfolio.volatility_function(allocation),4)*100,2))
        title_line(f'({return_string} %, {vol_string}%) Portfolio')
        print_line()

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
        return_line()

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
        if self.log_level in [LOG_LEVEL_INFO, LOG_LEVEL_DEBUG, LOG_LEVEL_VERBOSE]:
            self.comment(msg)

    def debug(self, msg):
        if self.log_level in [LOG_LEVEL_DEBUG, LOG_LEVEL_VERBOSE]:
            self.comment(msg)

    def verbose(self, msg):
        if self.log_level == LOG_LEVEL_VERBOSE:
            self.comment(msg)
            
    def sys_error(self):
        e, f, g = sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2]
        msg = f'{e} \n {f} \n {g} \n'
        self.debug(msg)

    def log_arguments(self, main_args, xtra_args, xtra_values):
        self.debug(f'Main Arguments: {main_args}')
        for i, item in enumerate(xtra_args):
            if i < len(xtra_values):
                self.debug(f'Extra Argument: {item} = {xtra_values[i]}')
            else:
                self.debug(f'Extra Argument: {item}')

    def log_django_settings(self, settings):
            print_line()
            title_line('SETTINGS.PY Configuration')

            print_line()
            self.comment("# Environment Configuration")
            self.comment(f'> Server Location : {settings.BASE_DIR}')
            self.comment(f'> App Location : {settings.APP_DIR}')
            self.comment(f'> Environment: {settings.APP_ENV}')

            print_line()
            self.comment("# Application Configuration")
            self.comment(f'> Debug : {settings.DEBUG}')
            self.comment(f'> Log Level: {settings.LOG_LEVEL}')

            print_line()
            self.comment("# Headers Configuration")
            self.comment(f'> ALLOWED_HOSTS: {settings.ALLOWED_HOSTS}')
            if hasattr(settings, 'CORS_ALLOW_ALL_ORIGINS'):
                self.comment(f'> CORS_ALLOW_ALL_ORIGINS: {settings.CORS_ALLOW_ALL_ORIGINS}')
            if hasattr(settings, 'CORS_ALLOWED_ORIGINS'):
                self.comment(f'> CORS_ALLOWED_ORIGINS {settings.CORS_ALLOWED_ORIGINS}')
            
            print_line()
            self.comment("# Database Configuration")
            self.comment(f'> Database Engine: {settings.DATABASES["default"]["ENGINE"]}')
            self.comment(f'> Database Host: {settings.DATABASES["default"]["HOST"]}')
            self.comment(f'> Database Port: {settings.DATABASES["default"]["PORT"]}')
            print_line()
