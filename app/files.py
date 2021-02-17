import os, io, json, datetime, csv, zipfile
import requests

import app.settings as settings

import util.outputter as outputter
import util.helper as helper

# os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
CLOSE_PRICE = "close"
OPEN_PRICE = "open"
logger = outputter.Logger("app.services", settings.LOG_LEVEL)

def parse_csv_response_column(column, url, firstRowHeader=None, savefile=None, filetype=None, zipped=None):
    """
    Parameters
    ----------
    column : int
        Required. Index of the column you wish to retrieve from the response.
    url : str
        Required. The url, already formatted with appropriate query and key, that will respond with the csv file, zipped or unzipped (see zipped argument for more info), you wish to parse.
    firstRowHeader : str
        Optional. name of the header for the column you wish to parse. if specified, the parsed response will ignore the row header. Do not include if you wish to have the row header in the return result.
    savefile : str
        Optional. the absolute path of the file you wish to save the parsed response column to.
    filetype : str
        Optional. determines the type of conversion that is applied to the response before it is saved. Currently, only supports 'json'.
    zipped : str
        if the response returns a zip file, this argument needs to be set equal to the file within the archive you wish to parse. 
    """
    col, big_mother = [], []

    with requests.Session() as s:
        download = s.get(url)
        
        if zipped is not None:
            zipdata = io.BytesIO(download.content)
            unzipped = zipfile.ZipFile(zipdata)
            with unzipped.open(zipped, 'r') as f:
                for line in f:
                    big_mother.append(helper.replace_troublesome_chars(line.decode("utf-8")))
                cr = csv.reader(big_mother, delimiter=',')
        
        else:
            decoded_content = download.content.decode('utf-8')
            cr = csv.reader(decoded_content.splitlines(), delimiter=',')

        s.close()
    
    for row in cr:
        if row[column] != firstRowHeader:
            col.append(row[column])

    if savefile is not None: 
        # TODO: Possibly infer file type extension from filename   
        with open(savefile, 'w') as outfile:
            if filetype == "json":
                json.dump(col, outfile)

    return col

def init_static_data():
    if ((not os.path.isfile(settings.STATIC_ECON_FILE)) or \
            (not os.path.isfile(settings.STATIC_TICKERS_FILE)) or \
                (not os.path.isfile(settings.STATIC_CRYPTO_FILE))):

        logger.info('Initializing static data. Please wait. This may take a moment.')
        logger.info('NOTE: set LOG_LEVEL = "debug" for more output while you wait.')
        

        # grab ticker symbols and store in STATIC_DIR
        if not os.path.isfile(settings.STATIC_TICKERS_FILE):
            if settings.PRICE_MANAGER == "alpha_vantage": 

                logger.debug(f'Missing {settings.STATIC_TICKERS_FILE}, querying \'{settings.PRICE_MANAGER}\'')

                # TODO: services calls should be in services.py! need to put this and the helper method 
                #       into services.py in the future. 
                query=f'{settings.PARAM_AV_FUNC}={settings.ARG_AV_FUNC_EQUITY_LISTINGS}'
                url = f'{settings.AV_URL}?{query}&{settings.PARAM_AV_KEY}={settings.AV_KEY}'

                logger.debug(f'Preparsing to parse \'{settings.PRICE_MANAGER}\' Response to query: {query}')
                helper.parse_csv_response_column(column=0, url=url, firstRowHeader=settings.AV_RES_EQUITY_KEY, 
                                                        savefile=settings.STATIC_TICKERS_FILE, filetype=settings.FILE_EXT)

            else:
                logger.info("No PRICE_MANAGER set in .env file!")

        # grab crypto symbols and store in STATIC_DIR
        if not os.path.isfile(settings.STATIC_CRYPTO_FILE):
            if settings.PRICE_MANAGER == "alpha_vantage": 
                logger.debug(f'Missing {settings.STATIC_CRYPTO_FILE}, querying \'{settings.PRICE_MANAGER}\'.')
                url = settings.AV_CRYPTO_LIST

                logger.debug(f'Preparsing to parse \'{settings.PRICE_MANAGER}\' Response to query: {query}')
                helper.parse_csv_response_column(column=0, url=url, firstRowHeader=settings.AV_RES_CRYPTO_KEY, 
                                                    savefile=settings.STATIC_CRYPTO_FILE, filetype=settings.FILE_EXT)
            else:
                logger.info("No PRICE_MANAGER set in .env file!")
            
        # grab econominc indicator symbols and store in STATIC_DIR
        if not os.path.isfile(settings.STATIC_ECON_FILE):
            if settings.STAT_MANAGER == "quandl":
                logger.debug(f'Missing {settings.STATIC_ECON_FILE}, querying \'{settings.STAT_MANAGER}\'.')

                query = f'{settings.PATH_Q_FRED}/{settings.PARAM_Q_METADATA}'
                url = f'{settings.Q_META_URL}/{query}?{settings.PARAM_Q_KEY}={settings.Q_KEY}'

                logger.debug(f'Preparsing to parse \'{settings.PRICE_MANAGER}\' Response to query: {query}')
                helper.parse_csv_response_column(column=0, url=url, firstRowHeader=settings.Q_RES_STAT_KEY,
                                                    savefile=settings.STATIC_ECON_FILE, filetype=settings.FILE_EXT,
                                                    zipped=settings.Q_RES_STAT_ZIP_KEY)

            else:
                logger.info("No STAT_MANAGER set in .env file!")
    else:
        logger.debug('Static data already initialized!')

