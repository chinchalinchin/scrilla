import pytest

from scrilla.util import dater

@pytest.mark.parametrize('start_date,days,result', [
    ('2021-11-15', 2, '2021-11-11'),
    ('2021-10-19', 5, '2021-10-12'),
    ('2021-09-13', 7, '2021-09-01'), # includes labor day
    ('2021-11-24', 10, '2021-11-10'),
    ('2021-06-01', 2, '2021-05-27') # includes memorial day
])
def test_decrement_date_by_business_days(start_date, days, result):
    test_date = dater.decrement_date_by_business_days(start_date, days)
    assert(test_date == dater.parse(result))