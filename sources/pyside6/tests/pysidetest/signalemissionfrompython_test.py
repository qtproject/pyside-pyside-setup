#!/usr/bin/python
# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0
from __future__ import annotations

import gc
import os
import sys
import unittest

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
from init_paths import init_test_paths
init_test_paths(True)

# Note: For PYSIDE-2792/testConnectionSignal()), QMetaObject needs to be
# forcibly created before Connection.
from PySide6.QtCore import QObject, SIGNAL, Slot, QMetaObject  # noqa: F401
from testbinding import TestObject, Connection

'''Tests the behaviour of signals with default values when emitted from Python.'''


class Receiver(QObject):
    """Test receiver for PYSIDE-2792 (testConnectionSignal)."""

    def __init__(self, p=None):
        super().__init__(p)
        self.received_handle = -1

    @Slot(Connection)
    def connectionSlot(self, c):
        self.received_handle = c.handle()


class SignalEmissionFromPython(unittest.TestCase):

    def setUp(self):
        self.obj1 = TestObject(0)
        self.obj2 = TestObject(0)
        self.one_called = 0
        self.two_called = 0

    def tearDown(self):
        del self.obj1
        del self.obj2
        del self.one_called
        del self.two_called
        # PYSIDE-535: Need to collect garbage in PyPy to trigger deletion
        gc.collect()

    def testConnectNewStyleEmitVoidSignal(self):
        def callbackOne():
            self.one_called += 1
            self.obj2.signalWithDefaultValue.emit()

        def callbackTwo():
            self.two_called += 1
        self.obj1.signalWithDefaultValue.connect(callbackOne)
        self.obj2.signalWithDefaultValue.connect(callbackTwo)
        self.obj1.emitSignalWithDefaultValue_void()
        self.obj2.emitSignalWithDefaultValue_void()
        self.assertEqual(self.one_called, 1)
        self.assertEqual(self.two_called, 2)

    def testConnectionSignal(self):
        """PYSIDE-2792: Test whether a signal parameter of type 'Connection'
           clashes with QMetaObject.Connection."""
        receiver = Receiver()
        qmetaobject_conn = self.obj1.connectionSignal.connect(receiver.connectionSlot)
        self.assertTrue(qmetaobject_conn)
        self.obj1.emitConnectionSignal(42)
        self.assertEqual(receiver.received_handle, 42)

    def testConnectOldStyleEmitVoidSignal(self):
        def callbackOne():
            self.one_called += 1
            self.obj2.signalWithDefaultValue.emit()

        def callbackTwo():
            self.two_called += 1
        self.obj1.signalWithDefaultValue.connect(callbackOne)
        self.obj2.signalWithDefaultValue.connect(callbackTwo)
        self.obj1.emitSignalWithDefaultValue_void()
        self.obj2.emitSignalWithDefaultValue_void()
        self.assertEqual(self.one_called, 1)
        self.assertEqual(self.two_called, 2)

    def testConnectNewStyleEmitBoolSignal(self):
        def callbackOne():
            self.one_called += 1
            self.obj2.signalWithDefaultValue[bool].emit(True)

        def callbackTwo():
            self.two_called += 1
        self.obj1.signalWithDefaultValue.connect(callbackOne)
        self.obj2.signalWithDefaultValue.connect(callbackTwo)
        self.obj1.emitSignalWithDefaultValue_void()
        self.obj2.emitSignalWithDefaultValue_void()
        self.assertEqual(self.one_called, 1)
        self.assertEqual(self.two_called, 2)

    def testConnectOldStyleEmitBoolSignal(self):
        def callbackOne():
            self.one_called += 1
            self.obj2.signalWithDefaultValue[bool].emit(True)

        def callbackTwo():
            self.two_called += 1
        self.obj1.signalWithDefaultValue.connect(callbackOne)
        self.obj2.signalWithDefaultValue.connect(callbackTwo)
        self.obj1.emitSignalWithDefaultValue_void()
        self.obj2.emitSignalWithDefaultValue_void()
        self.assertEqual(self.one_called, 1)
        self.assertEqual(self.two_called, 2)


if __name__ == '__main__':
    unittest.main()
