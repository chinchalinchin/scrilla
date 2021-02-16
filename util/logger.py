import datetime, sys
import numpy
import matplotlib.pyplot as matplotlib

import util.helper as helper
import util.formatter as formatter

LOG_LEVEL_NONE = "none"
LOG_LEVEL_INFO = "info"
LOG_LEVEL_DEBUG = "debug"
LOG_LEVEL_VERBOSE = "verbose"

class Logger():

    def __init__(self, location, log_level="info"):
        self.location = location
        self.log_level = log_level
    
    # FORMATTING FUNCTIONS
    def comment(self, msg):
        now = datetime.datetime.now()
        dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
        print(dt_string, ' :' , self.location, ' : ',msg)

    @staticmethod
    def return_line():
        print('\n')

    @staticmethod
    def break_lines(msg):
        if len(msg)>formatter.LINE_LENGTH:
            return [msg[i:i+formatter.LINE_LENGTH] for i in range(0,len(msg), formatter.LINE_LENGTH)]
        else:
            return [msg]

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

    @staticmethod
    def title_line(title):
        buff = int((formatter.LINE_LENGTH - len(title))/2)
        print(formatter.SEPARATER*buff, title, formatter.SEPARATER*buff) 
    
    @staticmethod
    def line():
        print(formatter.SEPARATER*formatter.LINE_LENGTH)

    @staticmethod
    def center(this_line):
        buff = int((formatter.LINE_LENGTH - len(this_line))/2)
        print(' '*buff, this_line, ' '*buff)

    @staticmethod
    def print_list(list_to_print):
        for i in range(len(list_to_print)):
            print(formatter.TAB, f'{i}. {list_to_print[i]}')
    
    # PRE-FORMATTED FUNCTIONS
    def example(self, ex_no, example, explanation):
        print(' '*formatter.INDENT, f'#{ex_no}:', example)
        for line in self.break_lines(explanation):
            print(' '*2*formatter.INDENT, '-', line)

    def examples(self):
        index = 1
        for example in formatter.EXAMPLES:
            self.example(index, example, formatter.EXAMPLES[example])
            self.return_line()
            index += 1

    def option(self, opt, explanation):
        print(' '*formatter.INDENT, opt, " :")
        for line in self.break_lines(explanation):
            print(' '*formatter.INDENT*2, line)

    def help(self):
        self.title_line(formatter.APP_NAME)
        explanation=self.break_lines(formatter.HELP_MSG)
        for line in explanation:
            self.center(line)
        self.return_line()

        self.title_line('SYNTAX')
        self.center(formatter.SYNTAX)
        self.return_line()

        self.title_line('OPTIONS')
        options = formatter.FUNC_ARG_DICT.keys()
        for option in options:
            self.option(formatter.FUNC_ARG_DICT[option], formatter.FUNC_DICT[option])
            self.return_line()

    def arguments(self, main_args, xtra_args, xtra_values):
        self.debug(f'Main Arguments: {main_args}')
        for i in range(len(xtra_args)):
            if i < len(xtra_values):
                self.debug(f'Extra Argument: {xtra_args[i]} = {xtra_values[i]}')
            else:
                self.debug(f'Extra Argument: {xtra_args[i]}')

    # APPLICATION SPECIFIC FORMATTING FUNCTIONS
    @staticmethod
    def string_result(operation, result):
        print(' '*formatter.INDENT, '>>', operation, ' = ', result)
        
    @staticmethod
    def scalar_result(calculation, result, currency=True):
        if currency:
            print(' '*formatter.INDENT, '>>', calculation, ' = $', round(result, 2))
        else:
            print(' '*formatter.INDENT, '>>', calculation, ' = ', round(result, 4))

    @staticmethod
    def equivalent_result(right_hand, left_hand, value):
        print(' '*formatter.INDENT, '>>', f'{right_hand} = {left_hand} = {value}')

    def spot_price(self, ticker, spot_price):
        formatted_price = round(float(spot_price), 2)
        self.scalar_result(f'{ticker} spot price', formatted_price)
    
    def model_price(self, ticker, model_price, model):
        formatted_price = round(float(model_price),2)
        self.scalar_result(f'{ticker} {str(model).upper()} price', formatted_price)
    
    @staticmethod
    def portfolio_percent_result(result, tickers):
        for i in range(len(tickers)):
            print(' '*formatter.INDENT, f'{tickers[i]} =', round(100*result[i], 2), '%')

    @staticmethod
    def portfolio_shares_result(result, tickers):
        for i in range(len(tickers)):
            print(' '*formatter.INDENT, f'{tickers[i]} =', result[i])

    def moving_average_result(self, tickers, averages_output, periods, start_date = None, end_date = None):
        averages, dates = averages_output
        MA1_prefix, MA2_prefix, MA3_prefix = f'MA({periods[0]})', f'MA({periods[1]})', f'MA({periods[2]})'
        if start_date is None and end_date is None:
            for i in range(len(tickers)):
                title = f'{tickers[i]} Moving Average of Daily Return for {periods[0]}, {periods[1]} & {periods[0]} Days'
                self.title_line(title)

                MA1_title, MA2_title, MA3_title = f'{MA1_prefix}_{tickers[i]}', f'{MA2_prefix}_{tickers[i]}', f'{MA3_prefix}_{tickers[i]}'
                self.scalar_result(MA1_title, round(averages[i][0], 2))
                self.scalar_result(MA2_title, round(averages[i][1], 2))
                self.scalar_result(MA3_title, round(averages[i][2], 2))
        else:
            for i in range(len(tickers)):

                title = f'{tickers[i]} Moving Average of Daily Return for {periods[0]}, {periods[1]} & {periods[0]} Days'
                self.title_line(title)

                MA1_title, MA2_title, MA3_title = f'{MA1_prefix}_{tickers[i]}', f'{MA2_prefix}_{tickers[i]}', f'{MA3_prefix}_{tickers[i]}'
                count = 0
                for j in range(len(dates)):
                    msg_1 = f'{dates[j]} : {MA1_title}'
                    self.scalar_result(msg_1, round(averages[i][0][j], 2))
                for j in range(len(dates)):
                    msg_2 = f'{dates[j]} : {MA2_title}'
                    self.scalar_result(msg_2, round(averages[i][1][j], 2))
                for j in range(len(dates)):  
                    msg_3 = f'{dates[j]} : {MA3_title}'
                    self.scalar_result(msg_3, round(averages[i][2][j], 2))      

    def screen_results(self, info, model):
        for ticker in info:
            self.title_line(f'{ticker} {str(model).upper()} Model vs. Spot Price ')
            self.spot_price(ticker=ticker, spot_price=info[ticker]['spot_price'])
            self.model_price(ticker=ticker, model_price=info[ticker]['model_price'], model=model)
            self.scalar_result(f'{ticker} discount', info[ticker]['discount'])
            self.line()

    # TODO: can probably combine optimal_result and efficient_frontier into a single function
    #         by wrapping the optimal_results in an array so when it iterates through frontier
    #         in efficient_frontier, it will only pick up the single allocation array for the
    #         optimal result.
    def optimal_result(self, portfolio, allocation, user_input):
        self.title_line('Optimal Percentage Allocation')
        self.portfolio_percent_result(allocation, portfolio.tickers)
        self.line()

        if user_input:
            investment = helper.get_number_input("Please Enter Total Investment : \n")
            shares = portfolio.calculate_approximate_shares(allocation, investment)
            total = portfolio.calculate_actual_total(allocation, investment)
            
            self.line()
            self.title_line('Optimal Share Allocation')
            self.portfolio_shares_result(shares, portfolio.tickers)
            self.title_line('Optimal Portfolio Value')
            self.scalar_result('Total', round(total,2))

        self.title_line('Risk-Return Profile')
        self.scalar_result(calculation='Return', result=portfolio.return_function(allocation), currency=False)
        self.scalar_result(calculation='Volatility', result=portfolio.volatility_function(allocation), currency=False)

    def efficient_frontier(self, portfolio, frontier, user_input):
        if user_input:
            investment = helper.get_number_input("Please Enter Total Investment : \n")
        else:
            investment = 1000
        
        self.title_line(f'(Annual Return %, Annual Volatility %) Portfolio')
        # TODO: edit title to include dates

        for allocation in frontier:
            self.line()
            return_string=str(round(round(portfolio.return_function(allocation),4)*100,2))
            vol_string=str(round(round(portfolio.volatility_function(allocation),4)*100,2))
            self.title_line(f'({return_string} %, {vol_string}%) Portfolio')
            self.line()

            self.title_line('Optimal Percentage Allocation')

            self.portfolio_percent_result(allocation, portfolio.tickers)
            
            if user_input:
                shares = portfolio.calculate_approximate_shares(allocation, investment)
                total = portfolio.calculate_actual_total(allocation, investment)
            
                self.title_line('Optimal Share Allocation')
                self.portfolio_shares_result(shares, portfolio.tickers)
                self.title_line('Optimal Portfolio Value')
                self.scalar_result('Total', round(total,2))
            
            self.title_line('Risk-Return Profile')
            self.scalar_result('Return', portfolio.return_function(allocation))
            self.scalar_result('Volatility', portfolio.volatility_function(allocation))
            self.return_line()

    def log_django_settings(self, settings):
            self.line()
            self.title_line('SETTINGS.PY Configuration')
            self.line()
            self.comment("# Environment Configuration")
            self.comment(f'> Directory Location : {settings.BASE_DIR}')
            self.comment(f'> Environment: {settings.APP_ENV}')
            self.line()
            self.comment("# Application Configuration")
            self.comment(f'> Debug : {settings.DEBUG}')
            self.comment(f'> Enviroment: {settings.APP_ENV}')
            self.comment(f'> Log Level: {settings.LOG_LEVEL}')
            self.line()
            self.comment("# Database Configuration")
            self.comment(f'> Database Engine: {settings.DATABASES["default"]["ENGINE"]}')
            self.line()
