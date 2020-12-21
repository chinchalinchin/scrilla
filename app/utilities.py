import datetime, os, dotenv

APP_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

dotenv.load_dotenv(os.path.join(APP_DIR,'.env'))

BUFFER_DIR = os.path.join(APP_DIR, 'cache')

QUERY_URL = os.getenv('AV_QUERY_URL')

ONE_TRADING_DAY=(1/252)

DEBUG=False

SEPARATER="-"
LINE_LENGTH=100
INDENT=10

FUNC_DICT={
    "efficient_frontier": "-f",
    "minimize_variance": "-m",
    "optimize_portfolio": "-o",
    "risk_return" : "-r",
    "correlation":"-c",
    "help": "-h",
    "examples": "-e"
}

def get_number_input(msg_prompt):
    flag = False 
    while flag is not True:
        user_input = input(msg_prompt)
        if isinstance(float(user_input), float):
            return user_input
        else:
            print('Input Not Understood. Please Enter A Numerical Value.')
        
class Logger():

    def __init__(self, location):
        self.location = location
    
    def comment(self, msg):
        now = datetime.datetime.now()
        dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
        print(dt_string, ' :' , self.location, ' : ',msg)

    def debug(self, msg):
        if DEBUG:
            self.comment(msg)

    def title_line(self, title):
        buff = int((LINE_LENGTH - len(title))/2)
        print(SEPARATER*buff, title, SEPARATER*buff) 
    
    def line(self):
        print(SEPARATER*LINE_LENGTH)

    def center(self, this_line):
        buff = int((LINE_LENGTH - len(this_line))/2)
        print(' '*buff, this_line, ' '*buff)

    def scalar_result(self, calculation, result):
        print(' '*INDENT, '>>', calculation, ' = ', round(result, 4))

    # TODO: align columns in result output
    def array_percent_result(self, calculation, result, tickers):
        for i in range(len(tickers)):
            print(' '*INDENT, f'{tickers[i]} =', round(100*result[i], 2), '%')

    def array_result(self, calculation, result, tickers):
        for i in range(len(tickers)):
            print(' '*INDENT, f'{tickers[i]} =', result[i])

    def option(self, opt, explanation):
        print(' '*INDENT, opt, " = ", explanation)

    def help(self):
        self.title_line('PYNANCE')
        line_1 = 'A financial application written in python to determine optimal portfolio allocations,'
        line_2 = 'in addition to calculating fundamental equity statistics.'
        self.center(line_1)
        self.center(line_2)
        print()

        self.title_line('SYNTAX')
        line_3 = 'command -OPTION [tickers] (additional input)'
        self.center(line_3)
        print()

        self.title_line('OPTIONS')
        self.option(FUNC_DICT['correlation'], 'Calculate pair-wise correlation for the supplied list of ticker symbols. \n')
        self.option(FUNC_DICT['examples'], 'Display examples of syntax. \n')
        self.option(FUNC_DICT['efficient_frontier'], 'Generate a plot of the portfolio\'s efficient frontier for the supplied list of tickers. \n')
        self.option(FUNC_DICT['help'], 'Print this help message. \n')
        self.option(FUNC_DICT['minimize_variance'], 'Minimize the variance of the portfolio defined by the supplied list of ticker symbols. \n')
        self.option(FUNC_DICT['risk_return'], 'Calculate the risk-return profile for the supplied list of ticker symbols. \n')
        self.option(FUNC_DICT['optimize_portfolio'], 'Optimize the variance of the portfolio\'s variance subject to the supplied return target. \n')
        
