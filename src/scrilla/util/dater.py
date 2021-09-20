import datetime, math, holidays

import dateutil.easter as easter

def get_today():
    return datetime.date.today()

def is_future_date(date):
    return (date - get_today()).days > 0

def truncate_future_from_date(date):
    if is_future_date(date):
        return get_today()
    return date

def get_time_to_next_period(starting_date, period):
    if period is None:
        return 0
    
    today = datetime.date.today()
    floored_days=math.floor(365*period)

    while ((starting_date - today).days<0):
        starting_date += datetime.timedelta(days=floored_days)
    
    return ((today - starting_date).days / 365)