#!/usr/bin/env python
# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

'''Test case for overflowing C++ numeric types.'''

import os
import sys
import unittest

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
from shiboken_paths import init_paths
init_paths()

from sample import *


class OverflowTest(unittest.TestCase):
    '''Test case for overflowing C++ numeric types.'''

    def assertRaises(self, *args, **kwds):
        if not hasattr(sys, "pypy_version_info"):
            # PYSIDE-535: PyPy complains "Fatal RPython error: NotImplementedError"
            return super().assertRaises(*args, **kwds)

    def testUnsignedInt(self):
        '''C++ function receives an unsigned int argument and raise OverflowError if the value is negative.'''
        val = 100
        self.assertEqual(doubleUnsignedInt(val), 2 * val)
        val *= -1
        self.assertRaises(OverflowError, doubleUnsignedInt, val)

    def testLongLong(self):
        '''C++ function receives an long long argument and raise OverflowError if the value is negative.'''
        val = 100
        self.assertEqual(doubleLongLong(val), 2 * val)
        val = int(100)
        self.assertEqual(doubleLongLong(val), 2 * val)
        val = (2 << 64) + 1
        self.assertRaises(OverflowError, doubleLongLong, val)

    def testUnsignedLongLong(self):
        '''C++ function receives an unsigned long long argument and raise OverflowError if the value is negative.'''
        val = 100
        self.assertEqual(doubleUnsignedLongLong(val), 2 * val)
        val = int(100)
        self.assertEqual(doubleUnsignedLongLong(val), 2 * val)
        val = -100
        self.assertRaises(OverflowError, doubleUnsignedLongLong, val)
        val = int(-200)
        self.assertRaises(OverflowError, doubleUnsignedLongLong, val)

    def testOverflow(self):
        '''Calls function with unsigned int parameter using an overflowing value.'''
        self.assertRaises(OverflowError, doubleUnsignedInt, 42415335332353253)
        doubleUnsignedInt(0xdeadbeef)

    def testShortOverflow(self):
        '''Calls function with short parameter using an overflowing value.'''
        doubleShort(-3)
        self.assertRaises(OverflowError, doubleShort, 0xFFFF*-1)
        self.assertRaises(OverflowError, doubleShort, 0xFFFF + 1)

    def testOverflowOnCtor(self):
        '''Calls object ctor with int parameter using overflowing values.'''
        self.assertRaises(OverflowError, Point, 42415335332353253, 42415335332353253)

if __name__ == '__main__':
    unittest.main()

