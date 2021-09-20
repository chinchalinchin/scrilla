# This file is part of scrilla: https://github.com/chinchalinchin/scrilla.

# scrilla is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 3
# as published by the Free Software Foundation.

# scrilla is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with scrilla.  If not, see <https://www.gnu.org/licenses/>
# or <https://github.com/chinchalinchin/scrilla/blob/develop/main/LICENSE>.


"""
` files` is in charge of all application file handling. In addition, this module handles requests for large csv files retrieved from external services. The metadata files from 'AlphaVantage' and 'Quandl' are returned as zipped csv files. The functions within in this module perform all the tasks necessary for parsing this response for the application.
"""
import os, io, json, csv, zipfile
from typing import Any
import requests

from scrilla import settings, static, errors
from scrilla.util import outputter, helper, formatter 
import scrilla.util.helper as helper

logger = outputter.Logger("files", settings.LOG_LEVEL)

static_tickers_blob, static_econ_blob, static_crypto_blob = None, None, None

def load_file(file_name: str) -> Any:
    with open(file_name, 'r') as infile:
        if settings.FILE_EXT == "json":
            file = json.load(infile)
        return file
        # TODO: implement other file loading extensions

def save_file(file_to_save: Any, file_name: str) -> bool:
    with open(file_name, 'w') as outfile:
        if settings.FILE_EXT == "json":
            try:
                json.dump(file_to_save, outfile)
                return True
            except Exception as e:
                logger.debug(f'A {e.__class__} exception occured.')
                return False
            
        # TODO: implement other file saving extensions.

def set_credentials(value: str, which_key: str) -> bool:
    file_name = os.path.join(settings.COMMON_DIR, f'{which_key}.{settings.FILE_EXT}')
    return save_file(file_to_save=value, file_name=file_name)

def get_credentials(which_key: str) -> str:
    file_name = os.path.join(settings.COMMON_DIR, f'{which_key}.{settings.FILE_EXT}')
    return load_file(file_name = file_name)

