#!/usr/bin/env python
# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

'''Test cases for constructor and method signature decisor on Time class.'''

import sys
import os
import sys
import unittest

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
from shiboken_paths import init_paths
init_paths()
import datetime

from sample import Time, ImplicitConv, ObjectType

class TimeTest(unittest.TestCase):
    '''Test cases for constructor and method signature decisor on Time class.
    The constructor and one method have these signatures: CTORMETHOD() and
    CTORMETHOD(int h, int m, int s = 0, int ms = 0); there another method
    with a more complex signature METH(int, int, ImplicitConv=DEFVALUE, ObjectType=0),
    to produce an even worse scenario.
    '''

    def testConstructorWithoutParamers(self):
        '''Constructor without parameters: Time()'''
        time = Time()
        self.assertTrue(time.isNull())

    def testConstructorWithAllParamers(self):
        '''Constructor with all parameters: Time(int h, int m, int s = 0, int ms = 0)'''
        time = Time(1, 2, 3, 4)
        self.assertTrue(time.toString(), '01:02:03.004')

    def testConstructorWithThreeParamers(self):
        '''Constructor with 3 parameters: Time(int h, int m, int s = 0, int ms = 0)'''
        time = Time(1, 2, 3)
        self.assertTrue(time.toString(), '01:02:03.000')

    def testConstructorWithTwoParamers(self):
        '''Constructor with 2 parameters: Time(int h, int m, int s = 0, int ms = 0)'''
        time = Time(1, 2)
        self.assertTrue(time.toString(), '01:02:00.000')

    def testSimpleMethodWithoutParamers(self):
        '''Constructor without parameters: Time.setTime()'''
        time = Time(1, 2, 3, 4)
        time.setTime()
        self.assertTrue(time.isNull())

    def testSimpleMethodWithAllParamers(self):
        '''Simple method with all parameters: Time.setTime(int h, int m, int s = 0, int ms = 0)'''
        time = Time()
        time.setTime(1, 2, 3, 4)
        self.assertTrue(time.toString(), '01:02:03.004')

    def testSimpleMethodWithThreeParamers(self):
        '''Simple method with 3 parameters: Time.setTime(int h, int m, int s = 0, int ms = 0)'''
        time = Time()
        time.setTime(1, 2, 3)
        self.assertTrue(time.toString(), '01:02:03.000')

    def testSimpleMethodWithTwoParamers(self):
        '''Simple method with 2 parameters: Time.setTime(int h, int m, int s = 0, int ms = 0)'''
        time = Time()
        time.setTime(1, 2)
        self.assertTrue(time.toString(), '01:02:00.000')

    def testMethodWithoutParamers(self):
        '''Method without parameters: Time.somethingCompletelyDifferent()'''
        time = Time()
        result = time.somethingCompletelyDifferent()
        self.assertEqual(result, Time.ZeroArgs)

    def testMethodWithAllParamers(self):
        '''Method with all parameters:
        Time.somethingCompletelyDifferent(
            int h, int m, ImplicitConv ic = ImplicitConv::CtorThree, ObjectType* type = 0
        );
        '''
        time = Time()
        obj = ObjectType()
        result = time.somethingCompletelyDifferent(1, 2, ImplicitConv(2), obj)
        self.assertEqual(result, Time.FourArgs)

    def testMethodWithThreeParamers(self):
        '''Method with 3 parameters: Time.somethingCompletelyDifferent(...)'''
        time = Time()
        result = time.somethingCompletelyDifferent(1, 2, ImplicitConv(ImplicitConv.CtorOne))
        self.assertEqual(result, Time.ThreeArgs)

    def testMethodWithTwoParamers(self):
        '''Method with 2 parameters: Time.somethingCompletelyDifferent(...)'''
        time = Time()
        result = time.somethingCompletelyDifferent(1, 2)
        self.assertEqual(result, Time.TwoArgs)

    def testMethodWithThreeParamersAndImplicitConversion(self):
        '''Method with 3 parameters, the last one triggers an implicit conversion.'''
        time = Time()
        result = time.somethingCompletelyDifferent(1, 2, ImplicitConv.CtorOne)
        self.assertEqual(result, Time.ThreeArgs)

    # PYSIDE-1436: These tests crash at shutdown due to `assert(Not)?Equal`.
    def testCompareWithPythonTime(self):
        time = Time(12, 32, 5)
        py = datetime.time(12, 32, 5)
        self.assertEqual(time, py)

    def testNotEqual(self):
        time = Time(12, 32, 6)
        py = datetime.time(12, 32, 5)
        self.assertNotEqual(time, py)

if __name__ == '__main__':
    unittest.main()

