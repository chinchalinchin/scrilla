import datetime
from datetime import date

import math
import holidays
from typing import Any, List, Tuple, Union

import dateutil.easter as easter

from scrilla.settings import DATE_FORMAT


def today() -> datetime.date:
    """
    Returns today's date
    """
    return datetime.date.today()


def validate_order_of_dates(start_date: date, end_date: date) -> Tuple[date, date]:
    """
    Returns the inputted dates as an tuple ordered from earliest to latest.
    """
    delta = (end_date - start_date).days
    if delta < 0:
        return end_date, start_date
    return start_date, end_date


def parse(date_string: str) -> Union[date, None]:
    """
    Converts a date string in the 'YYYY-MM-DD' format to a Python `datetime.date`.
    """
    return datetime.datetime.strptime(date_string, DATE_FORMAT).date()


def validate_date(this_date):
    if isinstance(this_date, str):
        return parse(this_date)
    if not isinstance(this_date, date):
        raise ValueError(
            f'{this_date} is neither date nor \'{DATE_FORMAT}\' formatted string')
    return this_date


def validate_date_range(start_date: Any, end_date: Any) -> Tuple[date, date]:
    if isinstance(start_date, str):
        start_date = parse(start_date)
    elif not isinstance(start_date, date):
        raise ValueError(
            f'{start_date} is neither date nor \'{DATE_FORMAT}\' formatted string')
    if isinstance(end_date, str):
        end_date = parse(end_date)
    elif not isinstance(end_date, date):
        raise ValueError(
            f'{end_date} is neither date nor \'{DATE_FORMAT}\' formatted string')
    return validate_order_of_dates(start_date, end_date)


def validate_date_list(dates: Union[List[Union[datetime.date, str]]]) -> Union[List[datetime.date], None]:
    """

    Raises
    ------
    1. **ValueError**
        If the supplied list of dates contains unexpected data types, this error will be thrown.

    """
    verified_dates = []
    for this_date in dates:
        if isinstance(this_date, str):
            verified_dates.append(parse(this_date))
            continue
        if isinstance(this_date, datetime.date):
            verified_dates.append(this_date)
            continue
        raise ValueError(
            f'{this_date} is neither date nor \'{DATE_FORMAT}\'formatted string')
    return verified_dates


def to_string(this_date: Union[date, None] = None) -> str:
    """ 
    Returns a datetime formatted as 'YYYY-MM-DD'. If no date is provided, function will return today's formatted date.
    """
    if this_date is None:
        return to_string(today())
    return datetime.datetime.strftime(this_date, DATE_FORMAT)


def is_date_today(this_date: Union[date, str]) -> bool:
    return (validate_date(this_date) == datetime.date.today())


def is_future_date(this_date: Union[date, str]) -> bool:
    return (validate_date(this_date) - today()).days > 0


def truncate_future_from_date(this_date: Union[date, str]) -> datetime.date:
    this_date = validate_date(this_date)
    if is_future_date(this_date):
        return today()
    return this_date


def last_close_date():
    right_now = datetime.datetime.now()
    trading_close_today = right_now.replace(hour=14)
    if right_now > trading_close_today:
        return right_now.date()
    return get_previous_business_date(right_now.date())


def is_date_weekend(this_date: Union[date, str]) -> bool:
    return validate_date(this_date).weekday() in [5, 6]


def is_date_holiday(this_date: Union[date, str]) -> bool:
    this_date = validate_date(this_date)
    us_holidays = holidays.UnitedStates(years=this_date.year)
    # generate list without columbus day and veterans day since markets are open on those days
    trading_holidays = [
        "Columbus Day", "Columbus Day (Observed)", "Veterans Day", "Veterans Day (Observed)"]
    custom_holidays = [that_date for that_date in list(
        us_holidays) if us_holidays[that_date] not in trading_holidays]
    # add good friday to list since markets are closed on good friday
    custom_holidays.append(easter.easter(
        year=this_date.year) - datetime.timedelta(days=2))

    return (this_date in custom_holidays)


def get_last_trading_date() -> date:
    """
    Returns
    -------
    The last full trading day. If today is a trading day and the time is past market close, today's date will be returned. Otherwise, the previous business day's date will be returned. 
    """
    todays_date = datetime.datetime.now()
    if is_date_holiday(todays_date) or is_date_weekend(todays_date):
        return get_previous_business_date(todays_date.date())
    return last_close_date()


