#!/usr/bin/python
# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

import os
import sys
import unittest

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
from init_paths import init_test_paths
init_test_paths(False)

from PySide6.QtCore import QCoreApplication, QObject, SIGNAL, QTimer
from PySide6.QtStateMachine import (QEventTransition, QFinalState, QState,
                                    QStateMachine, QSignalTransition)


class QStateTest(unittest.TestCase):
    def testBasic(self):
        app = QCoreApplication([])

        o = QObject()
        o.setProperty("text", "INdT")

        machine = QStateMachine()
        s1 = QState()
        s1.assignProperty(o, "text", "Rocks")

        s2 = QFinalState()
        t = s1.addTransition(o, SIGNAL("change()"), s2)
        self.assertTrue(isinstance(t, QSignalTransition))

        machine.addState(s1)
        machine.addState(s2)
        machine.setInitialState(s1)
        machine.start()

        o.emit(SIGNAL("change()"))

        QTimer.singleShot(100, app.quit)
        app.exec()

        txt = o.property("text")
        self.assertTrue(txt, "Rocks")


if __name__ == '__main__':
    unittest.main()
