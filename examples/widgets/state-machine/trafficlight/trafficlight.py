
#############################################################################
##
## Copyright (C) 2010 velociraptor Genjix <aphidia@hotmail.com>
## Copyright (C) 2016 The Qt Company Ltd.
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

from PySide6.QtWidgets import *
from PySide6.QtGui import *
from PySide6.QtCore import *
from PySide6.QtStateMachine import QFinalState, QState, QStateMachine


class LightWidget(QWidget):
    def __init__(self, color):
        super().__init__()
        self.color = color
        self._on_val = False

    def is_on(self):
        return self._on_val

    def set_on(self, on):
        if self._on_val == on:
            return
        self._on_val = on
        self.update()

    @Slot()
    def turn_off(self):
        self.set_on(False)

    @Slot()
    def turn_on(self):
        self.set_on(True)

    def paintEvent(self, e):
        if not self._on_val:
            return
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setBrush(self.color)
        painter.drawEllipse(0, 0, self.width(), self.height())

    on = Property(bool, is_on, set_on)


class TrafficLightWidget(QWidget):
    def __init__(self):
        super().__init__()
        vbox = QVBoxLayout(self)
        self._red_light = LightWidget(Qt.red)
        vbox.addWidget(self._red_light)
        self._yellow_light = LightWidget(Qt.yellow)
        vbox.addWidget(self._yellow_light)
        self._green_light = LightWidget(Qt.green)
        vbox.addWidget(self._green_light)
        pal = QPalette()
        pal.setColor(QPalette.Window, Qt.black)
        self.setPalette(pal)
        self.setAutoFillBackground(True)


def create_light_state(light, duration, parent=None):
    light_state = QState(parent)
    timer = QTimer(light_state)
    timer.setInterval(duration)
    timer.setSingleShot(True)
    timing = QState(light_state)
    timing.entered.connect(light.turn_on)
    timing.entered.connect(timer.start)
    timing.exited.connect(light.turn_off)
    done = QFinalState(light_state)
    timing.addTransition(timer, SIGNAL('timeout()'), done)
    light_state.setInitialState(timing)
    return light_state


class TrafficLight(QWidget):
    def __init__(self):
        super().__init__()
        vbox = QVBoxLayout(self)
        widget = TrafficLightWidget()
        vbox.addWidget(widget)
        vbox.setContentsMargins(0, 0, 0, 0)

        machine = QStateMachine(self)
        red_going_yellow = create_light_state(widget._red_light, 1000)
        red_going_yellow.setObjectName('redGoingYellow')
        yellow_going_green = create_light_state(widget._red_light, 1000)
        yellow_going_green.setObjectName('redGoingYellow')
        red_going_yellow.addTransition(red_going_yellow, SIGNAL('finished()'), yellow_going_green)
        green_going_yellow = create_light_state(widget._yellow_light, 3000)
        green_going_yellow.setObjectName('redGoingYellow')
        yellow_going_green.addTransition(yellow_going_green, SIGNAL('finished()'), green_going_yellow)
        yellow_going_red = create_light_state(widget._green_light, 1000)
        yellow_going_red.setObjectName('redGoingYellow')
        green_going_yellow.addTransition(green_going_yellow, SIGNAL('finished()'), yellow_going_red)
        yellow_going_red.addTransition(yellow_going_red, SIGNAL('finished()'), red_going_yellow)

        machine.addState(red_going_yellow)
        machine.addState(yellow_going_green)
        machine.addState(green_going_yellow)
        machine.addState(yellow_going_red)
        machine.setInitialState(red_going_yellow)
        machine.start()


if __name__ == '__main__':
    import sys
    app = QApplication(sys.argv)
    widget = TrafficLight()
    widget.resize(110, 300)
    widget.show()
    sys.exit(app.exec())
