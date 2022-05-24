#!/usr/bin/env python
# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

'''Test cases for Complex class'''

import os
import sys
import unittest

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
from shiboken_paths import init_paths
init_paths()

import sample
from sample import Point

class ComplexTest(unittest.TestCase):
    '''Test case for conversions between C++ Complex class to Python complex class'''

    def testFunctionReturningComplexObject(self):
        '''Test function returning a C++ Complex object.'''
        cpx = sample.transmutePointIntoComplex(Point(5.0, 2.3))
        self.assertEqual(cpx, complex(5.0, 2.3))

    def testFunctionReceivingComplexObjectAsArgument(self):
        '''Test function returning a C++ Complex object.'''
        pt = sample.transmuteComplexIntoPoint(complex(1.2, 3.4))
        # these assertions intentionally avoids to test the == operator,
        # it should have its own test cases.
        self.assertEqual(pt.x(), 1.2)
        self.assertEqual(pt.y(), 3.4)

    def testComplexList(self):
        '''Test list of C++ Complex objects conversion to a list of Python complex objects.'''
        # the global function gimmeComplexList() is expected to return a list
        # containing the following Complex values: [0j, 1.1+2.2j, 1.3+2.4j]
        cpxlist = sample.gimmeComplexList()
        self.assertEqual(cpxlist, [complex(), complex(1.1, 2.2), complex(1.3, 2.4)])

    def testSumComplexPair(self):
        '''Test sum of a tuple containing two complex objects.'''
        cpx1 = complex(1.2, 3.4)
        cpx2 = complex(5.6, 7.8)
        self.assertEqual(sample.sumComplexPair((cpx1, cpx2)), cpx1 + cpx2)

    def testUsingTuples(self):
        cpx1, cpx2 = (1.2, 3.4), (5.6, 7.8)
        self.assertEqual(sample.sumComplexPair((cpx1, cpx2)), sample.sumComplexPair((complex(*cpx1), complex(*cpx2))))
        cpx1, cpx2 = (1, 3), (5, 7)
        self.assertEqual(sample.sumComplexPair((cpx1, cpx2)), sample.sumComplexPair((complex(*cpx1), complex(*cpx2))))
        cpx1, cpx2 = (1.2, 3), (5.6, 7)
        self.assertEqual(sample.sumComplexPair((cpx1, cpx2)), sample.sumComplexPair((complex(*cpx1), complex(*cpx2))))
        cpx1, cpx2 = (1, 2, 3), (4, 5, 7)
        self.assertRaises(TypeError, sample.sumComplexPair, (cpx1, cpx2))
        cpx1, cpx2 = ('1', '2'), ('4', '5')
        self.assertRaises(TypeError, sample.sumComplexPair, (cpx1, cpx2))


if __name__ == '__main__':
    unittest.main()

