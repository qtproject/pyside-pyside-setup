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

from PySide6.QtCore import (QObject, QParallelAnimationGroup,
                            QPropertyAnimation, QTimer, SIGNAL)
from PySide6.QtStateMachine import (QFinalState, QState, QStateMachine)

from helper.usesqapplication import UsesQApplication


class QStateMachineTest(UsesQApplication):

    def cb(self, *args):
        self.assertEqual(self.machine.defaultAnimations(), [self.anim])

    def testBasic(self):
        self.machine = QStateMachine()
        s1 = QState()
        s2 = QState()
        s3 = QFinalState()

        self.machine.started.connect(self.cb)

        self.anim = QParallelAnimationGroup()

        self.machine.addState(s1)
        self.machine.addState(s2)
        self.machine.addState(s3)
        self.machine.setInitialState(s1)
        self.machine.addDefaultAnimation(self.anim)
        self.machine.start()

        QTimer.singleShot(100, self.app.quit)
        self.app.exec()


class QSetConverterTest(UsesQApplication):
    '''Test converter of QSet toPython using QStateAnimation.configuration'''

    def testBasic(self):
        '''QStateMachine.configuration converting QSet to python set'''
        machine = QStateMachine()
        s1 = QState()
        machine.addState(s1)
        machine.setInitialState(s1)
        machine.start()

        QTimer.singleShot(100, self.app.quit)
        self.app.exec()

        configuration = machine.configuration()

        self.assertTrue(isinstance(configuration, set))
        self.assertTrue(s1 in configuration)


if __name__ == '__main__':
    unittest.main()
