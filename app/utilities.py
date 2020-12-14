import datetime, os, dotenv

APP_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BUFFER_DIR = os.path.join(APP_DIR, 'cache')
ENV = dotenv.load_dotenv(os.path.join(APP_DIR,'.env'))
QUERY_URL = os.getenv('AV_QUERY_URL')
ONE_TRADING_DAY=(1/252)
DEBUG=False
SEPARATER="-------------------------"
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
        print("      -", opt, " = ", explanation)

    def help(self):
        print('command -OPTION [tickers]')
        title_line('OPTIONS')
        option(FUNC_DICT['correlation'], 'Calculate pair-wise correlation for the supplied list of ticker symbols.')
        option(FUNC_DICT['help'], 'Print this help message.')
        option(FUNC_DICT['optimize'], 'Optimize the portfolio defined by the supplied list of ticker symbols.')
        option(FUNC_DICT['statistics'], 'Calculate the risk-return profile for the supplied list of ticker symbols.')
        
