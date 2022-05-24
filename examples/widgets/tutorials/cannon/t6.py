# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause

# PySide6 tutorial 6


import sys

from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (QApplication, QGridLayout, QLCDNumber,
                               QPushButton, QSlider, QVBoxLayout, QWidget)


class LCDRange(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        lcd = QLCDNumber(2)
        slider = QSlider(Qt.Horizontal)
        slider.setRange(0, 99)
        slider.setValue(0)
        slider.valueChanged.connect(lcd.display)

        layout = QVBoxLayout(self)
        layout.addWidget(lcd)
        layout.addWidget(slider)


class MyWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        quit = QPushButton("Quit")
        quit.setFont(QFont("Times", 18, QFont.Bold))
        quit.clicked.connect(qApp.quit)

        layout = QVBoxLayout(self)
        layout.addWidget(quit)
        grid = QGridLayout()
        layout.addLayout(grid)
        for row in range(3):
            for column in range(3):
                grid.addWidget(LCDRange(), row, column)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    widget = MyWidget()
    widget.show()
    sys.exit(app.exec())
