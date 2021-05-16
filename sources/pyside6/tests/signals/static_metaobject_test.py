#!/usr/bin/env python
# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

"""Tests covering signal emission and receiving to python slots"""

import gc
import os
import sys
import unittest

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
from init_paths import init_test_paths
init_test_paths(False)

from PySide6.QtCore import QObject, SIGNAL, Slot
from helper.usesqapplication import UsesQApplication


class MyObject(QObject):
    def __init__(self, parent=None):
        QObject.__init__(self, parent)
        self._slotCalledCount = 0

    # this '@Slot()' is needed to get the right sort order in testSharedSignalEmission.
    # For some reason, it also makes the tests actually work!
    @Slot()
    def mySlot(self):
        self._slotCalledCount = self._slotCalledCount + 1


class StaticMetaObjectTest(UsesQApplication):

    def testSignalPropagation(self):
        o = MyObject()
        o2 = MyObject()

        # SIGNAL foo not created yet
        self.assertEqual(o.metaObject().indexOfSignal("foo()"), -1)

        o.connect(SIGNAL("foo()"), o2.mySlot)
        # SIGNAL foo create after connect
        self.assertTrue(o.metaObject().indexOfSignal("foo()") > 0)

        # SIGNAL does not propagate to others objects of the same type
        self.assertEqual(o2.metaObject().indexOfSignal("foo()"), -1)

        del o
        del o2
        # PYSIDE-535: Need to collect garbage in PyPy to trigger deletion
        gc.collect()
        o = MyObject()
        # The SIGNAL was destroyed with old objects
        self.assertEqual(o.metaObject().indexOfSignal("foo()"), -1)

    def testSharedSignalEmission(self):
        o = QObject()
        m = MyObject()

        o.connect(SIGNAL("foo2()"), m.mySlot)
        m.connect(SIGNAL("foo2()"), m.mySlot)
        o.emit(SIGNAL("foo2()"))
        self.assertEqual(m._slotCalledCount, 1)
        del o
        # PYSIDE-535: Need to collect garbage in PyPy to trigger deletion
        gc.collect()
        m.emit(SIGNAL("foo2()"))
        self.assertEqual(m._slotCalledCount, 2)


if __name__ == '__main__':
    unittest.main()
