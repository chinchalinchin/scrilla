import sys
import random
from PySide6 import QtCore, QtWidgets, QtGui

# DESIGN: menu widget holds other widgets. when you click the function button,
# it will hide the menu widget and show the function widget. a button on 
# the function widget will cause the function widget to hide and the menu
# widget to redisplay
class MenuWidget(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.hello = ["Hallo Welt", "Hei maailma", "Hola Mundo", "Привет мир"]

        self.button = QtWidgets.QPushButton("Click me!")
        self.text = QtWidgets.QLabel("Hello World",
                                     alignment=QtCore.Qt.AlignCenter)

        self.layout = QtWidgets.QVBoxLayout()
        self.layout.addWidget(self.text)
        self.layout.addWidget(self.button)
        self.setLayout(self.layout)

        self.button.clicked.connect(self.magic)

    @QtCore.Slot()
    def magic(self):
        self.text.setText(random.choice(self.hello))
        # self.hide()

if __name__ == "__main__":
    app = QtWidgets.QApplication([])

    widget = MenuWidget()
    widget.resize(800, 600)
    widget.show()

    sys.exit(app.exec_())