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
        self.logger.info("# Application Configuration")
        self.logger.info('> Production Url: %s', config.PRODUCTION_URL)
        self.logger.info('> Maintainer: %s', config.MAINTAINER)
        self.logger.info('> Version: %s', config.VERSION)
        self.logger.info("-------------------------------------------------")
        self.logger.info("# Environment Configuration")
        self.logger.info("> Directory Location : %s", config.BASE_DIR)
        self.logger.info('> Debug : %s', config.DEBUG)
        self.logger.info('> Development Mode: %s', config.DEVELOPMENT_MODE)
        self.logger.info('> Enviroment: %s', config.APP_ENV)
        self.logger.info("-------------------------------------------------")
        self.logger.info("# Database Configuration")
        self.logger.info('> Database Host: %s', config.db_creds['host'])
        self.logger.info('> Database Name: %s', config.db_creds['db_name'])
        self.logger.info('> Database Username: %s', config.db_creds['username'])
        self.logger.info("-------------------------------------------------")
        self.logger.info("# AWS S3 Configuration")
        self.logger.info('> AWS Bucket Name: %s', config.aws_creds['bucket'])
        self.logger.info('> AWS Region: %s', config.aws_creds['region'])
        self.logger.info("-------------------------------------------------")
        if not (config.APP_ENV == 'mcaas' or config.APP_ENV == 'local_mcaas'):
            self.logger.info("# UAA OAuth2 Configuration")
            self.logger.info('> UAA Authorization URLL: %s', config.UAA_AUTH_URL)
            self.logger.info('> UAA Token URL: %s', config.UAA_TOKEN_URL)
            self.logger.info('> UAA Login Redirect URL: %s', config.LOGIN_REDIRECT_URL)
        else: 
            self.logger.info("# Auth Configuration")
            self.logger.info('> Login Redirect URL: %s', config.LOGIN_REDIRECT_URL)

        self.logger.info("-------------------------------------------------")
        self.logger.info("# Email Configuration")
        self.logger.info("> Email Host: %s", config.EMAIL_HOST)
        self.logger.info("> Email Host User: %s", config.EMAIL_HOST_USER)
        self.logger.info("-------------------------------------------------")
        self.logger.info("# Miscellanous Configuration")
        self.logger.info('> CSRF Header Name: %s', config.CSRF_HEADER_NAME)
        for folder in config.STATICFILES_DIR:  
            self.logger.info('> Static Files Directory: %s', folder)
        self.logger.info("-------------------------------------------------")

if __name__ == "__main__":
    logger = DebugLogger("debug.py")
    logger.log_config()