#!/usr/bin/python
# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

'''Test case for QObject.timerEvent overloading'''

import os
import sys
import unittest

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
from init_paths import init_test_paths
init_test_paths(False)

from PySide6.QtCore import QObject, QCoreApplication

from helper.usesqapplication import UsesQApplication


class Dummy(QObject):

    def __init__(self, app):
        super().__init__()
        self.times_called = 0
        self.app = app

    def timerEvent(self, event):
        QObject.timerEvent(self, event)
        event.accept()
        self.times_called += 1

        if self.times_called == 5:
            self.app.exit(0)


class QObjectTimerEvent(UsesQApplication):

    def setUp(self):
        # Acquire resources
        super(QObjectTimerEvent, self).setUp()

    def tearDown(self):
        # Release resources
        super(QObjectTimerEvent, self).tearDown()

    def testTimerEvent(self):
        # QObject.timerEvent overloading
        obj = Dummy(self.app)
        timer_id = obj.startTimer(200)
        self.app.exec()
        obj.killTimer(timer_id)
        self.assertEqual(obj.times_called, 5)


if __name__ == '__main__':
    unittest.main()
