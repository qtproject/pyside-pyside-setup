# Copyright (C) 2010 velociraptor Genjix <aphidia@hotmail.com>
# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause

import sys

from PySide6.QtCore import QTimer, Qt, Property, Slot
from PySide6.QtGui import QPainter, QPalette
from PySide6.QtWidgets import QApplication, QVBoxLayout, QWidget
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
        with QPainter(self) as painter:
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
    timing.addTransition(timer.timeout, done)
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
        yellow_going_green.setObjectName('yellowGoingGreen')
        red_going_yellow.addTransition(red_going_yellow.finished,
                                       yellow_going_green)
        green_going_yellow = create_light_state(widget._yellow_light, 3000)
        green_going_yellow.setObjectName('greenGoingYellow')
        yellow_going_green.addTransition(yellow_going_green.finished,
                                         green_going_yellow)
        yellow_going_red = create_light_state(widget._green_light, 1000)
        yellow_going_red.setObjectName('yellowGoingRed')
        green_going_yellow.addTransition(green_going_yellow.finished,
                                         yellow_going_red)
        yellow_going_red.addTransition(yellow_going_red.finished,
                                       red_going_yellow)

        machine.addState(red_going_yellow)
        machine.addState(yellow_going_green)
        machine.addState(green_going_yellow)
        machine.addState(yellow_going_red)
        machine.setInitialState(red_going_yellow)
        machine.start()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    widget = TrafficLight()
    widget.resize(110, 300)
    widget.show()
    sys.exit(app.exec())
