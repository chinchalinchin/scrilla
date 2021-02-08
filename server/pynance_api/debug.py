import logging
from core import settings as config

class DebugLogger():

    def __init__(self, location_name):
        self.logger = self.init_logger(location_name)

    def init_logger(self, location_name):
        this_logger = logging.getLogger(location_name)
        this_logger.setLevel(logging.INFO)
        ch = logging.StreamHandler()
        format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        ch.setLevel(logging.INFO)
        ch.setFormatter(format)
        this_logger.addHandler(ch)
        return this_logger

    def get_logger(self):
        return self.logger
        
    def log_config(self):
        self.logger.info("-------------------------------------------------")
        self.logger.info('SETTINGS.PY Configuration')
        self.logger.info("-------------------------------------------------")
        self.logger.info("# Environment Configuration")
        self.logger.info("> Directory Location : %s", config.BASE_DIR)
        self.logger.info('> Debug : %s', config.DEBUG)
        self.logger.info('> Verbose: %s', config.VERBOSE)
        self.logger.info('> Enviroment: %s', config.APP_ENV)
        self.logger.info("-------------------------------------------------")
        self.logger.info("# Database Configuration")
        self.logger.info('> Database Engine: %s', config.DATABASES['default']['ENGINE'])
        self.logger.info("-------------------------------------------------")

if __name__ == "__main__":
    logger = DebugLogger("debug.py")
    logger.log_config()