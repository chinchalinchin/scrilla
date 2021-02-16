import os, csv, json

import app.settings as settings
import app.markets as markets

import util.logger as logger
import util.helper as helper

# os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
CLOSE_PRICE = "close"
OPEN_PRICE = "open"
output = logger.Logger("app.services", settings.LOG_LEVEL)

# TODO: move services calls to services.py! 
def init_static_data():
    if settings.INIT or \
        ((not os.path.isfile(settings.STATIC_ECON_FILE)) or \
            (not os.path.isfile(settings.STATIC_TICKERS_FILE)) or \
                (not os.path.isfile(settings.STATIC_CRYPTO_FILE))):

        output.info('Initializing static data. Please wait. This may take a moment.')
        output.info('NOTE: set LOG_LEVEL = "debug" for more output while you wait.')

        # Clear static folder if initializing, otherwise unnecessary
        if settings.INIT:
            output.debug('Initialzing because settings.INIT set to True')
            helper.clear_directory(settings.STATIC_DIR, retain=True, outdated_only=False)
        
        else:
            output.debug('Initializing because settings.STATIC_DIR directory is missing file(s)')

        # Initialize Static Price Data
        if settings.PRICE_MANAGER == "alpha_vantage": 

            # grab ticker symbols and store in STATIC_DIR
            if not os.path.isfile(settings.STATIC_TICKERS_FILE):
                output.debug(f'Missing {settings.STATIC_TICKERS_FILE}, querying \'{settings.PRICE_MANAGER}\'')

                # TODO: services calls should be in services.py! need to put this and the helper method 
                #       into services.py in the future. 
                query=f'{settings.PARAM_AV_FUNC}={settings.ARG_AV_FUNC_EQUITY_LISTINGS}'
                url = f'{settings.AV_URL}?{query}&{settings.PARAM_AV_KEY}={settings.AV_KEY}'

                output.debug(f'Preparsing to parse \'{settings.PRICE_MANAGER}\' Response to query: {query}')
                helper.parse_csv_response_column(column=0, url=url, firstRowHeader=settings.AV_RES_EQUITY_KEY, 
                                                    savefile=settings.STATIC_TICKERS_FILE, filetype=settings.FILE_EXT)

            # grab crypto symbols and store in STATIC_DIR
            if not os.path.isfile(settings.STATIC_CRYPTO_FILE):
                output.debug(f'Missing {settings.STATIC_CRYPTO_FILE}, querying \'{settings.PRICE_MANAGER}\'.')
                url = settings.AV_CRYPTO_LIST

                output.debug(f'Preparsing to parse \'{settings.PRICE_MANAGER}\' Response to query: {query}')
                helper.parse_csv_response_column(column=0, url=url, firstRowHeader=settings.AV_RES_CRYPTO_KEY, 
                                                    savefile=settings.STATIC_CRYPTO_FILE, filetype=settings.FILE_EXT)

        else:
            output.info("No PRICE_MANAGER set in .env file!")

        # Initialize Static Statistic Data
        if settings.STAT_MANAGER == "quandl":
            
            # grab econominc indicator symbols and store in STATIC_DIR
            if not os.path.isfile(settings.STATIC_ECON_FILE):
                output.debug(f'Missing {settings.STATIC_ECON_FILE}, querying \'{settings.STAT_MANAGER}\'.')

                query = f'{settings.PATH_Q_FRED}/{settings.PARAM_Q_METADATA}'
                url = f'{settings.Q_META_URL}/{query}?{settings.PARAM_Q_KEY}={settings.Q_KEY}'

                output.debug(f'Preparsing to parse \'{settings.PRICE_MANAGER}\' Response to query: {query}')
                helper.parse_csv_response_column(column=0, url=url, firstRowHeader=settings.Q_RES_STAT_KEY,
                                                    savefile=settings.STATIC_ECON_FILE, filetype=settings.FILE_EXT,
                                                    zipped=settings.Q_RES_STAT_ZIP_KEY)

        else:
            output.info("No STAT_MANAGER set in .env file!")
    else:
        output.debug('Static data already initialized!')

def get_static_data(static_type):
    output.debug(f'Loading in cached {static_type} symbols.')
    path = None

    if static_type == settings.ASSET_CRYPTO:
        path = settings.STATIC_CRYPTO_FILE
    
    elif static_type == settings.ASSET_EQUITY:
        path = settings.STATIC_TICKERS_FILE
    
    elif static_type == settings.STAT_ECON:
        path = settings.STATIC_ECON_FILE
    
    else:
        return False

    if path is not None:
        if not os.path.isfile(path):
            init_static_data()

        with open(path, 'r') as infile:
            if settings.FILE_EXT == "json":
                symbols = json.load(infile)   
            # TODO: implement other file loading exts    
        return symbols
    else:
        return False

def get_watchlist():
    output.debug('Loading in Watchlist symbols.')

    if os.path.isfile(settings.COMMON_WATCHLIST_FILE):
        output.debug('Watchlist found.')
        with open(settings.COMMON_WATCHLIST_FILE, 'r') as infile:
            if settings.FILE_EXT =="json":
                watchlist = json.load(infile)
                output.debug('Watchlist loaded in JSON format.')

            # TODO: implement other file loading exts
    else: 
        output.info('Watchlist not found.')
        watchlist = []

    return watchlist

def add_watchlist(new_tickers):
    output.debug('Saving tickers to Watchlist')

    current_tickers = get_watchlist()
    all_tickers = get_static_data(settings.ASSET_EQUTY)

    for ticker in new_tickers:
        if ticker not in current_tickers and ticker in all_tickers:
            output.debug(f'New ticker being added to Watchlist: {ticker}')
            current_tickers.append(ticker)

    current_tickers = sorted(current_tickers)

    with open(settings.COMMON_WATCHLIST_FILE, 'w+') as outfile:
        if settings.FILE_EXT == "json":
            json.dump(current_tickers, outfile)
        # TODO: implement other file extensions