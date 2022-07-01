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

@pytest.mark.parametrize('component,expected_type',[
    ( 'title', QtWidgets.QLabel),
    ('subtitle', QtWidgets.QLabel),
    ('heading', QtWidgets.QLabel),
    ('label',  QtWidgets.QLabel),
    ('error', QtWidgets.QLabel),
    ('text', QtWidgets.QLabel),
    ('splash', QtWidgets.QLabel),
    ('calculate-button', QtWidgets.QPushButton),
    ('clear-button', QtWidgets.QPushButton),
    ('hide-button', QtWidgets.QPushButton),
    ('download-button', QtWidgets.QPushButton),
    ('source-button', QtWidgets.QPushButton),
    ('package-button', QtWidgets.QPushButton),
    ('okay-button', QtWidgets.QPushButton),
    ('documentation-button',QtWidgets.QPushButton ),
    ('button', QtWidgets.QPushButton),
    ('save-dialog', QtWidgets.QFileDialog),
    ('table', QtWidgets.QTableWidget),
    ('table-item', QtWidgets.QTableWidgetItem),
    ('figure', QtWidgets.QLabel),
    ('menu-bar', QtWidgets.QMenuBar),
    ('random-string', QtWidgets.QWidget),
    ('werqklasdaq', QtWidgets.QWidget)
])
def test_atomic_widget_factory(qtbot, component, expected_type):
    widget = factories.atomic_widget_factory(component, 'placehodler')
    assert isinstance(widget, expected_type)