# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause

# PySide6 tutorial 7


import sys

from PySide6.QtCore import Signal, Slot, Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (QApplication, QGridLayout, QLCDNumber,
                               QPushButton, QSlider, QVBoxLayout, QWidget)


class LCDRange(QWidget):

    value_changed = Signal(int)

    def __init__(self, parent=None):
        super().__init__(parent)

        lcd = QLCDNumber(2)

        self.slider = QSlider(Qt.Horizontal)
        self.slider.setRange(0, 99)
        self.slider.setValue(0)

        self.slider.valueChanged.connect(lcd.display)
        self.slider.valueChanged.connect(self.value_changed)

        layout = QVBoxLayout(self)
        layout.addWidget(lcd)
        layout.addWidget(self.slider)

    def value(self):
        return self.slider.value()

    @Slot(int)
    def set_value(self, value):
        self.slider.setValue(value)


class MyWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        quit = QPushButton("Quit")
        quit.setFont(QFont("Times", 18, QFont.Bold))
        quit.clicked.connect(qApp.quit)

        previous_range = None

        layout = QVBoxLayout(self)
        layout.addWidget(quit)
        grid = QGridLayout()
        layout.addLayout(grid)

        for row in range(3):
            for column in range(3):
                lcd_range = LCDRange()
                grid.addWidget(lcd_range, row, column)

                if previous_range:
                    lcd_range.value_changed.connect(previous_range.set_value)

                previous_range = lcd_range


if __name__ == '__main__':
    app = QApplication(sys.argv)
    widget = MyWidget()
    widget.show()
    sys.exit(app.exec())
