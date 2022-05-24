#!/usr/bin/env python
# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

'''Test cases for Point class'''

import os
import sys
import unittest

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
from shiboken_paths import init_paths
init_paths()

from sample import Point

class PointTest(unittest.TestCase):
    '''Test case for Point class, including operator overloads.'''

    def assertRaises(self, *args, **kwds):
        if not hasattr(sys, "pypy_version_info"):
            # PYSIDE-535: PyPy complains "Fatal RPython error: NotImplementedError"
            return super().assertRaises(*args, **kwds)

    def testConstructor(self):
        '''Test Point class constructor.'''
        pt = Point(5.0, 2.3)
        self.assertEqual(pt.x(), 5.0)
        self.assertEqual(pt.y(), 2.3)

    def testPlusOperator(self):
        '''Test Point class + operator.'''
        pt1 = Point(5.0, 2.3)
        pt2 = Point(0.5, 3.2)
        self.assertEqual(pt1 + pt2, Point(5.0 + 0.5, 2.3 + 3.2))

    def testEqualOperator(self):
        '''Test Point class == operator.'''
        pt1 = Point(5.0, 2.3)
        pt2 = Point(5.0, 2.3)
        pt3 = Point(0.5, 3.2)
        self.assertTrue(pt1 == pt1)
        self.assertTrue(pt1 == pt2)
        self.assertFalse(pt1 == pt3)
        self.assertFalse(pt1 == object())

    def testNotEqualOperator(self):
        '''Test Point class != operator.'''
        pt1 = Point(5.0, 2.3)
        pt2 = Point(5.0, 2.3)
        # This test no longer makes sense because we always supply default `==`, `!=`.
        #self.assertRaises(NotImplementedError, pt1.__ne__, pt2)
        # Since we use the default identity comparison, this results in `!=` .
        self.assertTrue(pt1 != pt2)

    def testReturnNewCopy(self):
        '''Point returns a copy of itself.'''
        pt1 = Point(1.1, 2.3)
        pt2 = pt1.copy()
        self.assertEqual(pt1, pt2)
        pt2 += pt1
        self.assertFalse(pt1 == pt2)

    @unittest.skipUnless(hasattr(sys, "getrefcount"), f"{sys.implementation.name} has no refcount")
    def testReturnConstPointer(self):
        '''Point returns a const pointer for itself.'''
        pt1 = Point(5.0, 2.3)
        refcount1 = sys.getrefcount(pt1)
        pt2 = pt1.getSelf()
        self.assertEqual(pt1, pt2)
        self.assertEqual(sys.getrefcount(pt1), refcount1 + 1)
        self.assertEqual(sys.getrefcount(pt1), sys.getrefcount(pt2))

    def testUintOverflow(self):
        pt1 = Point(0.0, 0.0)
        self.assertRaises(OverflowError, pt1.setXAsUint, 840835495615213080)
        self.assertEqual(pt1.x(), 0.0)

    def testAddedOperator(self):
        p = Point(0.0, 0.0)
        r = p - 'Hi'
        self.assertEqual(r, 'Hi')

        # now the reverse op.
        r = 'Hi' - p
        self.assertEqual(r, 'Hi')

    def testModifiedMethod(self):
        pt1 = Point(0.0, 0.0)
        pt2 = Point(10.0, 10.0)
        expected = Point((pt1.x() + pt2.x()) / 2.0, (pt1.y() + pt2.y()) / 2.0)
        self.assertEqual(pt1.midpoint(pt2), expected)

if __name__ == '__main__':
    unittest.main()
