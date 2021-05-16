# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

'''Test case for timeout() signals from QTimer object.'''

import gc
import os
import sys
import unittest

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
from init_paths import init_test_paths
init_test_paths(False)

from PySide6.QtCore import QObject, QTimer, SIGNAL
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


class TestTimeoutSignal(UsesQApplication):
    '''Test case to check if the signals are really being caught'''

    def setUp(self):
        # Acquire resources
        super().setUp()
        self.watchdog = WatchDog(self)
        self.timer = QTimer()
        self.called = False

    def tearDown(self):
        # Release resources
        del self.watchdog
        del self.timer
        del self.called
        # PYSIDE-535: Need to collect garbage in PyPy to trigger deletion
        gc.collect()
        super().tearDown()

    def callback(self, *args):
        # Default callback
        self.called = True

    @unittest.skipUnless(hasattr(sys, "getrefcount"), f"{sys.implementation.name} has no refcount")
    def testTimeoutSignal(self):
        # Test the QTimer timeout() signal
        refCount = sys.getrefcount(self.timer)
        self.timer.timeout.connect(self.callback)
        self.timer.start(4)
        self.watchdog.startTimer(10)

        self.app.exec()

        self.assertTrue(self.called)
        self.assertEqual(sys.getrefcount(self.timer), refCount)


if __name__ == '__main__':
    unittest.main()

