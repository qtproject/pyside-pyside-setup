#!/usr/bin/env python
# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

import gc
import os
import sys
import unittest

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
from shiboken_paths import init_paths
init_paths()
from smart import Integer, Integer2, StdUniquePtrTestBench, StdUniquePtrVirtualMethodTester, std


def call_func_on_ptr(ptr):
    ptr.printInteger()


class VirtualTester(StdUniquePtrVirtualMethodTester):

    def doCreateInteger(self, v):
        iv = Integer()  # Construct from pointee
        iv.setValue(2 * v)
        return std.unique_ptr_Integer(iv)

    def doModifyIntegerByRef(self, p):
        return 2 * p.value()

    def doModifyIntegerByValue(self, p):
        return 2 * p.value()


class StdUniquePtrTests(unittest.TestCase):
    def testInteger(self):
        p = StdUniquePtrTestBench.createInteger()
        StdUniquePtrTestBench.printInteger(p)  # unique_ptr by ref
        self.assertTrue(p)

        call_func_on_ptr(p)
        self.assertTrue(p)

        StdUniquePtrTestBench.takeInteger(p)  # unique_ptr by value, takes pointee
        self.assertFalse(p)

        np = StdUniquePtrTestBench.createNullInteger()
        StdUniquePtrTestBench.printInteger(np)
        self.assertFalse(np)
        self.assertRaises(AttributeError, call_func_on_ptr, np)

        iv = Integer()  # Construct from pointee
        iv.setValue(42)
        np = std.unique_ptr_Integer(iv)
        self.assertEqual(np.value(), 42)

    def test_derived(self):
        iv2 = Integer2()  # Construct from pointee
        iv2.setValue(42)
        p = std.unique_ptr_Smart_Integer2(iv2)
        self.assertEqual(p.value(), 42)
        StdUniquePtrTestBench.printInteger2(p)  # unique_ptr by ref
        self.assertTrue(p)
        StdUniquePtrTestBench.printInteger(p)  # conversion
        # FIXME: This fails, pointer is moved in value conversion
        # self.assertTrue(p)

    def testInt(self):
        p = StdUniquePtrTestBench.createInt()  # unique_ptr by ref
        StdUniquePtrTestBench.printInt(p)
        StdUniquePtrTestBench.takeInt(p)  # unique_ptr by value, takes pointee
        self.assertFalse(p)

        np = StdUniquePtrTestBench.createNullInt()
        StdUniquePtrTestBench.printInt(np)
        self.assertFalse(np)

    def testVirtuals(self):
        """Test whether code generating virtual function overrides is generated
           correctly."""
        p = StdUniquePtrTestBench.createInteger()
        p.setValue(42)
        v = StdUniquePtrVirtualMethodTester()
        self.assertTrue(v.testCreateInteger(42, 42))
        self.assertTrue(v.testModifyIntegerByRef(42, 43))  # Default implementation increments
        self.assertTrue(v.testModifyIntegerValue(42, 43))

        v = VirtualTester()  # Reimplemented methods double values
        self.assertTrue(v.testCreateInteger(42, 84))
        self.assertTrue(v.testModifyIntegerByRef(42, 84))
        self.assertTrue(v.testModifyIntegerValue(42, 84))


if __name__ == '__main__':
    unittest.main()
