# Copyright (C) 2010 velociraptor Genjix <aphidia@hotmail.com>
# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause
from __future__ import annotations

import sys

from PySide6.QtCore import QCoreApplication, QEvent
from PySide6.QtStateMachine import QAbstractTransition, QState, QStateMachine


class PingEvent(QEvent):
    def __init__(self):
        super().__init__(QEvent.Type(QEvent.User + 2))


class PongEvent(QEvent):
    def __init__(self):
        super().__init__(QEvent.Type(QEvent.User + 3))


class Pinger(QState):
    def __init__(self, parent):
        super().__init__(parent)

    def onEntry(self, e):
        self.p = PingEvent()
        self.machine().postEvent(self.p)
        print('ping?')


class PongTransition(QAbstractTransition):
    def eventTest(self, e):
        return e.type() == QEvent.User + 3

    def onTransition(self, e):
        self.p = PingEvent()
        machine.postDelayedEvent(self.p, 500)
        print('ping?')


class PingTransition(QAbstractTransition):
    def eventTest(self, e):
        return e.type() == QEvent.User + 2

    def onTransition(self, e):
        self.p = PongEvent()
        machine.postDelayedEvent(self.p, 500)
        print('pong!')


if __name__ == '__main__':
    app = QCoreApplication(sys.argv)

    machine = QStateMachine()
    group = QState(QState.ParallelStates)
    group.setObjectName('group')

    pinger = Pinger(group)
    pinger.setObjectName('pinger')
    pinger.addTransition(PongTransition())

    ponger = QState(group)
    ponger.setObjectName('ponger')
    ponger.addTransition(PingTransition())

    machine.addState(group)
    machine.setInitialState(group)
    machine.start()

    sys.exit(app.exec())
