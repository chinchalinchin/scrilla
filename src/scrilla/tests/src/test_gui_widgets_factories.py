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

def test_dialog_widget_factory(qtbot):
    options = ['list','of','options']
    widget = factories.dialog_widget_factory('name', options)
    option_widget = widget.layout().itemAt(0).widget().layout().itemAt(0).widget()
    button_widget = widget.layout().itemAt(1).widget()

    assert isinstance(widget, QtWidgets.QDialog)
    assert isinstance(button_widget, QtWidgets.QDialogButtonBox)
    assert isinstance(option_widget, QtWidgets.QComboBox)
    for i, opt in enumerate(options):
        assert option_widget.itemText(i) == opt

def test_group_widget_factory(qtbot):
    options = ['a', 'real', 'sophies', 'choice']
    widget = factories.group_widget_factory(options, 'my group')
    assert isinstance(widget, QtWidgets.QGroupBox)
    for i in range(len(options)):
        radio = widget.layout().itemAt(i).widget()
        assert isinstance(radio, QtWidgets.QRadioButton)
        assert radio.text() == options[i]

@pytest.mark.parametrize('component,expected_type',[
    ('date', QtWidgets.QDateEdit),
    ('decimal', QtWidgets.QLineEdit),
    ('currency', QtWidgets.QLineEdit),
    ('integer', QtWidgets.QLineEdit),
    ('flag', QtWidgets.QRadioButton),
    ('symbols', QtWidgets.QLineEdit),
    ('symbol', QtWidgets.QLineEdit),
    ('randomstring', QtWidgets.QWidget)
])
def test_argument_widget_factory(qtbot, component, expected_type):
    widget = factories.argument_widget_factory(component, 'argument placeholder')
    label_widget = widget.layout().itemAt(0).widget()
    arg_widget = widget.layout().itemAt(1).widget()
    assert isinstance(widget, QtWidgets.QWidget)
    assert isinstance(label_widget, QtWidgets.QLabel)
    assert isinstance(arg_widget, expected_type) 

def test_set_policy_on_widget_list(qtbot):
    widgets = [QtWidgets.QWidget() for _ in range(0, 10)]

    policy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Maximum, 
                                    QtWidgets.QSizePolicy.Maximum)
    factories.set_policy_on_widget_list(widgets, policy)
    assert all(isinstance(widget.sizePolicy(),QtWidgets.QSizePolicy) for widget in widgets)
    assert all(isinstance(widget.sizePolicy().verticalPolicy(),
                            QtWidgets.QSizePolicy.Policy) for widget in widgets)
    assert all(isinstance(widget.sizePolicy().horizontalPolicy(),
                            QtWidgets.QSizePolicy.Policy) for widget in widgets)