import pytest

from scrilla.util import helper


@pytest.mark.parametrize('number,sigfigs,expected',[
    (1500,1,2000),
    (0.03452,2,0.035),
    (15.325, 3, 15.3),
    (-245, 2, -240),
    (-2.34566, 3, -2.35)
])
def test_significant_digits(number, sigfigs, expected):
    assert helper.significant_digits(number, sigfigs) == expected

@pytest.mark.parametrize('decimal, expected', [
    (0.03, '0.03'),
    (0.0000001, '0.0000001'),
    (0.0000000001, '0'),
    (0.15678, '0.15678'),
    (1.123456, '1.1235'),
    (-0.05, '-0.05'),
    (-0.04324, '-0.04324'),
    (-3.20987591, '-3.2099')
])
def test_format_float_number(decimal, expected):
    assert isinstance(helper.format_float_number(decimal), str)
    assert helper.format_float_number(decimal) == expected

@pytest.mark.parametrize('decimal, expected', [
    (0.03, '3%'),
    (0.15678, '15.678%'),
    (1.123456, '112.35%'),
    (-0.05, '-5%'),
    (-0.04324, '-4.324%'),
    (-3.20987591, '-320.99%')
])
def test_format_float_percent(decimal, expected):
    assert isinstance(helper.format_float_percent(decimal), str)
    assert helper.format_float_percent(decimal) == expected
