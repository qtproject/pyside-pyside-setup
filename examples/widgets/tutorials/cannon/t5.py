# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause

# PySide6 tutorial 5


import sys

from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (QApplication, QLCDNumber, QPushButton,
                               QSlider, QVBoxLayout, QWidget)


class MyWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        quit = QPushButton("Quit")
        quit.setFont(QFont("Times", 18, QFont.Bold))

        lcd = QLCDNumber(2)

        slider = QSlider(Qt.Horizontal)
        slider.setRange(0, 99)
        slider.setValue(0)

        quit.clicked.connect(qApp.quit)
        slider.valueChanged.connect(lcd.display)

        layout = QVBoxLayout(self)
        layout.addWidget(quit)
        layout.addWidget(lcd)
        layout.addWidget(slider)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    widget = MyWidget()
    widget.show()
    sys.exit(app.exec())
