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
from PySide6.QtCore import QObject, Signal, SignalInstance

'''Tests the behaviour of homonymous signals and slots.'''


class HomonymousSignalAndMethodTest(unittest.TestCase):

    def setUp(self):
        self.value = 123
        self.called = False
        self.obj = TestObject(self.value)

    def tearDown(self):
        del self.value
        del self.called
        del self.obj
        # PYSIDE-535: Need to collect garbage in PyPy to trigger deletion
        gc.collect()

    def testIdValueSignalEmission(self):
        def callback(idValue):
            self.assertEqual(idValue, self.value)
        self.obj.idValue.connect(callback)
        self.obj.emitIdValueSignal()

    def testStaticMethodDoubleSignalEmission(self):
        def callback():
            self.called = True
        self.obj.staticMethodDouble.connect(callback)
        self.obj.emitStaticMethodDoubleSignal()
        self.assertTrue(self.called)

    def testSignalNotCallable(self):
        self.assertRaises(TypeError, self.obj.justASignal)

    def testCallingInstanceMethodWithArguments(self):
        self.assertRaises(TypeError, TestObject.idValue, 1)

    def testCallingInstanceMethodWithoutArguments(self):
        self.assertRaises(TypeError, TestObject.idValue)

    def testHomonymousSignalAndMethod(self):
        self.assertEqual(self.obj.idValue(), self.value)

    def testHomonymousSignalAndStaticMethod(self):
        self.assertEqual(TestObject.staticMethodDouble(3), 6)

    def testHomonymousSignalAndStaticMethodFromInstance(self):
        self.assertEqual(self.obj.staticMethodDouble(4), 8)


# PYSIDE-1730: Homonymous Methods with multiple inheritance

class Q(QObject):
    signal = Signal()

    def method(self):
        msg = 'Q::method'
        print(msg)
        return msg


class M:

    def signal(self):
        msg = 'M::signal'
        print(msg)
        return msg

    def method(self):
        msg = 'M::method'
        print(msg)
        return msg


class C(M, Q):

    def __init__(self):
        Q.__init__(self)
        M.__init__(self)


class HomonymousMultipleInheritanceTest(unittest.TestCase):

    def testHomonymousMultipleInheritance(self):
        c = C()
        self.assertEqual(c.method(), "M::method") # okay
        self.assertEqual(c.signal(), "M::signal") # problem on PySide6 6.2.2
        self.assertEqual(type(c.signal), SignalInstance)


if __name__ == '__main__':
    unittest.main()

