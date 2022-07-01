import pytest

from PySide6 import QtWidgets

from scrilla.gui.widgets import factories

@pytest.mark.parametrize('layout,expected', [
    ('vertical-box', QtWidgets.QVBoxLayout), 
    ('horizontal-box', QtWidgets.QHBoxLayout)
])
def test_layout_factory(qtbot, layout, expected):
    widget = factories.layout_factory(layout)
    assert isinstance(widget, QtWidgets.QWidget)
    assert isinstance(widget.layout(), expected) 
