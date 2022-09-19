# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause

# PySide6 tutorial 8


import sys

from PySide6.QtCore import Signal, Slot, Qt, qWarning
from PySide6.QtGui import QColor, QFont, QPainter, QPalette
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

        self.setFocusProxy(self.slider)

    def value(self):
        return self.slider.value()

    @Slot(int)
    def set_value(self, value):
        self.slider.setValue(value)

    def set_range(self, minValue, maxValue):
        if minValue < 0 or maxValue > 99 or minValue > maxValue:
            qWarning("LCDRange.setRange({minValue}, {maxValue})\n"
                    "\tRange must be 0..99\n"
                    "\tand minValue must not be greater than maxValue")
            return

        self.slider.setRange(minValue, maxValue)


class CannonField(QWidget):

    angle_changed = Signal(int)

    def __init__(self, parent=None):
        super().__init__(parent)

        self._current_angle = 45
        self.setPalette(QPalette(QColor(250, 250, 200)))
        self.setAutoFillBackground(True)

    def angle(self):
        return self._current_angle

    @Slot(int)
    def set_angle(self, angle):
        if angle < 5:
            angle = 5
        if angle > 70:
            angle = 70
        if self._current_angle == angle:
            return
        self._current_angle = angle
        self.update()
        self.angle_changed.emit(self._current_angle)

    def paintEvent(self, event):
        with QPainter(self) as painter:
            painter.drawText(200, 200, f"Angle = {self._current_angle}")


class MyWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        quit = QPushButton("Quit")
        quit.setFont(QFont("Times", 18, QFont.Bold))

        quit.clicked.connect(qApp.quit)

        angle = LCDRange()
        angle.set_range(5, 70)

        cannon_field = CannonField()

        angle.value_changed.connect(cannon_field.set_angle)
        cannon_field.angle_changed.connect(angle.set_value)

        grid_layout = QGridLayout(self)
        grid_layout.addWidget(quit, 0, 0)
        grid_layout.addWidget(angle, 1, 0)
        grid_layout.addWidget(cannon_field, 1, 1, 2, 1)
        grid_layout.setColumnStretch(1, 10)

        angle.set_value(60)
        angle.setFocus()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    widget = MyWidget()
    widget.setGeometry(100, 100, 500, 355)
    widget.show()
    sys.exit(app.exec())
