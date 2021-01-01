import sys
import random
from PySide6 import QtCore, QtWidgets, QtGui

from gui.functions import RiskProfileWidget, CorrelationWidget

def get_title_font():
    font = QtGui.QFont('Impact', 12)
    font.bold()
    return font

# NOTE: widget_buttons and function_widgets must preserve order.
class MenuWidget(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.title = QtWidgets.QLabel("Pynance", alignment=QtCore.Qt.AlignTop)
        self.title.setFont(get_title_font())

        self.back_button = QtWidgets.QPushButton("Menu")
        self.back_button.setAutoDefault(True)
        self.back_button.hide()

        # Widget Buttons
        self.widget_buttons = [ QtWidgets.QPushButton("Risk-Return Profile"),
                                    QtWidgets.QPushButton("Correlation") ]

        # Function Widgets
        self.function_widgets = [ RiskProfileWidget(),
                                    CorrelationWidget() ]

        self.layout = QtWidgets.QVBoxLayout()

        self.layout.addWidget(self.title)
    
        self.layout.addStretch()

        for button in self.widget_buttons:
            this_widget = self.widget_buttons.index(button)
            button.setAutoDefault(True)
            if this_widget == 1:
                button.clicked.connect(lambda: self.show_widget(this_widget))
            self.layout.addWidget(button)
            button.show()

        for i in range(len(self.widget_buttons)):
            self.widget_buttons[i].setAutoDefault(True)
            # TODO: can't pass i for some reason...has to be literal int???
                # has to have something to do with when lambda functions execute
            if i == 0:
                self.widget_buttons[i].clicked.connect(lambda: self.show_widget(0))
            elif i == 1:
                self.widget_buttons[i].clicked.connect(lambda: self.show_widget(1))
            self.layout.addWidget(self.widget_buttons[i])
            self.widget_buttons[i].show()


        for widget in self.function_widgets:
            widget.hide()
            self.layout.addWidget(widget)
        
        self.layout.addWidget(self.back_button)

        self.setLayout(self.layout)
        
        self.back_button.clicked.connect(self.clear)

    @QtCore.Slot()
    def show_widget(self, widget):
        for button in self.widget_buttons:
            button.hide()

        self.back_button.show()
        
        self.function_widgets[widget].show()

    @QtCore.Slot()
    def clear(self):
        for widget in self.function_widgets:
            widget.hide()

        for button in self.widget_buttons:
            button.show()

        self.back_button.hide()

if __name__ == "__main__":
    app = QtWidgets.QApplication([])

    widget = MenuWidget()
    widget.resize(800, 600)
    widget.show()

    sys.exit(app.exec_())