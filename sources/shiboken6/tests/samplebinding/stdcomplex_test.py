#!/usr/bin/env python
# Copyright (C) 2023 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

'''Test cases for StdComplex class'''

import os
import math
import sys
import unittest

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
from shiboken_paths import init_paths
init_paths()

from sample import StdComplex


REAL = 5.0
IMAG = 2.3


class StdComplexTest(unittest.TestCase):
    '''Test case for StdComplex class, exercising esoteric number
       protocols (Py_nb_). For standard number protocols, see Point.'''

    def testConversion(self):
        pt = StdComplex(REAL, IMAG)
        self.assertEqual(int(pt), int(round(pt.abs_value())))
        self.assertEqual(float(pt), pt.abs_value())

    def testAbs(self):
        pt = StdComplex(REAL, IMAG)
        self.assertEqual(abs(pt), pt.abs_value())

    def testPow(self):
        '''Compare pow() function to builtin Python type.'''
        pt = StdComplex(REAL, IMAG)
        result = pow(pt, StdComplex(2.0, 0))
        py_pt = complex(REAL, IMAG)
        py_result = pow(py_pt, complex(2.0, 0))
        self.assertAlmostEqual(result.real(), py_result.real)
        self.assertAlmostEqual(result.imag(), py_result.imag)

    def testFloor(self):
        pt = StdComplex(REAL, IMAG)
        self.assertEqual(math.floor(pt), math.floor(pt.abs_value()))

    def testCeil(self):
        pt = StdComplex(REAL, IMAG)
        self.assertEqual(math.ceil(pt), math.ceil(pt.abs_value()))

    def testPlusOperator(self):
        '''Test StdComplex class + operator.'''
        pt1 = StdComplex(REAL, IMAG)
        pt2 = StdComplex(0.5, 3.2)
        self.assertEqual(pt1 + pt2, StdComplex(REAL + 0.5, IMAG + 3.2))

    def testEqualOperator(self):
        '''Test StdComplex class == operator.'''
        pt1 = StdComplex(REAL, IMAG)
        pt2 = StdComplex(REAL, IMAG)
        pt3 = StdComplex(0.5, 3.2)
        self.assertTrue(pt1 == pt1)
        self.assertTrue(pt1 == pt2)
        self.assertFalse(pt1 == pt3)


if __name__ == '__main__':
    unittest.main()
