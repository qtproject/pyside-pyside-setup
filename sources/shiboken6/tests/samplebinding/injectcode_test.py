#!/usr/bin/env python
# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

'''Test cases for std::list container conversions'''

import os
import sys
import unittest

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
from shiboken_paths import init_paths
init_paths()
from sample import InjectCode

class MyInjectCode(InjectCode):
    def __init__(self):
        InjectCode.__init__(self)
        self.multiplier = 2

    def arrayMethod(self, values):
        return self.multiplier * sum(values)

class InjectCodeTest(unittest.TestCase):

    @unittest.skipIf(hasattr(sys, "pypy_version_info"),
                             "PyPy type objects cannot be modified (yet) after creation")
    def testTypeNativeBeginning_TypeTargetBeginning(self):
        ic = InjectCode()
        self.assertEqual(str(ic), "Hi! I'm the inject code dummy class.")

    def testFunctionTargetBeginning_FunctionTargetEnd(self):
        ic = InjectCode()
        ret = ic.simpleMethod1(2, 1)
        self.assertEqual(ret, "4end")
        ret = ic.simpleMethod1(4, 2)
        self.assertEqual(ret, "7end")

    def testFunctionTargetBeginning(self):
        ic = InjectCode()
        ret = ic.simpleMethod2()
        self.assertEqual(ret, "_end")

    def testArgsModification(self):
        ic = InjectCode()
        ret = ic.overloadedMethod(["1", "2", "3", "4"])
        self.assertEqual(ret, "1234")
        ret = ic.overloadedMethod(2, 0.5)
        self.assertEqual(ret, "2.5")
        ret = ic.overloadedMethod(6, True)
        self.assertEqual(ret, "6true")

    def testArgsModification2(self):
        ic = InjectCode()
        ret = ic.simpleMethod3(["1", "2", "3", "4"])
        self.assertEqual(ret, "1234")

    def testArgumentRemovalAndArgumentTypeModification(self):
        '''A method has its first argument removed and the second modified.'''
        ic = InjectCode()
        values = (1, 2, 3, 4, 5)
        result = ic.arrayMethod(values)
        self.assertEqual(result, sum(values))

    def testCallVirtualMethodWithArgumentRemovalAndArgumentTypeModification(self):
        '''A virtual method has its first argument removed and the second modified.'''
        ic = InjectCode()
        values = (1, 2, 3, 4, 5)
        result = ic.callArrayMethod(values)
        self.assertEqual(result, sum(values))

    def testCallReimplementedVirtualMethodWithArgumentRemovalAndArgumentTypeModification(self):
        '''Calls a reimplemented virtual method that had its first argument removed and the second modified.'''
        ic = MyInjectCode()
        values = (1, 2, 3, 4, 5)
        result = ic.callArrayMethod(values)
        self.assertEqual(result, ic.multiplier * sum(values))

    def testUsageOfTypeSystemCheckVariableOnPrimitiveType(self):
        '''When the sequence item is convertible to an integer -1 is returned, or -2 if its not convertible.'''
        ic = InjectCode()
        values = (1, 2, 3, 4, '5', 6.7)
        result = ic.arrayMethod(values)

        fixedValues = [v for v in values if isinstance(v, int)]\
                    + [-1 for v in values if isinstance(v, float)]\
                    + [-2 for v in values if not isinstance(v, int) and not isinstance(v, float)]
        self.assertEqual(result, sum(fixedValues))


class IntArrayTest(unittest.TestCase):
    '''Test case for converting python sequence to int array'''

    def testBasic(self):
        '''Shiboken::sequenceToIntArray - basic case'''
        args = [1, 2, 3, 4]
        ic = InjectCode()
        self.assertEqual(sum(args) + len(args), ic.sumArrayAndLength(args))

    def testEmpty(self):
        '''Shiboken::sequenceToIntArray - empty sequence'''
        args = []
        ic = InjectCode()
        self.assertEqual(sum(args) + len(args), ic.sumArrayAndLength(args))

    def testWithZero(self):
        '''Shiboken::sequenceToIntArray - count only up to zero'''
        args = [1, 2, 0, 3]
        ic = InjectCode()
        self.assertEqual(sum([1, 2]) + len([1, 2]), ic.sumArrayAndLength(args))

if __name__ == '__main__':
    unittest.main()
