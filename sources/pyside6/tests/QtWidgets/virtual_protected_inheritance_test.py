# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

'''Test cases for overriding inherited protected virtual methods'''

import gc
import os
import sys
import unittest

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
from init_paths import init_test_paths
init_test_paths(False)

from PySide6.QtCore import QTimerEvent
from PySide6.QtWidgets import QApplication, QSpinBox

from helper.usesqapplication import UsesQApplication


class MySpinButton(QSpinBox):
    '''Simple example class of overriding QObject.timerEvent'''

    def __init__(self, max_runs=5, app=None):
        # Creates a new spinbox that will run <max_runs> and quit <app>
        super().__init__()

        if app is None:
            app = QApplication([])

        self.app = app
        self.max_runs = max_runs
        self.runs = 0

    def timerEvent(self, event):
        # Timer event method
        self.runs += 1

        self.setValue(self.runs)

        if self.runs == self.max_runs:
            self.app.quit()

        if not isinstance(event, QTimerEvent):
            raise TypeError('Invalid event type. Must be TimerEvent')


class TimerEventTest(UsesQApplication):
    '''Test case for running QObject.timerEvent from inherited class'''

    qapplication = True

    def setUp(self):
        # Acquire resources
        super(TimerEventTest, self).setUp()
        self.widget = MySpinButton(app=self.app)

    def tearDown(self):
        # Release resources
        del self.widget
        # PYSIDE-535: Need to collect garbage in PyPy to trigger deletion
        gc.collect()
        super(TimerEventTest, self).tearDown()

    def testMethod(self):
        # QWidget.timerEvent overrinding (protected inherited)
        timer_id = self.widget.startTimer(0)

        self.app.exec()

        self.widget.killTimer(timer_id)

        self.assertTrue(self.widget.runs >= self.widget.max_runs)


if __name__ == '__main__':
    unittest.main()
    #app = QApplication([])
    #widget  = MySpinButton(app=app)
    #widget.startTimer(500)
    #widget.show()
    #app.exec()

