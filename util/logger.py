import datetime, sys
import numpy as numpy
import matplotlib.pyplot as matplotlib

import app.settings as settings

import util.helpers as helper


class Logger():

    def __init__(self, location):
        self.location = location
    
    # FORMATTING FUNCTIONS
    def comment(self, msg):
        now = datetime.datetime.now()
        dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
        print(dt_string, ' :' , self.location, ' : ',msg)

    def return_line(self):
        print('\n')

    def break_lines(self, msg):
        if len(msg)>settings.LINE_LENGTH:
            return [msg[i:i+settings.LINE_LENGTH] for i in range(0,len(msg), settings.LINE_LENGTH)]
        else:
            return [msg]

    def debug(self, msg):
        if settings.DEBUG:
            self.comment(msg)

    def verbose(self, msg):
        if settings.VERBOSE:
            self.comment(msg)
            
    def sys_error(self):
        e = sys.exc_info()[0]
        f = sys.exc_info()[1]
        g = sys.exc_info()[2]
        msg = f'{e} \n {f} \n {g} \n'
        self.debug(msg)

    def title_line(self, title):
        buff = int((settings.LINE_LENGTH - len(title))/2)
        print(settings.SEPARATER*buff, title, settings.SEPARATER*buff) 
    
    def line(self):
        print(settings.SEPARATER*settings.LINE_LENGTH)

    def center(self, this_line):
        buff = int((settings.LINE_LENGTH - len(this_line))/2)
        print(' '*buff, this_line, ' '*buff)

    # PRE-FORMATTED FUNCTIONS
    def example_expo(self, ex_no, example, explanation):
        print(' '*settings.INDENT, f'#{ex_no}:', example)
        for line in self.break_lines(explanation):
            print(' '*2*settings.INDENT, '-', line)

    def examples(self):
        index = 1
        for example in settings.EXAMPLES:
            self.example_expo(index, example, settings.EXAMPLES[example])
            self.return_line()
            index += 1

    def option(self, opt, explanation):
        print(' '*settings.INDENT, opt, " :")
        for line in self.break_lines(explanation):
            print(' '*settings.INDENT*2, line)

    def help(self):
        self.title_line(settings.APP_NAME)
        explanation=self.break_lines(settings.HELP_MSG)
        for line in explanation:
            self.center(line)
        self.return_line()

        self.title_line('SYNTAX')
        self.center(settings.SYNTAX)
        self.return_line()

        self.title_line('OPTIONS')
        options = settings.FUNC_ARG_DICT.keys()
        for option in options:
            self.option(settings.FUNC_ARG_DICT[option], settings.FUNC_DICT[option])
            self.return_line()

    # APPLICATION SPECIFIC FORMATTING FUNCTIONS
    def string_result(self, operation, result):
        print(' '*settings.INDENT, '>>', operation, ' = ', result)
        
    def scalar_result(self, calculation, result):
        print(' '*settings.INDENT, '>>', calculation, ' = ', round(result, 4))

    def portfolio_percent_result(self, result, tickers):
        for i in range(len(tickers)):
            print(' '*settings.INDENT, f'{tickers[i]} =', round(100*result[i], 2), '%')

    def portfolio_shares_result(self, result, tickers):
        for i in range(len(tickers)):
            print(' '*settings.INDENT, f'{tickers[i]} =', result[i])

    def moving_average_result(self, tickers, averages):
        MA1_prefix, MA2_prefix, MA3_prefix = f'MA({settings.MA_1_PERIOD})', f'MA({settings.MA_2_PERIOD})', f'MA({settings.MA_3_PERIOD})'
        for i in range(len(tickers)):
            title = f'{tickers[i]} Moving Average of Daily Return for {settings.MA_1_PERIOD}, {settings.MA_2_PERIOD} & {settings.MA_3_PERIOD} Days'
            self.title_line(title)

            MA1_title, MA2_title, MA3_title = f'{MA1_prefix}_{tickers[i]}', f'{MA2_prefix}_{tickers[i]}', f'{MA3_prefix}_{tickers[i]}'
            self.scalar_result(MA1_title, round(averages[i][0], 2))
            self.scalar_result(MA2_title, round(averages[i][1], 2))
            self.scalar_result(MA3_title, round(averages[i][2], 2))

    def optimal_result(self, portfolio, allocation):
        self.title_line('Optimal Percentage Allocation')
        self.portfolio_percent_result(allocation, portfolio.tickers)
        self.line()

        if settings.INVESTMENT_MODE:
            investment = helper.get_number_input("Please Enter Total Investment : \n")
            shares = portfolio.calculate_approximate_shares(allocation, investment)
            total = portfolio.calculate_actual_total(allocation, investment)
            
            self.line()
            self.title_line('Optimal Share Allocation')
            self.portfolio_shares_result(shares, portfolio.tickers)
            self.title_line('Optimal Portfolio Value')
            self.scalar_result('Total', round(total,2))

        self.title_line('Risk-Return Profile')
        self.scalar_result('Return', portfolio.return_function(allocation))
        self.scalar_result('Volatility', portfolio.volatility_function(allocation))

    def efficient_frontier(self, portfolio, frontier):
        if settings.INVESTMENT_MODE:
            investment = helper.get_number_input("Please Enter Total Investment : \n")
        else:
            investment = 1000
        
        self.title_line(f'(Annual Return %, Annual Volatility %) Portfolio')

        for allocation in frontier:
            self.line()
            return_string=str(round(round(portfolio.return_function(allocation),4)*100,2))
            vol_string=str(round(round(portfolio.volatility_function(allocation),4)*100,2))
            self.title_line(f'({return_string} %, {vol_string}%) Portfolio')
            self.line()

            self.title_line('Optimal Percentage Allocation')

            self.portfolio_percent_result(allocation, portfolio.tickers)
            
            if settings.INVESTMENT_MODE:
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

    # APPLICATION SPECIFIC GRAPHICS
    def plot_frontier(self, portfolio, frontier):
        return_profile=[]
        risk_profile=[]
        for allocation in frontier:
            return_profile.append(portfolio.return_function(allocation))
            risk_profile.append(portfolio.volatility_function(allocation))
        return_profile = numpy.array(return_profile)
        risk_profile = numpy.array(risk_profile)
        
        title = " ( "
        for i in range(len(portfolio.tickers)):
            if i != (len(portfolio.tickers) - 1):
                title += portfolio.tickers[i] + ", "
            else:
                title += portfolio.tickers[i] + " ) Efficient Frontier"
        
        matplotlib.plot(risk_profile, return_profile, linestyle='dashed')
        matplotlib.xlabel('Volatility')
        matplotlib.ylabel('Return')
        matplotlib.title(title)
        matplotlib.show()
    
    def plot_moving_averages(self, tickers, averages):
        width = settings.BAR_WIDTH
        x = numpy.arange(len(tickers))
        fig, ax = matplotlib.subplots()
        
        ma1s, ma2s, ma3s = [], [], []
        for i in range(len(tickers)):
            ma1s.append(averages[i][0])
            ma2s.append(averages[i][1])
            ma3s.append(averages[i][2])
        
        ma1_label, ma2_label, ma3_label = f'MA({settings.MA_1_PERIOD})', f'MA({settings.MA_2_PERIOD})', f'MA({settings.MA_3_PERIOD})'
        ax.bar(x - width, ma1s, width, label=ma1_label)
        ax.bar(x, ma2s, width, label=ma2_label)
        ax.bar(x + width, ma3s, width, label=ma3_label)

        ax.set_ylabel('Moving Average of Daily Return')
        ax.set_title('Moving Averages of Daily Return Grouped By Equity')
        ax.set_xticks(x)
        ax.set_xticklabels(tickers)
        ax.legend()


        matplotlib.show()