"""
Description
-----------
`app.files` is in charge of all application file handling. In addition, this module handles requests for large csv files retrieved from external services. The metadata files from 'AlphaVantage' and 'Quandl' are returned as zipped csv files. The functions within in this module perform all the tasks necessary for parsing this response into the application file system, whether on the localhost or a containerized filesytem.
"""
import os, io, json, datetime, csv, zipfile
import requests

import app.settings as settings

import util.outputter as outputter
import util.helper as helper

# os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
CLOSE_PRICE = "close"
OPEN_PRICE = "open"

logger = outputter.Logger("app.services", settings.LOG_LEVEL)

def load_file(file_name):
    with open(file_name, 'r') as infile:
        if settings.FILE_EXT == "json":
            prices = json.load(infile)
        return prices
        # TODO: implement other file loading extensions

def save_file(file_to_save, file_name):
    with open(file_name, 'w') as outfile:
        if settings.FILE_EXT == "json":
            json.dump(file_to_save, outfile)
        # TODO: implement other file saving extensions.

def parse_csv_response_column(column, url, firstRowHeader=None, savefile=None, zipped=None):
    """
    Parameters
    ----------
    1. column : int \n
        Required. Index of the column you wish to retrieve from the response. \n \n
    2. url : str \n
        Required. The url, already formatted with appropriate query and key, that will respond with the csv file, zipped or unzipped (see zipped argument for more info), you wish to parse. \n \n 
    3. firstRowHeader : str \n 
        Optional. name of the header for the column you wish to parse. if specified, the parsed response will ignore the row header. Do not include if you wish to have the row header in the return result. \n \n 
    4. savefile : str \n 
        Optional. the absolute path of the file you wish to save the parsed response column to. \n \n 
    5. zipped : str \n 
        if the response returns a zip file, this argument needs to be set equal to the file within the zipped archive you wish to parse. \n \n 
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
            if settings.FILE_EXT == "json":
                json.dump(col, outfile)

    return col

def init_static_data():
    """
    Description
    -----------
    Initializes the three static files defined in app.settings: `STATIC_TICKERS_FILE`, `STATIC_CRYPTO_FILE` and `STATIC_ECON_FILE`. The data for these files is retrieved from the service managers. While this function blurs the lines between file management and service management, the function has been included in the `files.py` module rather than the `services.py` module due the unique response types of static metadata. All metadata is returned a csv or zipped csvs. These responses require specialized functions. Moreover, these files should only be initialized the first time the application executes. Subsequent executions will refer to their cached versions residing in the local or containerized filesytems. 
    """
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
                                                        savefile=settings.STATIC_TICKERS_FILE)

            else:
                logger.info("No PRICE_MANAGER set in .env file!")

        # grab crypto symbols and store in STATIC_DIR
        if not os.path.isfile(settings.STATIC_CRYPTO_FILE):
            if settings.PRICE_MANAGER == "alpha_vantage": 
                logger.debug(f'Missing {settings.STATIC_CRYPTO_FILE}, querying \'{settings.PRICE_MANAGER}\'.')
                url = settings.AV_CRYPTO_LIST

                logger.debug(f'Preparsing to parse \'{settings.PRICE_MANAGER}\' Response to query: {query}')
                helper.parse_csv_response_column(column=0, url=url, firstRowHeader=settings.AV_RES_CRYPTO_KEY, 
                                                    savefile=settings.STATIC_CRYPTO_FILE)
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
                                                    savefile=settings.STATIC_ECON_FILE, zipped=settings.Q_RES_STAT_ZIP_KEY)

            else:
                logger.info("No STAT_MANAGER set in .env file!")
    else:
        logger.debug('Static data already initialized!')

def get_static_data(static_type):
    """
    Description
    ----------- 
    Retrieves static data cached in the local or containerized file system. \n \n 

    Parameters
    ----------
    1. `static_type` : str \n
    A string corresponding to the type of static data to be retrieved. The types can be statically accessed through the `app.settings` variables: ASSET_CRYPTO, ASSET_EQUITY and STAT_ECON. \n \n
    """
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
        
    return False

def get_watchlist():
    """
    Description
    -----------
    Retrieves the list of watchlisted equity ticker symbols saved in /data/common/watchlist.json.
    """
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
    """
    Description
    -----------
    Retrieves the list of watchlisted equity ticker symbols saved in /data/common/watchlist.json and then appends to it the list of tickers supplied as arguments. After appending, the list is sorted in alphabetical order. The tickers to add must exist in the /data/static/tickers.json file in order to be added to the watchlist, i.e. the tickers must have price histories that can be retrieved (the static file tickers.json contains a list of all equities with retrievable price histories.) \n \n 
    """
    logger.debug('Saving tickers to Watchlist')

    current_tickers = get_watchlist()
    all_tickers = get_static_data(settings.ASSET_EQUITY)

    for ticker in new_tickers:
        if ticker not in current_tickers and ticker in all_tickers:
            logger.debug(f'New ticker being added to Watchlist: {ticker}')
            current_tickers.append(ticker)

    current_tickers = sorted(current_tickers)

    with open(settings.COMMON_WATCHLIST_FILE, 'w+') as outfile:
        if settings.FILE_EXT == "json":
            json.dump(current_tickers, outfile)
        # TODO: implement other file extensions

def save_frontier(portfolio, frontier, file_name):
    save_format = {}
    for i in range(len(frontier)):
        allocation_format = {}
        for j in range(len(portfolio.tickers)):
            allocation_format[f'{portfolio.tickers[j]}_allocation'] = frontier[i][j] 
        save_format[f'portfolio_{i}'] = allocation_format
    
    save_file(file_to_save=save_format, file_name=file_name)

def save_profile(profile, ticker, save_file):
    # TODO:
    pass

def save_allocation(allocation, ticker, save_file):
    # TODO: 
    pass

################################################
##### FILE MANAGEMENT FUNCTIONS

# TODO: this deletes subdirectories.
# retain: keeps .gitkeep in directory
# outdated_only: only deletes files with a timestamp != today
def clear_directory(directory, retain=True, outdated_only=False):
    """
    Description
    -----------
    Wipes a directory of files without deleting the directory itself. \n \n 

    Parameters
    ----------
    1. directory: str \n
    Path of the directory to be cleaned. \n \n 

    2. retain : bool \n
    If set to True, the method will skip files named '.gitkeep' within the directory, i.e. version control configuration files. 

    3. outdated_only: bool \b 
    If set to True, the method will check for a time stamp on files with the format 'DD-MM-YYYY' and retain files that contain this timestamp.
    """
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