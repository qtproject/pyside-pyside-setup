#!/usr/bin/python
# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

'''Test cases for QTimer.singleShot'''

import gc
import os
import sys
import unittest

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
from init_paths import init_test_paths
init_test_paths(False)

from PySide6.QtCore import QObject, QTimer, QCoreApplication, Signal
from helper.usesqapplication import UsesQApplication


class WatchDog(QObject):
    '''Exits the QCoreApplication main loop after sometime.'''

    def __init__(self, watched):
        super().__init__()
        self.times_called = 0
        self.watched = watched

    def timerEvent(self, evt):
        self.times_called += 1
        if self.times_called == 20:
            self.watched.exit_app_cb()


class TestSingleShot(UsesQApplication):
    '''Test case for QTimer.singleShot'''

    def setUp(self):
        # Acquire resources
        UsesQApplication.setUp(self)
        self.watchdog = WatchDog(self)
        self.called = False

    def tearDown(self):
        # Release resources
        del self.watchdog
        del self.called
        # PYSIDE-535: Need to collect garbage in PyPy to trigger deletion
        gc.collect()
        UsesQApplication.tearDown(self)

    def callback(self):
        self.called = True
        self.app.quit()

    def testSingleShot(self):
        QTimer.singleShot(100, self.callback)
        self.app.exec()
        self.assertTrue(self.called)


class SigEmitter(QObject):

    sig1 = Signal()


class TestSingleShotSignal(UsesQApplication):
    '''Test case for QTimer.singleShot connecting to signals'''

    def setUp(self):
        UsesQApplication.setUp(self)
        self.watchdog = WatchDog(self)
        self.called = False

    def tearDown(self):
        del self.watchdog
        del self.called
        # PYSIDE-535: Need to collect garbage in PyPy to trigger deletion
        gc.collect()
        UsesQApplication.tearDown(self)

    def callback(self):
        self.called = True
        self.app.quit()

    def testSingleShotSignal(self):
        emitter = SigEmitter()
        emitter.sig1.connect(self.callback)
        QTimer.singleShot(100, emitter.sig1)
        self.app.exec()
        self.assertTrue(self.called)


if __name__ == '__main__':
    unittest.main()

