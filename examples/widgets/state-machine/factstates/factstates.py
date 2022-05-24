# Copyright (C) 2010 velociraptor Genjix <aphidia@hotmail.com>
# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause

import sys

from PySide6.QtCore import QCoreApplication, QObject, Qt, Property, Signal
from PySide6.QtStateMachine import (QFinalState, QSignalTransition, QState,
                                    QStateMachine)


class Factorial(QObject):
    x_changed = Signal(int)

    def __init__(self):
        super().__init__()
        self.xval = -1
        self.facval = 1

    def get_x(self):
        return self.xval

    def set_x(self, x):
        if self.xval == x:
            return
        self.xval = x
        self.x_changed.emit(x)
    x = Property(int, get_x, set_x)

    def get_fact(self):
        return self.facval

    def set_fact(self, fac):
        self.facval = fac

    fac = Property(int, get_fact, set_fact)


class FactorialLoopTransition(QSignalTransition):
    def __init__(self, fact):
        super().__init__(fact.x_changed)
        self.fact = fact

    def eventTest(self, e):
        if not super(FactorialLoopTransition, self).eventTest(e):
            return False
        return e.arguments()[0] > 1

    def onTransition(self, e):
        x = e.arguments()[0]
        fac = self.fact.fac
        self.fact.fac = x * fac
        self.fact.x = x - 1


class FactorialDoneTransition(QSignalTransition):
    def __init__(self, fact):
        super().__init__(fact.x_changed)
        self.fact = fact

    def eventTest(self, e):
        if not super(FactorialDoneTransition, self).eventTest(e):
            return False
        return e.arguments()[0] <= 1

    def onTransition(self, e):
        print(self.fact.fac)


if __name__ == '__main__':
    app = QCoreApplication(sys.argv)
    factorial = Factorial()
    machine = QStateMachine()

    compute = QState(machine)
    compute.assignProperty(factorial, 'fac', 1)
    compute.assignProperty(factorial, 'x', 6)
    compute.addTransition(FactorialLoopTransition(factorial))

    done = QFinalState(machine)
    done_transition = FactorialDoneTransition(factorial)
    done_transition.setTargetState(done)
    compute.addTransition(done_transition)

    machine.setInitialState(compute)
    machine.finished.connect(app.quit)
    machine.start()

    sys.exit(app.exec())