def this_date_or_last_trading_date(this_date: Union[date, str, None] = None) -> date:
    if this_date is None:
        return get_last_trading_date()
    this_date = validate_date(this_date)
    if is_date_holiday(this_date) or is_date_weekend(this_date):
        return get_previous_business_date(this_date)
    if is_date_today(this_date):
        return last_close_date()
    return this_date


def format_date_range(start_date: date, end_date: date) -> str:
    result = ""
    if start_date is not None:
        start_string = to_string(start_date)
        result += f'From {start_string}'
    if end_date is not None:
        end_string = to_string(end_date)
        result += f' Until {end_string}'
    return result


def is_trading_date(this_date: Union[date, str]) -> bool:
    this_date = validate_date(this_date)
    return not is_date_weekend(this_date) and not is_date_holiday(this_date)


def intersect_with_trading_dates(date_key_dict: dict) -> dict:
    return {this_date: date_key_dict[this_date] for this_date in date_key_dict if is_trading_date(this_date)}


def get_holidays_between(start_date: Union[date, str], end_date: Union[date, str]) -> int:
    if isinstance(start_date, date):
        start_date = to_string(start_date)
    if isinstance(end_date, date):
        end_date = to_string(end_date)
    us_holidays = holidays.UnitedStates()
    return len(us_holidays[start_date: end_date])

# YYYY-MM-DD


def consecutive_trading_days(start_date: Union[date, str], end_date: Union[date, str]) -> bool:
    """
    Parameters
    ----------
    1. **start_date_string**: ``str``
        The start date of the time period under consideration. Must be formatted "YYYY-MM-DD"
    2. **end_date_string**: ``str``
        The end date of the time period under consideration. Must be formatted "YYYY-MM-DD"

    Returns 
    -------
    True
        if start_date_string and end_date_string are consecutive trading days, i.e. Tuesday -> Wednesday or Friday -> Monday,
        or Tuesday -> Thursday where Wednesday is a Holiday.
    False
        if start_date_string and end_date_string are NOT consecutive trading days.
    """
    start_date, end_date = validate_date_range(start_date, end_date)

    if is_date_weekend(start_date) or is_date_weekend(end_date):
        return False

    delta = (end_date - start_date).days

    if delta < 0:
        start_date, end_date = end_date, start_date
        delta = end_date - start_date

    holiday_count = get_holidays_between(
        start_date=start_date, end_date=end_date)

    if (delta - holiday_count) == 0:
        return False

    if (delta - holiday_count) == 1:
        return True

    if ((delta - holiday_count) > 1 and (delta - holiday_count) < 4):
        start_week, end_week = start_date.isocalendar()[
            1], end_date.isocalendar()[1]

        if start_week == end_week:
            return False

        return True

    return False


def dates_between(start_date: Union[date, str], end_date: Union[date, str]) -> List[date]:
    """
    Returns a list of dates between the inputted dates. "Between" is used in the inclusive sense, i.e. the list includes `start_date` and `end_date`.

    Parameters
    ----------
    1. **start_date**: ``datetime.date``
        Start date of the date range.
    2. **end_date**: ``datetime.date``
        End date of the date range. 
    """
    start_date, end_date = validate_date_range(start_date, end_date)
    return [start_date + datetime.timedelta(x) for x in range((end_date - start_date).days+1)]


def days_between(start_date: Union[date, str], end_date: Union[date, str]) -> int:
    start_date, end_date = validate_date_range(start_date, end_date)
    return int((end_date - start_date).days) + 1

# excludes start_date


def business_dates_between(start_date: Union[date, str], end_date: Union[date, str]) -> List[date]:
    """
    Returns a list of business dates between the inputted dates. "Between" is used in the inclusive sense, i.e. the list includes `start_date` and `dates`

    Parameters
    ----------
    1. **start_date**: ``datetime.date``
        Start date of the date range.
    2. **end_date**: ``datetime.date``
        End date of the date range. 
    """
    start_date, end_date = validate_date_range(start_date, end_date)
    dates = []
    for x in range((end_date - start_date).days+1):
        this_date = start_date + datetime.timedelta(x)
        if is_trading_date(this_date):
            dates.append(this_date)
    return dates


def business_days_between(start_date: Union[date, str], end_date: Union[date, str]) -> List[int]:
    start_date, end_date = validate_date_range(start_date, end_date)
    dates = dates_between(start_date, end_date)
    return len([1 for this_date in dates if is_trading_date(this_date)])


def weekends_between(start_date: Union[date, str], end_date: Union[date, str]) -> List[int]:
    start_date, end_date = validate_date_range(start_date, end_date)
    dates = dates_between(start_date, end_date)
    return len([1 for day in dates if day.weekday() > 4])


