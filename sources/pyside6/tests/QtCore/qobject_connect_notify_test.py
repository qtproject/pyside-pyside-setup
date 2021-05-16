# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

''' Test case for QObject::connectNotify()'''

import os
import sys
import unittest

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
from init_paths import init_test_paths
init_test_paths(False)

from PySide6.QtCore import QObject, SIGNAL, SLOT
from helper.usesqapplication import UsesQApplication


def cute_slot():
    pass


class Obj(QObject):
    def __init__(self):
        super().__init__()
        self.con_notified = False
        self.dis_notified = False
        self.signal = ""

    def connectNotify(self, signal):
        self.con_notified = True
        self.signal = signal

    def disconnectNotify(self, signal):
        self.dis_notified = True

    def reset(self):
        self.con_notified = False
        self.dis_notified = False


class TestQObjectConnectNotify(UsesQApplication):
    '''Test case for QObject::connectNotify'''
    def setUp(self):
        UsesQApplication.setUp(self)
        self.called = False

    def tearDown(self):
        UsesQApplication.tearDown(self)

    def testBasic(self):
        sender = Obj()
        receiver = QObject()
        sender.connect(SIGNAL("destroyed()"), receiver, SLOT("deleteLater()"))
        self.assertTrue(sender.con_notified)
        # When connecting to a regular slot, and not a python callback function, QObject::connect
        # will use the non-cloned method signature, so connecting to destroyed() will actually
        # connect to destroyed(QObject*).
        self.assertEqual(sender.signal.methodSignature(), "destroyed(QObject*)")
        sender.disconnect(SIGNAL("destroyed()"), receiver, SLOT("deleteLater()"))
        self.assertTrue(sender.dis_notified)

    def testPySignal(self):
        sender = Obj()
        receiver = QObject()
        sender.connect(SIGNAL("foo()"), receiver, SLOT("deleteLater()"))
        self.assertTrue(sender.con_notified)
        sender.disconnect(SIGNAL("foo()"), receiver, SLOT("deleteLater()"))
        self.assertTrue(sender.dis_notified)

    def testPySlots(self):
        sender = Obj()
        receiver = QObject()
        sender.connect(SIGNAL("destroyed()"), cute_slot)
        self.assertTrue(sender.con_notified)
        sender.disconnect(SIGNAL("destroyed()"), cute_slot)
        self.assertTrue(sender.dis_notified)

    def testpyAll(self):
        sender = Obj()
        receiver = QObject()
        sender.connect(SIGNAL("foo()"), cute_slot)
        self.assertTrue(sender.con_notified)
        sender.disconnect(SIGNAL("foo()"), cute_slot)
        self.assertTrue(sender.dis_notified)


if __name__ == '__main__':
    unittest.main()
