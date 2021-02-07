import datetime, os, io, json, csv, zipfile
import holidays
import requests

import util.formatting as formatter

################################################
##### FORMATTING FUNCTIONS

def get_number_input(msg_prompt) -> str:
    while True:
        user_input = input(msg_prompt)
        if user_input.isnumeric():
            return user_input
        else:
            print('Input Not Understood. Please Enter A Numerical Value.')
    
def strip_string_array(array) -> [str]:
    new_array = []
    for string in array:
        new_array.append(string.strip())
    return new_array

################################################
##### DATE FUNCTIONS

# YYYY-MM-DD
def parse_date_string(date_string) -> datetime.date:
    parsed = str(date_string).split('-')
    date = datetime.date(year=int(parsed[0]), month=int(parsed[1]), day=int(parsed[2]))
    return date

def date_to_string(date) -> str:
    year, month, day = date.year, date.month, date.day
    if month<10:
        month_string = "0"+str(month)
    else:
        month_string = str(month)
    if day<10:
        day_string = "0"+str(day)
    else:
        day_string = str(day)
    return f'{date.year}-{month_string}-{day_string}'

def format_date_range(start_date, end_date):
    result = ""
    if start_date is not None:
        start_string = date_to_string(start_date)
        result += f'From {start_string}'
    if end_date is not None:
        end_string = date_to_string(end_date)
        result += f' Until {end_string}'
    return result

def is_date_weekend(date) -> bool:
    if date.weekday() in [5, 6]:
        return True
    else:
        return False

# YYYY-MM-DD
def is_date_string_weekend(date_string) -> bool:
    return is_date_weekend(parse_date_string(date_string))

# YYYY-MM-DD
def is_date_string_holiday(date_string) -> bool:
    us_holidays = holidays.UnitedStates()
    return (date_string in us_holidays)

def is_date_holiday(date) -> bool:
    return is_date_string_holiday(date_to_string(date))

# YYYY-MM-DD
def get_holidays_between(start_date_string, end_date_string) -> int:
    us_holidays = holidays.UnitedStates()
    return len(us_holidays[start_date_string: end_date_string])

# YYYY-MM-DD
def consecutive_trading_days(start_date_string, end_date_string) -> bool:
    """
    Parameters
    ----------
    start_date_string : str
        Required. The start date of the time period under consideration. Must be formatted "YYYY-MM-DD"
    end_date_string : str
        Required. The end date of the time period under consideration. Must be formatted "YYYY-MM-DD"
    
    Returns 
    -------
    True
        if start_date_string and end_date_string are consecutive trading days, i.e. Tuesday -> Wednesday or Friday -> Monday,
        or Tuesday -> Thursday where Wednesday is a Holiday.
    False
        if start_date_string and end_date_string are NOT consecutive trading days.
    """
    if is_date_string_weekend(start_date_string) or is_date_string_weekend(end_date_string):
        return False

    start_date = parse_date_string(start_date_string)
    end_date = parse_date_string(end_date_string)
    delta = end_date - start_date

    if delta.days < 0:
        buffer = start_date
        start_date = end_date
        end_date = buffer
        delta = end_date - start_date

    holiday_count = get_holidays_between(start_date_string=start_date_string, end_date_string=end_date_string)

    if (delta.days - holiday_count) == 0:
        return False

    elif (delta.days - holiday_count) == 1:
        return True

    elif ((delta.days - holiday_count) > 1 and (delta.days - holiday_count) < 4):
        start_week, end_week = start_date.isocalendar()[1], end_date.isocalendar()[1]

        if start_week == end_week:
            return False

        else:
            return True

    else:
        return False

def dates_between(start_date, end_date):
    return [start_date + datetime.timedelta(x + 1) for x in range((end_date - start_date).days)]

def days_between(start_date, end_date):
    return (end_date - start_date).days

def business_dates_between(start_date, end_date):
    dates = []
    for x in range((end_date - start_date).days):
        this_date = start_date + datetime.timedelta(x+1)
        if not (is_date_weekend(this_date) or is_date_holiday(this_date)):
            dates.append(this_date)
    return dates

def business_days_between(start_date, end_date):
    dates = dates_between(start_date, end_date)
    return len([1 for day in dates if day.weekday() < 5])