def decrement_date_by_days(start_date: Union[date, str], days: int):
    start_date = validate_date(start_date)
    while days > 0:
        days -= 1
        start_date -= datetime.timedelta(days=1)
    return start_date


def decrement_date_by_business_days(start_date: Union[date, str], business_days: int) -> date:
    """
    Subtracts `business_days`, ignoring weekends and trading holidays, from `start_date`
    """
    start_date = validate_date(start_date)
    first_pass = True
    while business_days > 0:
        if is_trading_date(start_date):
            if first_pass:
                first_pass = False
            else:
                business_days -= 1

        if business_days > 0:
            start_date -= datetime.timedelta(days=1)

    return start_date


def increment_date_by_business_days(start_date: Union[date, str], business_days: int) -> date:
    start_date = validate_date(start_date)
    while business_days > 0:
        if is_trading_date(start_date):
            business_days -= 1
        start_date += datetime.timedelta(days=1)
    return start_date


def get_next_business_date(this_date: Union[date, str]) -> date:
    this_date = validate_date(this_date)
    while not is_trading_date(this_date):
        this_date += datetime.timedelta(days=1)
    return this_date


def get_previous_business_date(this_date: Union[date, str]) -> date:
    this_date = decrement_date_by_days(start_date=this_date, days=1)
    while not is_trading_date(this_date):
        this_date -= datetime.timedelta(days=1)
    return this_date

# in years


def get_time_to_next_month(todays_date: date = today(), trading_days: int = 252) -> float:
    """
    Parameters
    ----------
    1. **todays_date**: ``date``
        *Optional*. Reference date for calculation.
    2. **trading_days**: ``int``
        *Optional*. Number of trading days in a year. Defaults to 252.

    """
    # TODO: what if first day of the month falls on non-trading days?
    todays_date = datetime.date.today()
    next_month = datetime.date(
        year=todays_date.year, month=(todays_date.month+1), day=1)
    return ((next_month - todays_date).days / trading_days)


def get_time_to_next_year(todays_date: date = today(), trading_days: int = 252) -> float:
    """
    Parameters
    ----------
    1. **todays_date**: ``date``
        *Optional*. Reference date for calculation.
    2. **trading_days**: ``int``
        *Optional*. Number of trading days in a year. Defaults to 252.
    """
    # TODO: what if first day of year falls on non-trading day?
    #       which it will, by definition. fuckwit.
    next_year = datetime.datetime(year=todays_date.year+1, day=1, month=1)
    return ((next_year - todays_date).days / trading_days)


def get_time_to_next_quarter(todays_date: date = today(), trading_days: int = 252) -> float:
    """
    Parameters
    ----------
    1. **todays_date**: ``date``
        *Optional*. Reference date for calculation.
    2. **trading_days**: ``int``
        *Optional*. Number of trading days in a year. Defaults to 252.
    """
    # TODO: what if first day of quarter falls on non-trading days?

    first_q = datetime.date(year=todays_date.year, month=1, day=1)
    second_q = datetime.date(year=todays_date.year, month=4, day=1)
    third_q = datetime.date(year=todays_date.year, month=7, day=1)
    fourth_q = datetime.date(year=todays_date.year, month=10, day=1)
    next_first_q = datetime.date(year=(todays_date.year+1), month=1, day=1)

    first_delta = (first_q - todays_date).days / trading_days
    second_delta = (second_q - todays_date).days / trading_days
    third_delta = (third_q - todays_date).days / trading_days
    fourth_delta = (fourth_q - todays_date).days / trading_days
    next_delta = (next_first_q - todays_date).days / trading_days

    return min(i for i in [first_delta, second_delta, third_delta, fourth_delta, next_delta] if i > 0)


def get_time_to_next_period(starting_date: Union[date, str], period: float) -> float:
    """
    Divides the year into segments of equal length 'period' and then calculates the time from today until 
    the next period. 

    Parameters
    ---------- 
    1. **starting_date**: ``Union[date, str]``
        Starting day of the period. Not to be confused with today. This is the point in time when the recurring event started. 
    2. **period**: float
        Length of one period, measured in years. 
    """
    if period is None:
        return 0

    starting_date = validate_date(starting_date)
    todays_date = datetime.date.today()
    floored_days = math.floor(365*period)

    while ((starting_date - todays_date).days < 0):
        starting_date += datetime.timedelta(days=floored_days)

    return float((todays_date - starting_date).days / 365)
