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

# @pytest.mark.parametrize('component,title,expected_type,expected_conf',[
#     ('title', ),
#     ('subtitle', ),
#     ('heading', ),
#     ('label', ),
#     ('error', ),
#     ('text', ),
#     ('splash', ),
#     ('calculate-button', ),
#     ('clear-button', ),
#     ('hide-button', ),
#     ('download-button', ),
#     ('source-button', ),
#     ('package-button', ),
#     ('documentation-button', ),
#     ('button')
# ])
# def test_atomic_widget_factory(qtbot, component, title, expected_type, expected_conf):
#     pass