def get_static_data(static_type):
    logger.debug(f'Loading in cached {static_type} symbols.')
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
    logger.debug('Loading in Watchlist symbols.')

    if os.path.isfile(settings.COMMON_WATCHLIST_FILE):
        logger.debug('Watchlist found.')
        with open(settings.COMMON_WATCHLIST_FILE, 'r') as infile:
            if settings.FILE_EXT =="json":
                watchlist = json.load(infile)
                logger.debug('Watchlist loaded in JSON format.')

            # TODO: implement other file loading exts
    else: 
        logger.info('Watchlist not found.')
        watchlist = []

    return watchlist

def add_watchlist(new_tickers):
    logger.debug('Saving tickers to Watchlist')

    current_tickers = get_watchlist()
    all_tickers = get_static_data(settings.ASSET_EQUTY)

    for ticker in new_tickers:
        if ticker not in current_tickers and ticker in all_tickers:
            logger.debug(f'New ticker being added to Watchlist: {ticker}')
            current_tickers.append(ticker)

    current_tickers = sorted(current_tickers)

    with open(settings.COMMON_WATCHLIST_FILE, 'w+') as outfile:
        if settings.FILE_EXT == "json":
            json.dump(current_tickers, outfile)
        # TODO: implement other file extensions

 
################################################
##### FILE MANAGEMENT FUNCTIONS

# TODO: this deletes subdirectories.
# retain: keeps .gitkeep in directory
# outdated_only: only deletes files with a timestamp != today
def clear_directory(directory, retain=True, outdated_only=False):
    filelist = list(os.listdir(directory))

    if outdated_only:
        now = datetime.datetime.now()
        timestamp = '{}{}{}'.format(now.month, now.day, now.year)
        if retain:
            for f in filelist:
                filename = os.path.basename(f)
                if filename != ".gitkeep" and timestamp not in filename:
                    os.remove(os.path.join(directory, f))
        else:
            for f in filelist:
                filename = os.path.basename(f)
                if timestamp not in filename:
                    os.remove(os.path.join(directory, f))

    else:
        if retain:
            for f in filelist:
                filename = os.path.basename(f)
                if filename != ".gitkeep":
                    os.remove(os.path.join(directory, f))
        else:
            for f in filelist:
                os.remove(os.path.join(directory, f))

def is_non_zero_file(fpath):  
    return os.path.isfile(fpath) and os.path.getsize(fpath) > 0