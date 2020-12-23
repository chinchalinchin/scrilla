import datetime, os, dotenv

# Application Settings
APP_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

dotenv.load_dotenv(os.path.join(APP_DIR,'.env'))

BUFFER_DIR = os.path.join(APP_DIR, 'cache')

QUERY_URL = os.getenv('AV_QUERY_URL')

DEBUG= True if os.getenv('DEBUG') == 'True' else False

PORTFOLIO_MODE = True if os.getenv('PORTFOLIO_MODE') == 'True' else False

ONE_TRADING_DAY=(1/252)

SEPARATER="-"

LINE_LENGTH=100

INDENT=10

FUNC_DICT={
    "efficient_frontier": "-ef",
    "minimize_variance": "-min",
    "maximize_return": "-max",
    "optimize_portfolio": "-opt",
    "risk_return" : "-rr",
    "correlation":"-cor",
    "help": "-help",
    "examples": "-ex"
}

EXAMPLES = { 
    'python ./main.py -rr GOOG AMZN XOM AAPL': 'Calculate the risk-return portfolio for each equity in the portfolio composed of (GOOG, AMZN, XOM, APPL)',
    'python ./main.py -cor GLD SPY SLV UUP TLT EWA': 'Calculate the correlation matrix for the portfolio composed of (GLD, SPY, SLV, UUP, TLT, EWA',
    'python ./main.py -min U TSLA SPCE': 'Find the portfolio allocation that minimizes the overall variance of the portfolio composed of (U, TSLA, SPCE). ',
    'python ./main.py -opt ALLY FB PFE SNE BX 0.83': 'Optimize the portfolio consisting of (ALLY, FB, PFE, SNE, BX) subject to the constraint their mean annual return equal 83%. Note the constrained return must reside within the feasible region of returns, i.e. the constrained return must be less than the maximum possible return.',  
    'python ./main.py -ef QS DIS RUN 5': 'Calculate a five point plot of the efficient portfolio (risk, return) frontier for the portfolio composed of (QS, DIS, RUN)'
}

# Application Helper Functions

def get_number_input(msg_prompt):
    flag = False 
    while flag is not True:
        user_input = input(msg_prompt)
        if isinstance(float(user_input), float):
            return user_input
        else:
            print('Input Not Understood. Please Enter A Numerical Value.')

# Application Logger        
class Logger():

    def __init__(self, location):
        self.location = location
    
    def comment(self, msg):
        now = datetime.datetime.now()
        dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
        print(dt_string, ' :' , self.location, ' : ',msg)

    def blank_line(self):
        print('\n')

    def break_lines(self, msg):
        if len(msg)>LINE_LENGTH:
            return [msg[i:i+LINE_LENGTH] for i in range(0,len(msg), LINE_LENGTH)]
        else:
            return [msg]

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

    def example_expo(self, ex_no, example, explanation):
        print(' '*INDENT, f'#{ex_no}:', example)
        for line in self.break_lines(explanation):
            print(' '*2*INDENT, '-', line)

    def examples(self):
        index = 1
        for example in EXAMPLES:
            self.example_expo(index, example, EXAMPLES[example])
            index += 1

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

    def optimal_result(self, portfolio, allocation):
        self.title_line('Optimal Percentage Allocation')
        self.array_percent_result('Optimal Portfolio Percentage Allocation', allocation, portfolio.tickers)
        self.line()

        if PORTFOLIO_MODE:
            investment = get_number_input("Please Enter Total Investment : \n")
            shares = portfolio.calculate_approximate_shares(allocation, investment)
            total = portfolio.calculate_actual_total(allocation, investment)
            self.line()

            self.title_line('Optimal Share Allocation')
            self.array_result('Optimal Portfolio Shares Allocation', shares, portfolio.tickers)
            self.title_line('Optimal Portfolio Value')
            self.scalar_result('Total', total)

        self.title_line('Risk-Return Profile')
        self.scalar_result('Return', portfolio.return_function(allocation))
        self.scalar_result('Volatility', portfolio.volatility_function(allocation))

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
        self.option(FUNC_DICT['efficient_frontier'], 'Generate a plot of the portfolio\'s efficient frontier for the supplied list of tickers. The number of points in the plot must be specified by the last argument.  \n')
        self.option(FUNC_DICT['help'], 'Print this help message. \n')
        self.option(FUNC_DICT['minimize_variance'], 'Minimize the variance of the portfolio defined by the supplied list of ticker symbols. \n')
        self.option(FUNC_DICT['maximize_return'], 'Maximize the return of the portfolio defined by the supplied list of ticker symbols. \n')
        self.option(FUNC_DICT['risk_return'], 'Calculate the risk-return profile for the supplied list of ticker symbols. \n')
        self.option(FUNC_DICT['optimize_portfolio'], 'Optimize the variance of the portfolio\'s variance subject to the supplied return target. The target return must be specified by the last argument. \n')   