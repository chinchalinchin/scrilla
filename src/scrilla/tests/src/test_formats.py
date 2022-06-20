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

@pytest.mark.parametrize('tickers,correlation_matrix,expected',[
    (
        ['ALLY','BX','SONY'],
        [ 
            [1,    0.05, 0.4 ],
            [0.05, 1,    0.33],
            [0.4,  0.33, 1   ]
        ],
        [
            {
                'ALLY_BX_correlation': 0.05,
                'ALLY_SONY_correlation': 0.4,
            },
            {
                'BX_SONY_correlation': 0.33
            }
        ]
    ),
    (
        ['SPY','GLD','EFA', 'SLV'],
        [ 
            [1,   0.2, 0.3, 0.4],
            [0.2, 1,   0.5, 0.6],
            [0.3, 0.5, 1,   0.7],
            [0.4, 0.6, 0.7, 1  ]
        ],
        [
            {
                'SPY_GLD_correlation': 0.2,
                'SPY_EFA_correlation': 0.3,
                'SPY_SLV_correlation': 0.4
            },
            {
                'GLD_EFA_correlation': 0.5,
                'GLD_SLV_correlation': 0.6
            },
            {
                'EFA_SLV_correlation': 0.7
            }
        ]
    )
])
def test_format_correlation_matrix(tickers,correlation_matrix,expected):
    assert formats.format_correlation_matrix(tickers,correlation_matrix) == expected