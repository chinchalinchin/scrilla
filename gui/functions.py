import sys

from PySide6 import QtCore, QtWidgets, QtGui

import app.statistics as statistics

class RiskProfileWidget(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()

        self.title = QtWidgets.QLabel("Risk-Profile Over Last 100 Days", alignment=QtCore.Qt.AlignTop)
        self.message = QtWidgets.QLabel("Please separate symbols with a comma", alignment=QtCore.Qt.AlignBottom)
        self.calculate_button = QtWidgets.QPushButton("Calculate Risk-Return")
        self.clear_button = QtWidgets.QPushButton("Clear")

        self.result = QtWidgets.QLabel("Result", alignment=QtCore.Qt.AlignCenter)
        self.result.hide()
        
        self.symbols = QtWidgets.QLineEdit()
        self.symbols.setMaxLength(100)
        
        self.layout = QtWidgets.QVBoxLayout()

        self.layout.addWidget(self.title)
        self.layout.addWidget(self.result)
        self.layout.addWidget(self.message)
        self.layout.addWidget(self.symbols)
        self.layout.addWidget(self.calculate_button)
        self.layout.addWidget(self.clear_button)

        self.setLayout(self.layout)

        self.calculate_button.clicked.connect(self.calculate)
        self.clear_button.clicked.connect(self.clear)

    @QtCore.Slot()
    def calculate(self):
        user_symbols = self.symbols.text().upper().split(",")

        formatted_result = ""
        for user_symbol in user_symbols:
            user_symbol = user_symbol.strip()
            stats = statistics.calculate_risk_return(user_symbol)
            if stats:
                annual_ret, annual_vol = str(stats['annual_return'])[:5], str(stats['annual_volatility'])[:5]
                formatted_result += f'{user_symbol}_(return, vol) = ({annual_ret}, {annual_vol}) \n'
            else: 
                formatted_result += f'Price History Not Found For {user_symbol} \n'
        self.result.setText(formatted_result)
        self.result.show()

    @QtCore.Slot()
    def clear(self):
        self.symbol.clear()
        self.result.hide()

if __name__ == "__main__":
    app = QtWidgets.QApplication([])

    widget = RiskProfileWidget()
    widget.resize(800, 600)
    widget.show()

    sys.exit(app.exec_())