def parse_csv_response_column(column: int, url: str, firstRowHeader: str=None, savefile: str=None, zipped: str=None):
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
    Initializes the three static files defined in  settings: `STATIC_TICKERS_FILE`, `STATIC_CRYPTO_FILE` and `STATIC_ECON_FILE`. The data for these files is retrieved from the service managers. While this function blurs the lines between file management and service management, the function has been included in the `files.py` module rather than the `services.py` module due the unique response types of static metadata. All metadata is returned as a csv or zipped csvs. These responses require specialized functions. Moreover, these files should only be initialized the first time the application executes. Subsequent executions will refer to their cached versions residing in the local filesytems. 

    Raises
    ------
    1. errors.ConfigurationError \n
        If `scrilla.settings.PRICE_MANAGER` and `scrilla.settings.STAT_MANAGER` are not configured through the environment variables `PRICE_MANAGER` and `STAT_MANAGER`, the function will throw this error.
    """
    global static_tickers_blob
    global static_econ_blob
    global static_crypto_blob

    if ((not os.path.isfile(settings.STATIC_ECON_FILE)) or \
            (not os.path.isfile(settings.STATIC_TICKERS_FILE)) or \
                (not os.path.isfile(settings.STATIC_CRYPTO_FILE))):

        logger.info('Initializing static data. Please wait. This may take a moment...')

        # grab ticker symbols and store in STATIC_DIR
        if not os.path.isfile(settings.STATIC_TICKERS_FILE):
            if settings.PRICE_MANAGER == "alpha_vantage": 
                service_map = static.keys["SERVICES"]["PRICES"]["ALPHA_VANTAGE"]["MAP"]
                logger.debug(f'Missing {settings.STATIC_TICKERS_FILE}, querying \'{settings.PRICE_MANAGER}\'')

                # TODO: services calls should be in services.py! need to put this and the helper method 
                #       into services.py in the future. 
                query=f'{settings.PARAM_AV_FUNC}={settings.ARG_AV_FUNC_EQUITY_LISTINGS}'
                url = f'{settings.AV_URL}?{query}&{settings.PARAM_AV_KEY}={settings.AV_KEY}'
                static_tickers_blob = parse_csv_response_column(column=0, url=url, savefile=settings.STATIC_TICKERS_FILE,
                                                                    firstRowHeader=service_map['KEYS']['EQUITY']['HEADER'])

            raise errors.ConfigurationError("No PRICE_MANAGER set in .env file!")

        # grab crypto symbols and store in STATIC_DIR
        if not os.path.isfile(settings.STATIC_CRYPTO_FILE):
            if settings.PRICE_MANAGER == "alpha_vantage": 
                service_map = static.keys["SERVICES"]["PRICES"]["ALPHA_VANTAGE"]["MAP"]
                logger.debug(f'Missing {settings.STATIC_CRYPTO_FILE}, querying \'{settings.PRICE_MANAGER}\'.')
                url = settings.AV_CRYPTO_LIST
                static_crypto_blob = parse_csv_response_column(column=0, url=url, savefile=settings.STATIC_CRYPTO_FILE,
                                                                firstRowHeader=service_map['KEYS']['CRYPTO']['HEADER'])
            raise errors.ConfigurationError("No PRICE_MANAGER set in .env file!")
            
        # grab econominc indicator symbols and store in STATIC_DIR
        if not os.path.isfile(settings.STATIC_ECON_FILE):
            if settings.STAT_MANAGER == "quandl":
                service_map = static.keys["SERVICES"]["STATISTICS"]["QUANDL"]["MAP"]

                logger.debug(f'Missing {settings.STATIC_ECON_FILE}, querying \'{settings.STAT_MANAGER}\'.')

                query = f'{service_map["PATHS"]["FRED"]}/{service_map["PARAMS"]["METADATA"]}'
                url = f'{settings.Q_META_URL}/{query}?{service_map["PARAMS"]["KEY"]}={settings.Q_KEY}'
                static_econ_blob = parse_csv_response_column(column=0, url=url, savefile=settings.STATIC_ECON_FILE,
                                                            firstRowHeader=service_map["KEYS"]["HEADER"],
                                                             zipped=service_map["KEYS"]["ZIPFILE"])

            raise errors.ConfigurationError("No STAT_MANAGER set in .env file!")

    else:
        logger.debug('Static data already initialized!')

def get_static_data(static_type):
    """
    Retrieves static data cached in the local or containerized file system. \n \n 

    Parameters
    ----------
    1. `static_type` : str \n
    A string corresponding to the type of static data to be retrieved. The types can be statically accessed through the ` settings` variables: ASSET_CRYPTO, ASSET_EQUITY and STAT_ECON. \n \n
    """
    path, blob = None, None
    global static_crypto_blob 
    global static_econ_blob 
    global static_tickers_blob

    if static_type == static.keys['ASSETS']['CRYPTO']:
        if static_crypto_blob is not None:
            blob = static_crypto_blob
        else:
            path = settings.STATIC_CRYPTO_FILE
    
    elif static_type == static.keys['ASSETS']['EQUITY']:
        if static_tickers_blob:
            blob = static_tickers_blob
        else:
            path = settings.STATIC_TICKERS_FILE
    
    elif static_type == static.keys['ASSETS']['STAT']:
        if static_econ_blob:
            blob = static_econ_blob
        else:
            path = settings.STATIC_ECON_FILE
    
    else:
        return None

    if blob is not None:
        logger.debug(f'Found in-memory {static_type} symbols.')
        return blob

    if path is not None:
        if not os.path.isfile(path):
            init_static_data()

        logger.debug(f'Loading in cached {static_type} symbols.')
        with open(path, 'r') as infile:
            if settings.FILE_EXT == "json":
                symbols = json.load(infile)
            # TODO: implement other file loading exts 
               
        if static_type == static.keys['ASSETS']['CRYPTO']:
            static_crypto_blob = symbols
        elif static_type == static.keys['ASSETS']['EQUITY']:
            static_tickers_blob = symbols
        elif static_type == static.keys['ASSETS']['STAT']:
            static_econ_blob = symbols
        return symbols
        
    return None
    
# NOTE: output from get_overlapping_symbols:
# OVERLAP = ['ABT', 'AC', 'ADT', 'ADX', 'AE', 'AGI', 'AI', 'AIR', 'AMP', 'AVT', 'BCC', 'BCD', 'BCH', 'BCX', 'BDL', 'BFT', 'BIS', 'BLK', 'BQ', 'BRX', 
# 'BTA', 'BTG', 'CAT', 'CMP', 'CMT', 'CNX', 'CTR', 'CURE', 'DAR', 'DASH', 'DBC', 'DCT', 'DDF', 'DFS', 'DTB', 'DYN', 'EBTC', 'ECC', 'EFL', 'ELA', 'ELF',
# 'EMB', 'ENG', 'ENJ', 'EOS', 'EOT', 'EQT', 'ERC', 'ETH', 'ETN', 'EVX', 'EXP', 'FCT', 'FLO', 'FLT', 'FTC', 'FUN', 'GAM', 'GBX', 'GEO', 'GLD', 'GNT', 
# 'GRC', 'GTO', 'INF', 'INS', 'INT', 'IXC', 'KIN', 'LBC', 'LEND', 'LTC', 'MAX', 'MCO', 'MEC', 'MED', 'MGC', 'MINT', 'MLN', 'MNE', 'MOD', 'MSP', 'MTH', 
# 'MTN', 'MUE', 'NAV', 'NEO', 'NEOS', 'NET', 'NMR', 'NOBL', 'NXC', 'OCN', 'OPT', 'PBT', 'PING', 'PPC', 'PPT', 'PRG', 'PRO', 'PST', 'PTC', 'QLC', 'QTUM',
# 'R', 'RDN', 'REC', 'RVT', 'SALT', 'SAN', 'SC', 'SKY', 'SLS', 'SPR', 'SNX', 'STK', 'STX', 'SUB', 'SWT', 'THC', 'TKR', 'TRC', 'TRST', 'TRUE', 'TRX', 
# 'TX', 'UNB', 'VERI', 'VIVO', 'VOX', 'VPN', 'VRM', 'VRS', 'VSL', 'VTC', 'VTR', 'WDC', 'WGO', 'WTT', 'XEL', 'NEM', 'ZEN']

# TODO: need some way to distinguish between overlap.

def get_overlapping_symbols(equities=None, cryptos=None):
    """
    Returns an array of symbols which are contained in both the STATIC_TICKERS_FILE and STATIC_CRYPTO_FILE, i.e. ticker symbols which have both a tradeable equtiy and a tradeable crypto asset. 
    """
    if equities is None:
        equities = list(get_static_data(static.keys['ASSETS']['EQUITY']))
    if cryptos is None:
        cryptos = list(get_static_data(static.keys['ASSETS']['CRYPTO']))
    overlap = []
    for crypto in cryptos:
        if crypto in equities:
            overlap.append(crypto)
    return overlap

def get_asset_type(symbol : str) -> str:
    """"
    Returns the asset type of the supplied ticker symbol. \n \n

    Output
    ------
    ``str``. Represents the type of asset of the symbol. Types are statically accessible through the `scrilla.static.keys['ASSETS]` dictionary. \n \n 
    """
    symbols = list(get_static_data(static.keys['ASSETS']['CRYPTO']))
    overlap = get_overlapping_symbols(cryptos=symbols)

    if symbol not in overlap:
        if symbol in symbols:
            return static.keys['ASSETS']['CRYPTO']
            
                # if other asset types are introduced, then uncomment these lines
                # and add new asset type to conditional. Keep in mind the static
                # equity data is HUGE.
        # symbols = list(get_static_data(static.keys['ASSETS']['EQUITY']))
        # if symbol in symbols:
            # return static.keys['ASSETS']['EQUITY']
        #return None
        return static.keys['ASSETS']['EQUITY']
    # default to equity for overlap until a better method is determined. 
    return static.keys['ASSETS']['EQUITY']
    
def get_watchlist() -> list:
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

def add_watchlist(new_tickers: list) -> None:
    """
    Description
    -----------
    Retrieves the list of watchlisted equity ticker symbols saved in /data/common/watchlist.json and then appends to it the list of tickers supplied as arguments. After appending, the list is sorted in alphabetical order. The tickers to add must exist in the /data/static/tickers.json file in order to be added to the watchlist, i.e. the tickers must have price histories that can be retrieved (the static file tickers.json contains a list of all equities with retrievable price histories.) \n \n 
    """
    logger.debug('Saving tickers to Watchlist')

    current_tickers = get_watchlist()
    all_tickers = get_static_data(static.keys['ASSETS']['EQUITY'])

    for ticker in new_tickers:
        if ticker not in current_tickers and ticker in all_tickers:
            logger.debug(f'New ticker being added to Watchlist: {ticker}')
            current_tickers.append(ticker)

    current_tickers = sorted(current_tickers)

    with open(settings.COMMON_WATCHLIST_FILE, 'w+') as outfile:
        if settings.FILE_EXT == "json":
            json.dump(current_tickers, outfile)
        # TODO: implement other file extensions
    
def save_profiles(profiles: dict, file_name: str):
    save_format = formatter.format_profiles(profiles)
    save_file(file_to_save=save_format, file_name=file_name)

def save_allocation(allocation, portfolio, file_name, investment=None):
    save_format = formatter.format_allocation(allocation=allocation, portfolio=portfolio, investment=investment)
    save_file(file_to_save=save_format, file_name=file_name)

def save_frontier(portfolio, frontier, file_name, investment=None):
    save_format = formatter.format_frontier(portfolio=portfolio, frontier=frontier,investment=investment)
    save_file(file_to_save=save_format, file_name=file_name)

def save_moving_averages(tickers, averages_output, file_name):
    save_format = formatter.format_moving_averages(tickers=tickers,averages_output=averages_output)
    save_file(file_to_save=save_format, file_name=file_name)

def save_correlation_matrix(tickers, correlation_matrix, file_name):
    save_format = formatter.format_correlation_matrix(tickers=tickers, correlation_matrix=correlation_matrix)
    save_file(file_to_save=save_format, file_name=file_name)
    
################################################
##### FILE MANAGEMENT FUNCTIONS

# TODO: this deletes subdirectories.
# retain: keeps .gitkeep in directory
def clear_directory(directory, retain=True):
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

    for f in filelist:
        filename = os.path.basename(f)
        if retain and filename == static.constants['KEEP_FILE']:
            continue
        os.remove(os.path.join(directory, f))

def is_non_zero_file(fpath):  
    return os.path.isfile(fpath) and os.path.getsize(fpath) > 0