#!/usr/bin/python

#############################################################################
##
## Copyright (C) 2021 The Qt Company Ltd.
## Contact: https://www.qt.io/licensing/
##
## This file is part of the test suite of Qt for Python.
##
## $QT_BEGIN_LICENSE:GPL-EXCEPT$
## Commercial License Usage
## Licensees holding valid commercial Qt licenses may use this file in
## accordance with the commercial license agreement provided with the
## Software or, alternatively, in accordance with the terms contained in
## a written agreement between you and The Qt Company. For licensing terms
## and conditions see https://www.qt.io/terms-conditions. For further
## information use the contact form at https://www.qt.io/contact-us.
##
## GNU General Public License Usage
## Alternatively, this file may be used under the terms of the GNU
## General Public License version 3 as published by the Free Software
## Foundation with exceptions as appearing in the file LICENSE.GPL3-EXCEPT
## included in the packaging of this file. Please review the following
## information to ensure the GNU General Public License requirements will
## be met: https://www.gnu.org/licenses/gpl-3.0.html.
##
## $QT_END_LICENSE$
##
#############################################################################

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

from helper.usesqcoreapplication import UsesQCoreApplication


class QStateMachineTest(UsesQCoreApplication):

    def cb(self, *args):
        self.assertEqual(self.machine.defaultAnimations(), [self.anim])

    def testBasic(self):
        self.machine = QStateMachine()
        s1 = QState()
        s2 = QState()
        s3 = QFinalState()

        QObject.connect(self.machine, SIGNAL("started()"), self.cb)

        self.anim = QParallelAnimationGroup()

        self.machine.addState(s1)
        self.machine.addState(s2)
        self.machine.addState(s3)
        self.machine.setInitialState(s1)
        self.machine.addDefaultAnimation(self.anim)
        self.machine.start()

        QTimer.singleShot(100, self.app.quit)
        self.app.exec()


class QSetConverterTest(UsesQCoreApplication):
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
