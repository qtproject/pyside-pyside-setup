#!/usr/bin/python
# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

'''Test case for QObject.childEvent and QTimer.childEvent overloading'''

import os
import sys
import unittest

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
from init_paths import init_test_paths
init_test_paths(False)

from PySide6.QtCore import QObject, QTimer, QCoreApplication
from helper.usesqapplication import UsesQApplication


class ExtQObject(QObject):
    def __init__(self):
        super().__init__()
        self.child_event_received = False

    def childEvent(self, event):
        QObject.childEvent(self, event)
        self.child_event_received = True


class ExtQTimer(QTimer):
    def __init__(self):
        super().__init__()
        self.child_event_received = False

    def childEvent(self, event):
        QTimer.childEvent(self, event)
        self.child_event_received = True


class TestChildEvent(UsesQApplication):
    '''Test case for QObject::childEvent and QTimer::childEvent'''

    def setUp(self):
        UsesQApplication.setUp(self)

    def tearDown(self):
        UsesQApplication.tearDown(self)

    def testQObject(self):
        parent = ExtQObject()
        child = QObject()
        child.setParent(parent)
        self.assertTrue(parent.child_event_received)

    def testQTimer(self):
        parent = ExtQTimer()
        child = QObject()
        child.setParent(parent)
        self.assertTrue(parent.child_event_received)


if __name__ == '__main__':
    unittest.main()

