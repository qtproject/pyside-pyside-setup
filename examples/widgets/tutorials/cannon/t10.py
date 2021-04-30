
#############################################################################
##
## Copyright (C) 2021 The Qt Company Ltd.
## Contact: http://www.qt.io/licensing/
##
## This file is part of the Qt for Python examples of the Qt Toolkit.
##
## $QT_BEGIN_LICENSE:BSD$
## You may use this file under the terms of the BSD license as follows:
##
## "Redistribution and use in source and binary forms, with or without
## modification, are permitted provided that the following conditions are
## met:
##   * Redistributions of source code must retain the above copyright
##     notice, this list of conditions and the following disclaimer.
##   * Redistributions in binary form must reproduce the above copyright
##     notice, this list of conditions and the following disclaimer in
##     the documentation and/or other materials provided with the
##     distribution.
##   * Neither the name of The Qt Company Ltd nor the names of its
##     contributors may be used to endorse or promote products derived
##     from this software without specific prior written permission.
##
##
## THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
## "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
## LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
## A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
## OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
## SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
## LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
## DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
## THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
## (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
## OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE."
##
## $QT_END_LICENSE$
##
#############################################################################

# PySide6 tutorial 10


import sys

from PySide6.QtCore import QRect, Qt, Signal, Slot
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
            qWarning(f"LCDRange::setRange({minValue}, {maxValue})\n"
                    "\tRange must be 0..99\n"
                    "\tand minValue must not be greater than maxValue")
            return

        self.slider.setRange(minValue, maxValue)


class CannonField(QWidget):

    angle_changed = Signal(int)
    force_changed = Signal(int)

    def __init__(self, parent=None):
        super().__init__(parent)

        self._current_angle = 45
        self._current_force = 0
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

    def force(self):
        return self._current_force

    @Slot(int)
    def set_force(self, force):
        if force < 0:
            force = 0
        if self._current_force == force:
            return
        self._current_force = force
        self.force_changed.emit(self._current_force)

    def paintEvent(self, event):
        painter = QPainter(self)

        painter.setPen(Qt.NoPen)
        painter.setBrush(Qt.blue)

        painter.translate(0, self.height())
        painter.drawPie(QRect(-35, -35, 70, 70), 0, 90 * 16)
        painter.rotate(-self._current_angle)
        painter.drawRect(QRect(33, -4, 15, 8))

    def cannon_rect(self):
        result = QRect(0, 0, 50, 50)
        result.moveBottomLeft(self.rect().bottomLect())
        return result


class MyWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        quit = QPushButton("&Quit")
        quit.setFont(QFont("Times", 18, QFont.Bold))

        quit.clicked.connect(qApp.quit)

        angle = LCDRange()
        angle.set_range(5, 70)

        force = LCDRange()
        force.set_range(10, 50)

        cannon_field = CannonField()

        angle.value_changed.connect(cannon_field.set_angle)
        cannon_field.angle_changed.connect(angle.set_value)

        force.value_changed.connect(cannon_field.set_force)
        cannon_field.force_changed.connect(force.set_value)

        left_layout = QVBoxLayout()
        left_layout.addWidget(angle)
        left_layout.addWidget(force)

        grid_layout = QGridLayout(self)
        grid_layout.addWidget(quit, 0, 0)
        grid_layout.addLayout(left_layout, 1, 0)
        grid_layout.addWidget(cannon_field, 1, 1, 2, 1)
        grid_layout.setColumnStretch(1, 10)

        angle.set_value(60)
        force.set_value(25)
        angle.setFocus()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    widget = MyWidget()
    widget.setGeometry(100, 100, 500, 355)
    widget.show()
    sys.exit(app.exec())
