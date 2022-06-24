import pytest

from scrilla.util import helper


@pytest.mark.parametrize('number,digits,expected', [
    (12.234, 2, 12.23),
    (0.056789, 3, 0.056),
    (-1.8750213, 4, -1.8750)
])
def test_truncate(number, digits, expected):
    assert helper.truncate(number, digits) == expected


@pytest.mark.parametrize('array,expected', [
    ([' hi', ' ho '], ['hi', 'ho']),
    ([' that     ', '     was', 'easy  '], ['that', 'was', 'easy']),
    (['hi  ho'], ['hi  ho'])
])
def test_strip_string_array(array, expected):
    assert helper.strip_string_array(array) == expected


@pytest.mark.parametrize('string,upper,delimiter,expected', [
    (
        'a.b.c.d',
        True,
        '.',
        ['A', 'B', 'C', 'D']
    ),
    (
        'a . b.c  .  d',
        True,
        '.',
        ['A', 'B', 'C', 'D']
    ),
    (
        'a . b.c  .  d',
        False,
        '.',
        ['a', 'b', 'c', 'd']
    ),
    (
        'a.b.c.d',
        False,
        '.',
        ['a', 'b', 'c', 'd']
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
        ['A', 'B', 'C', 'D']
    )
])
def test_split_and_strip(string, upper, delimiter, expected):
    assert helper.split_and_strip(string, upper, delimiter) == expected


@pytest.mark.parametrize('array,decimals,expected', [
    (
        [.005, .2367, 1.56808],
        2,
        [.01, .24, 1.57]
    )
])
def test_round_array(array, decimals, expected):
    assert helper.round_array(array, decimals) == expected


@pytest.mark.parametrize('dict1,dict2,expected1,expected2', [
    (
        {
            'a': 1,
            'b': 2
        },
        {
            'a': 3,
            'c': 5
        },
        {
            'b': 2
        },
        {
            'c': 5
        }
    ),
    (
        {
            'one': 'a',
            'two': 'b',
            'three': 'c'
        },
        {
            'one': 'hello',
            'four': 'there',
            'five': 'obiwan'
        },
        {
            'two': 'b',
            'three': 'c'
        },
        {
            'four': 'there',
            'five': 'obiwan'
        }
    ),
    (
        {
            'a': 1,
            'b': 2,
            'c': 3,
            'd': 4,
            'e': 5
        },
        {
            'a': 3,
            'b': 4,
            'c': 5
        },
        {
            'd': 4,
            'e': 5
        },
        {}
    ),
])
def test_complement_dict_keys(dict1, dict2, expected1, expected2):
    assert helper.complement_dict_keys(dict1, dict2) == (expected1, expected2)


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
def test_intersect_dict_keys(dict1, dict2, expected1, expected2):
    assert helper.intersect_dict_keys(dict1, dict2) == (expected1, expected2)


@pytest.mark.parametrize('decimal,expected', [
    (0.01, False),
    (0.001, False),
    (0.0001, False),
    (0.00001, False),
    (0.000001, False),
    (0.0000001, False),
    (0.00000001, True),
    (0, True),
    (-0.01, False),
    (-0.001, False),
    (-0.0001, False),
    (-0.00001, False),
    (-0.000001, False),
    (-0.0000001, False),
    (-0.00000001, True),
])
def test_exceeds_accurary(decimal, expected):
    assert helper.exceeds_accuracy(decimal) == expected


@pytest.mark.parametrize('number,sigfigs,expected', [
    (1500, 1, 2000),
    (0.03452, 2, 0.035),
    (15.325, 3, 15.3),
    (-245, 2, -240),
    (-2.34566, 3, -2.35)
])
def test_significant_digits(number, sigfigs, expected):
    assert helper.significant_digits(number, sigfigs) == expected

@pytest.mark.parametrize('this_dict,desired_order,expected',[
    (
        {
            'a': 1,
            'b': 2,
            'c': 3,
            'd': 4,
            'e': 5
        },
        ['e','c','a','b', 'd'],
        {
            'e': 5,
            'c': 3,
            'a': 1,
            'b': 2,
            'd': 4
        }
    )
])
def test_reorder_dict(this_dict,desired_order,expected):
    assert helper.reorder_dict(this_dict,desired_order) == expected