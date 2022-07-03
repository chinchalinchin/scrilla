import pytest

from PySide6 import QtWidgets

from scrilla.gui.widgets import components

@pytest.mark.parametrize('func_name,expected_conf',[
    (
        'correlation',
        {
            'criteria': False,
            'discount': False,
            'end_date': True,
            'expiry': False,
            'investment': False,
            'likelihood': True,
            'moments': True,
            'optimize_sharpe': False,
            'percentiles': True,
            'probability': False,
            'start_date': True,
            'steps': False,
            'target': False
        }
    ),
    (
        'discount_dividend',
        {
            'criteria': False,
            'discount': True,
            'end_date': False,
            'expiry': False,
            'investment': False,
            'likelihood': False,
            'moments': False,
            'optimize_sharpe': False,
            'percentiles': False,
            'probability': False,
            'start_date': False,
            'steps': False,
            'target': False
        }
    ),
    (
        'efficient_frontier',
        {
            'criteria': False,
            'discount': False,
            'end_date': True,
            'expiry': False,
            'investment': True,
            'likelihood': True,
            'moments': True,
            'optimize_sharpe': False,
            'percentiles': True,
            'probability': False,
            'start_date': True,
            'steps': True,
            'target': True
        }
    ),
    (
        'moving_averages',
        {
            'criteria': False,
            'discount': False,
            'end_date': True,
            'expiry': False,
            'investment': False,
            'likelihood': True,
            'moments': True,
            'optimize_sharpe': False,
            'percentiles': True,
            'probability': False,
            'start_date': True,
            'steps': False,
            'target': False
        }
    ),
    (
        'optimize_portfolio',
        {
            'criteria': False,
            'discount': False,
            'end_date': True,
            'expiry': False,
            'investment': True,
            'likelihood': True,
            'moments': True,
            'optimize_sharpe': True,
            'percentiles': True,
            'probability': False,
            'start_date': True,
            'steps': False,
            'target': True
        }
    ),
    (
        'risk_profile',
        {
            'criteria': False,
            'discount': False,
            'end_date': False,
            'expiry': False,
            'investment': False,
            'likelihood': True,
            'moments': True,
            'optimize_sharpe': False,
            'percentiles': True,
            'probability': False,
            'start_date': True,
            'steps': False,
            'target': False
        }
    ),
    (
        'yield_curve',
        {
            'criteria': False,
            'discount': False,
            'end_date': False,
            'expiry': False,
            'investment': False,
            'likelihood': False,
            'moments': False,
            'optimize_sharpe': False,
            'percentiles': False,
            'probability': False,
            'start_date': True,
            'steps': False,
            'target': False
        }
    ),
    # TODO: plot_return_dist 
])
def test_skeleton_widget(qtbot, func_name, expected_conf):
    skeleton = components.SkeletonWidget(func_name, QtWidgets.QWidget)
    assert skeleton.controls == expected_conf