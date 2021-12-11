#!/usr/bin/python

#############################################################################
##
## Copyright (C) 2021 The Qt Company Ltd.
## Contact: https://www.qt.io/licensing/
##
## This file is part of the test suite of Qt for Python.
##
## $QT_BEGIN_LICENSE:GPL-EXCEPT$
## Commercial License Usage
## Licensees holding valid commercial Qt licenses may use this file in
## accordance with the commercial license agreement provided with the
## Software or, alternatively, in accordance with the terms contained in
## a written agreement between you and The Qt Company. For licensing terms
## and conditions see https://www.qt.io/terms-conditions. For further
## information use the contact form at https://www.qt.io/contact-us.
##
## GNU General Public License Usage
## Alternatively, this file may be used under the terms of the GNU
## General Public License version 3 as published by the Free Software
## Foundation with exceptions as appearing in the file LICENSE.GPL3-EXCEPT
## included in the packaging of this file. Please review the following
## information to ensure the GNU General Public License requirements will
## be met: https://www.gnu.org/licenses/gpl-3.0.html.
##
## $QT_END_LICENSE$
##
#############################################################################

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

