#!/usr/bin/env python
# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

'''Test cases for PointF class'''

import os
import sys
import unittest

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
from shiboken_paths import init_paths
init_paths()

from sample import PointF

class PointFTest(unittest.TestCase):
    '''Test case for PointF class, including operator overloads.'''

    def testConstructor(self):
        '''Test PointF class constructor.'''
        pt = PointF(5.0, 2.3)
        self.assertEqual(pt.x(), 5.0)
        self.assertEqual(pt.y(), 2.3)

    def testPlusOperator(self):
        '''Test PointF class + operator.'''
        pt1 = PointF(5.0, 2.3)
        pt2 = PointF(0.5, 3.2)
        self.assertEqual(pt1 + pt2, PointF(5.0 + 0.5, 2.3 + 3.2))

    def testEqualOperator(self):
        '''Test PointF class == operator.'''
        pt1 = PointF(5.0, 2.3)
        pt2 = PointF(5.0, 2.3)
        pt3 = PointF(0.5, 3.2)
        self.assertTrue(pt1 == pt1)
        self.assertTrue(pt1 == pt2)
        self.assertFalse(pt1 == pt3)

    def testModifiedMethod(self):
        pt1 = PointF(0.0, 0.0)
        pt2 = PointF(10.0, 10.0)
        expected = PointF((pt1.x() + pt2.x()) / 2.0, (pt1.y() + pt2.y()) / 2.0)
        self.assertEqual(pt1.midpoint(pt2), expected)

if __name__ == '__main__':
    unittest.main()
