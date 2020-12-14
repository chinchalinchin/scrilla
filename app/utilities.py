import datetime, os, dotenv

APP_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

dotenv.load_dotenv(os.path.join(APP_DIR,'.env'))

BUFFER_DIR = os.path.join(APP_DIR, 'cache')

QUERY_URL = os.getenv('AV_QUERY_URL')

ONE_TRADING_DAY=(1/252)

DEBUG=False

SEPARATER="--------------------------------------------------"

FUNC_DICT={
    "optimize": "-o",
    "statistics" : "-s",
    "correlation":"-c",
    "help": "-h"
}

class Logger():

    def __init__(self, location):
        self.location = location

    def debug(self, msg):
        if DEBUG:
            now = datetime.datetime.now()
            dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
            print(dt_string, ' :' , self.location, ' : ',msg)

    def log(self, calculation, result):
        now = datetime.datetime.now()
        dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
        print(dt_string, 'pyfin >> ', calculation, ' = ', round(result, 4))

    def title_line(self, title):
        print(SEPARATER, title, SEPARATER) 

    def option(self, opt, explanation):
        print("      ", opt, " = ", explanation)

    def help(self):
        self.title_line('PYNANCE')
        line_1 = 'A financial application written in python to determine optimal portfolio allocations,'
        line_2 = 'in addition to calculating fundamental equity statistics.'
        side_buffer_1 = len(line_1)
        side_buffer_2 = len(line_2)
        print(' '*(len(SEPARATER)-int(side_buffer_1/2)), line_1, ' '*(len(SEPARATER)-int(side_buffer_1/2)))
        print(' '*(len(SEPARATER)-int(side_buffer_2/2)), line_2, ' '*(len(SEPARATER)-int(side_buffer_2/2)))
        print()

        self.title_line('SYNTAX')
        line_3 = 'command -OPTION [tickers]'
        side_buffer = len(line_3)
        print(' '*(len(SEPARATER) - int(side_buffer/2)), line_3, ' '*(len(SEPARATER) - int(side_buffer/2)))
        print()
        
        self.title_line('OPTIONS')
        self.option(FUNC_DICT['correlation'], 'Calculate pair-wise correlation for the supplied list of ticker symbols.')
        self.option(FUNC_DICT['help'], 'Print this help message.')
        self.option(FUNC_DICT['optimize'], 'Optimize the portfolio defined by the supplied list of ticker symbols.')
        self.option(FUNC_DICT['statistics'], 'Calculate the risk-return profile for the supplied list of ticker symbols.')
        
