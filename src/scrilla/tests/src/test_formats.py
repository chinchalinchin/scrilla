from calendar import formatstring
import pytest

#from scrilla.static import formats

from ...static import formats

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
    assert isinstance(formats.format_float_number(decimal), str)
    assert formats.format_float_number(decimal) == expected

@pytest.mark.parametrize('decimal,expected', [
    (0.03, '3%'),
    (0.15678, '15.678%'),
    (1.123456, '112.35%'),
    (0.0000000000001, '0%'),
    (-0.05, '-5%'),
    (-0.04324, '-4.324%'),
    (-3.20987591, '-320.99%')
])
def test_format_float_percent(decimal, expected):
    assert isinstance(formats.format_float_percent(decimal), str)
    assert formats.format_float_percent(decimal) == expected

@pytest.mark.parametrize('this_dict,which_key,expected',[
    (
        {
            'a': 1.05,
            'b': 0.067
        },
        'b',
        {
            'a': 1.05,
            'b': '6.7%'
        }
    ),
    (
        {
            'one': 1.35,
            'two': 'a word please'
        },
        'one',
        {
            'one': '135%',
            'two': 'a word please'
        }
    )
])
def test_format_dict_percent(this_dict, which_key, expected):
    assert formats.format_dict_percent(this_dict, which_key) == expected

@pytest.mark.parametrize('this_dict,which_key,expected',[
    (
        {
            'a': 'hi',
            'b': 1.0237498237589234
        },
        'b',
        {
            'a': 'hi',
            'b': '1.0237'
        }
    ),
    (
        {
            'one': 473.3456,
            'two': 55.324980
        },
        'one',
        {
            'one': '473.35',
            'two': 55.324980
        },
    )

])
def test_format_dict_number(this_dict, which_key, expected):
    assert formats.format_dict_number(this_dict, which_key) == expected