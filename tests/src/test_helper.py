import pytest

from scrilla.util import helper

@pytest.mark.parametrize('number,digits,expected',[
    (12.234, 2, 12.23),
    (0.056789, 3, 0.056),
    (-1.8750213, 4, -1.8750)
])
def test_truncate(number, digits, expected):
    assert helper.truncate(number, digits) == expected

@pytest.mark.parametrize('number,sigfigs,expected',[
    (1500, 1, 2000),
    (0.03452, 2,0.035),
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
    assert isinstance(helper.format_float_percent(decimal), str)
    assert helper.format_float_percent(decimal) == expected

@pytest.mark.parametrize('array,expected',[
    ([' hi', ' ho '], ['hi','ho']),
    ([' that     ', '     was', 'easy  '], ['that', 'was', 'easy']),
    (['hi  ho'], ['hi  ho'])
])
def test_strip_string_array(array, expected):
    assert helper.strip_string_array(array) == expected

@pytest.mark.parametrize('string,upper,delimiter,expected',[ 
    (   
        'a.b.c.d',
        True,
        '.', 
        ['A','B', 'C', 'D']
    ),
    (
        'a . b.c  .  d',
        True,
        '.', 
        ['A','B', 'C', 'D']
    ),
    (
        'a . b.c  .  d',
        False,
        '.', 
        ['a','b', 'c', 'd']
    ),
    (
        'a.b.c.d', 
        False, 
        '.', 
        ['a','b','c','d']
    ),
    (
        'a.b.c.d', 
        False, 
        ',', 
        ['a.b.c.d']
    ),
    (
        'a.b.c.d', 
        True, 
        ',', 
        ['A.B.C.D']
    ),
    (
        'a,b,c,d',
        True,
        ',', 
        ['A','B','C','D']
    )
])
def test_split_and_strip(string,upper,delimiter,expected):
    assert helper.split_and_strip(string,upper,delimiter) == expected
# def test_format_dict_percent(dict,expected):
#     pass

# def test_format_dict_number(dict,expected):
#     pass

@pytest.mark.parametrize('dict1,dict2,expected1,expected2', [
    (
        {
            'a': 1,
            'b': 2
        },
        {
            'c': 3,
            'd': 4
        },
        {},
        {}
    ),
    (
        {
            'a': 1,
            'b': 2
        },
        {
            'a': 3,
            'd': 4
        },
        { 
            'a': 1
        },
        {
            'a': 3
        }
    ),
    (
        {
            'a': 1,
            'b': 2,
            'c': 3
        },
        {
            'b': 4,
            'c': 5,
            'd': 6
        },
        { 
            'b': 2,
            'c': 3
        },
        {
            'b': 4,
            'c': 5 
        }
    ),
])
def test_intersect_dict_keys(dict1,dict2,expected1,expected2):
    assert helper.intersect_dict_keys(dict1,dict2) == (expected1,expected2)