def weekends_between(start_date, end_date):
    dates = dates_between(start_date, end_date)
    return len([1 for day in dates if day.weekday() > 4])

def decrement_date_by_business_days(start_date, business_days):
    days_to_subtract = business_days
    while days_to_subtract > 0:
        if not (is_date_weekend(start_date) or is_date_holiday(start_date)):
            days_to_subtract -= 1
        start_date -= datetime.timedelta(days=1)
    return start_date

def decrement_date_string_by_business_days(start_date_string, business_days):
    start_date = parse_date_string(start_date_string)
    return date_to_string(decrement_date_by_business_days(start_date, business_days))

def increment_date_by_business_days(start_date, business_days):
    days_to_add = business_days
    while days_to_add > 0:
        if not (is_date_weekend(start_date) or is_date_holiday(start_date)):
            days_to_add -= 1
        start_date += datetime.timedelta(days=1)
    return start_date

def increment_date_string_by_business_days(start_date_string, business_days):
    start_date = parse_date_string(start_date_string)
    return date_to_string(increment_date_by_business_days(start_date, business_days))

def get_next_business_day(date):
    while is_date_weekend(date) or is_date_holiday(date):
        date += datetime.timedelta(days=1)
    return date

def get_previous_business_day(date):
    while is_date_weekend(date) or is_date_holiday(date):
        date -= datetime.timedelta(days=1)
    return date
    
################################################
##### PARSING FUNCTIONS

def separate_args(args):
    extra_args, extra_values= [], []
    reduced_args = args
    offset = 0
    
    for arg in args:
        if arg in formatter.FUNC_XTRA_ARGS_DICT.values():
            extra_args.append(arg)
            extra_values.append(args[args.index(arg)+1])

    for arg in extra_args:
        reduced_args.remove(arg)

    for arg in extra_values:
        reduced_args.remove(arg)

    return (extra_args, extra_values, reduced_args)

def get_start_date(xtra_args, xtra_values):
    if formatter.FUNC_XTRA_ARGS_DICT['start_date'] in xtra_args:
        unparsed_start = xtra_values[xtra_args.index(formatter.FUNC_XTRA_ARGS_DICT['start_date'])]
        start_date = parse_date_string(unparsed_start)
    else:
        start_date = None
    return start_date

def get_end_date(xtra_args, xtra_values):
    if formatter.FUNC_XTRA_ARGS_DICT['end_date'] in xtra_args:
        unparsed_end = xtra_values[xtra_args.index(formatter.FUNC_XTRA_ARGS_DICT['end_date'])]
        end_date = parse_date_string(unparsed_end)
    else:
        end_date = None
    return end_date

def get_save_file(xtra_args, xtra_values):
    if formatter.FUNC_XTRA_ARGS_DICT['save'] in xtra_args:
        save_file = xtra_values[xtra_args.index(formatter.FUNC_XTRA_ARGS_DICT['save'])]
    else:
        save_file = None
    return save_file

def get_target(xtra_args, xtra_values):
    if formatter.FUNC_XTRA_ARGS_DICT['target'] in xtra_args:
        try:
            target = float(xtra_values[xtra_args.index(formatter.FUNC_XTRA_ARGS_DICT['target'])])
        except:
            target = None
    else:
        target = None
    return target

def format_allocation_profile(allocation, portfolio) -> str:
    port_return, port_volatility = portfolio.return_function(allocation), portfolio.volatility_function(allocation)
    formatted_result = "("+str(100*port_return)[:5]+"%, " + str(100*port_volatility)[:5]+"%)"
    formatted_result_title = "("
    for symbol in portfolio.tickers:
        if portfolio.tickers.index(symbol) != (len(portfolio.tickers) - 1):
            formatted_result_title += symbol+", "
        else:
            formatted_result_title += symbol + ") Portfolio Return-Risk Profile"
    whole_thing = formatted_result_title +" = "+formatted_result
    return whole_thing

def get_first_json_key(this_json):
    return list(this_json.keys())[0]

def replace_troublesome_chars(msg):
    return msg.replace('\u2265','').replace('\u0142', '')

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
                    big_mother.append(replace_troublesome_chars(line.decode("utf-8")))
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

################################################
##### FILE MANAGEMENT FUNCTIONS

def clear_directory(directory, retain=True, outdated_only=False):
    filelist = [ f for f in os.listdir(directory)]

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