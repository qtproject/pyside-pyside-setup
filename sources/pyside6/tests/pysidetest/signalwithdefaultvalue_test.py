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

'''Tests the behaviour of signals with default values.'''


class SignalWithDefaultValueTest(unittest.TestCase):

    def setUp(self):
        self.obj = TestObject(0)
        self.void_called = False
        self.bool_called = False

    def tearDown(self):
        del self.obj
        del self.void_called
        del self.bool_called
        # PYSIDE-535: Need to collect garbage in PyPy to trigger deletion
        gc.collect()

    def testConnectNewStyleEmitVoidSignal(self):
        def callbackVoid():
            self.void_called = True

        def callbackBool(value):
            self.bool_called = True
        self.obj.signalWithDefaultValue.connect(callbackVoid)
        self.obj.signalWithDefaultValue[bool].connect(callbackBool)
        self.obj.emitSignalWithDefaultValue_void()
        self.assertTrue(self.void_called)
        self.assertTrue(self.bool_called)

    def testConnectNewStyleEmitBoolSignal(self):
        def callbackVoid():
            self.void_called = True

        def callbackBool(value):
            self.bool_called = True
        self.obj.signalWithDefaultValue.connect(callbackVoid)
        self.obj.signalWithDefaultValue[bool].connect(callbackBool)
        self.obj.emitSignalWithDefaultValue_bool()
        self.assertTrue(self.void_called)
        self.assertTrue(self.bool_called)

    def testConnectOldStyleEmitVoidSignal(self):
        def callbackVoid():
            self.void_called = True

        def callbackBool(value):
            self.bool_called = True
        self.obj.signalWithDefaultValue.connect(callbackVoid)
        self.obj.signalWithDefaultValue.connect(callbackBool)
        self.obj.emitSignalWithDefaultValue_void()
        self.assertTrue(self.void_called)
        self.assertTrue(self.bool_called)

    def testConnectOldStyleEmitBoolSignal(self):
        def callbackVoid():
            self.void_called = True

        def callbackBool(value):
            self.bool_called = True
        self.obj.signalWithDefaultValue.connect(callbackVoid)
        self.obj.signalWithDefaultValue.connect(callbackBool)
        self.obj.emitSignalWithDefaultValue_bool()
        self.assertTrue(self.void_called)
        self.assertTrue(self.bool_called)


if __name__ == '__main__':
    unittest.main()

