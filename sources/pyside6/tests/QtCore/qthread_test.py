#!/usr/bin/python
# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

'''Test cases for QThread'''

import os
import sys
import unittest

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
from init_paths import init_test_paths
init_test_paths(False)

from PySide6.QtCore import QThread, QCoreApplication, QObject, QTimer, Slot
from PySide6.QtCore import QEventLoop

from helper.usesqapplication import UsesQApplication


class Dummy(QThread):
    '''Dummy thread'''
    def __init__(self, *args):
        super().__init__(*args)
        self.called = False

    def run(self):
        # Start-quit sequence
        self.qobj = QObject()
        self.called = True


class QThreadSimpleCase(UsesQApplication):

    def setUp(self):
        UsesQApplication.setUp(self)
        self._started_called = False
        self._finished_called = False
        self.called = False

    def testThread(self):
        # Basic QThread test
        obj = Dummy()
        obj.start()
        self.assertTrue(obj.wait(100))

        self.assertTrue(obj.called)

    @Slot()
    def abort_application(self):
        if self._thread.isRunning():
            print("Warning: terminating thread", file=sys.stderr)
            self._thread.terminate()
        self.app.quit()

    @Slot()
    def finished(self):
        self._finished_called = True

    @Slot()
    def started(self):
        self._started_called = True

    def testSignals(self):
        # QThread.finished() (signal)
        self._thread = Dummy()
        self._thread.started.connect(self.started)
        self._thread.finished.connect(self.finished)
        self._thread.finished.connect(self.app.quit)

        QTimer.singleShot(50, self._thread.start)
        QTimer.singleShot(1000, self.abort_application)

        self.app.exec()
        if self._thread.isRunning():
            self._thread.wait(100)

        self.assertTrue(self._started_called)
        self.assertTrue(self._finished_called)


if __name__ == '__main__':
    unittest.main()
