#!/usr/bin/python
# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

import gc
import os
import sys
import unittest

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
from init_paths import init_test_paths
init_test_paths(True)

from testbinding import TestObject
from PySide6.QtCore import QObject, SIGNAL

'''Tests the behaviour of signals with default values when emitted from Python.'''


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

