import datetime, os, dotenv

APP_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BUFFER_DIR = os.path.join(APP_DIR, 'data')
ENV = dotenv.load_dotenv(os.path.join(APP_DIR,'.env'))
QUERY_URL = os.getenv('AV_QUERY_URL')
ONE_TRADING_DAY=(1/252)
DEBUG=True

class Logger():

    def __init__(self, location):
        self.location = location

    def log(self, msg):
        if DEBUG:
            now = datetime.datetime.now()
            print(now, ' :' , self.location, ' : ',msg)
