#!/usr/bin/env python
# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

'''Test cases for operator overloads on Size class'''

import os
import sys
import unittest

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
from shiboken_paths import init_paths
init_paths()

from sample import Size

class PointTest(unittest.TestCase):
    '''Test case for Size class, including operator overloads.'''

    def testConstructor(self):
        '''Test Size class constructor.'''
        width, height = (5.0, 2.3)
        size = Size(width, height)
        self.assertEqual(size.width(), width)
        self.assertEqual(size.height(), height)
        self.assertEqual(size.calculateArea(), width * height)

    def testCopyConstructor(self):
        '''Test Size class copy constructor.'''
        width, height = (5.0, 2.3)
        s1 = Size(width, height)
        s2 = Size(s1)
        self.assertFalse(s1 is s2)
        self.assertEqual(s1, s2)

    def testPlusOperator(self):
        '''Test Size class + operator.'''
        s1 = Size(5.0, 2.3)
        s2 = Size(0.5, 3.2)
        self.assertEqual(s1 + s2, Size(5.0 + 0.5, 2.3 + 3.2))

    def testEqualOperator(self):
        '''Test Size class == operator.'''
        s1 = Size(5.0, 2.3)
        s2 = Size(5.0, 2.3)
        s3 = Size(0.5, 3.2)
        self.assertTrue(s1 == s1)
        self.assertTrue(s1 == s2)
        self.assertFalse(s1 == s3)

    def testNotEqualOperator(self):
        '''Test Size class != operator.'''
        s1 = Size(5.0, 2.3)
        s2 = Size(5.0, 2.3)
        s3 = Size(0.5, 3.2)
        self.assertFalse(s1 != s1)
        self.assertFalse(s1 != s2)
        self.assertTrue(s1 != s3)

    def testMinorEqualOperator(self):
        '''Test Size class <= operator.'''
        s1 = Size(5.0, 2.3)
        s2 = Size(5.0, 2.3)
        s3 = Size(0.5, 3.2)
        self.assertTrue(s1 <= s1)
        self.assertTrue(s1 <= s2)
        self.assertTrue(s3 <= s1)
        self.assertFalse(s1 <= s3)

    def testMinorOperator(self):
        '''Test Size class < operator.'''
        s1 = Size(5.0, 2.3)
        s2 = Size(0.5, 3.2)
        self.assertFalse(s1 < s1)
        self.assertFalse(s1 < s2)
        self.assertTrue(s2 < s1)

    def testMajorEqualOperator(self):
        '''Test Size class >= operator.'''
        s1 = Size(5.0, 2.3)
        s2 = Size(5.0, 2.3)
        s3 = Size(0.5, 3.2)
        self.assertTrue(s1 >= s1)
        self.assertTrue(s1 >= s2)
        self.assertTrue(s1 >= s3)
        self.assertFalse(s3 >= s1)

    def testMajorOperator(self):
        '''Test Size class > operator.'''
        s1 = Size(5.0, 2.3)
        s2 = Size(0.5, 3.2)
        self.assertFalse(s1 > s1)
        self.assertTrue(s1 > s2)
        self.assertFalse(s2 > s1)

if __name__ == '__main__':
    unittest.main()

