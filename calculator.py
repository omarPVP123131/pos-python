from PyQt6.QtWidgets import QWidget, QVBoxLayout, QGridLayout, QPushButton, QLineEdit

class CalculatorModule(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        
        self.display = QLineEdit()
        self.display.setReadOnly(True)
        layout.addWidget(self.display)

        buttons_layout = QGridLayout()
        buttons = [
            '7', '8', '9', '/',
            '4', '5', '6', '*',
            '1', '2', '3', '-',
            '0', '.', '=', '+'
        ]

        row = 0
        col = 0
        for button in buttons:
            btn = QPushButton(button)
            btn.clicked.connect(self.on_button_click)
            buttons_layout.addWidget(btn, row, col)
            col += 1
            if col > 3:
                col = 0
                row += 1

        layout.addLayout(buttons_layout)
        self.setLayout(layout)

    def on_button_click(self):
        button = self.sender()
        current = self.display.text()

        if button.text() == '=':
            try:
                result = eval(current)
                self.display.setText(str(result))
            except:
                self.display.setText("Error")
        else:
            self.display.setText(current + button.text())