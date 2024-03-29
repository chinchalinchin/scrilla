import pytest

from scrilla.util import dater

@pytest.mark.parametrize('this_date,expected',[ 
    ('2022-06-20', True)
])
def test_is_date_holiday(this_date,expected):
    assert dater.is_date_holiday(this_date) == expected

@pytest.mark.parametrize('this_date,expected',[ 
    ('2022-06-20', False)
])
def test_is_trading_date(this_date, expected):
    assert dater.is_trading_date(this_date) == expected

@pytest.mark.parametrize('start_date,days,bond,result', [
    ('2021-11-15', 2, False, '2021-11-11'),
    ('2021-10-19', 5, False, '2021-10-12'),
    ('2021-09-13', 7, False, '2021-09-01'),  # includes labor day
    ('2021-11-24', 10, False, '2021-11-10'),
    ('2021-06-01', 2, False, '2021-05-27'),  # includes memorial day,
    ('2022-06-21', 1, False, '2022-06-17'),  # includes first observance of Juneteenth
    ('2022-06-06', 2, False, '2022-06-02'),
    ('2022-01-17', 7, False, '2022-01-05'),  # includes MLK Jr. day
])
def test_decrement_date_by_business_days(start_date, days, bond, result):
    test_date = dater.decrement_date_by_business_days(start_date, days, bond)
    assert(test_date == dater.parse(result))


@pytest.mark.parametrize('start_date,end_date,length', [
    ('2021-01-01', '2021-01-01', 1),
    ('2021-11-04', '2021-11-06', 3),
    ('2020-01-01', '2020-02-05', 36)
])
def test_dates_between(start_date, end_date, length):
    date_range = dater.dates_between(start_date, end_date)
    assert len(date_range) == length
    assert dater.parse(start_date) in date_range
    assert dater.parse(end_date) in date_range

@pytest.mark.parametrize('start_date,end_date,length', [
    ('2022-06-01', '2022-06-07',5),
    ('2021-12-23', '2021-12-27', 2)
])
def test_business_dates_between(start_date, end_date, length):
    date_range = dater.business_dates_between(start_date, end_date)
    assert len(date_range) == length