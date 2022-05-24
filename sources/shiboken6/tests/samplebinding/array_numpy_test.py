#!/usr/bin/env python
# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

'''Test case for NumPy Array types.'''

import os
import sys
import unittest

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
from shiboken_paths import init_paths
init_paths()
import sample

hasNumPy = False

try:
    import numpy
    hasNumPy = True
except ImportError:
    pass

class ArrayTester(unittest.TestCase):
    '''Test case for NumPy arrays.'''

    def testIntArray(self):
        intList = numpy.array([1, 2, 3, 4], dtype = 'int32')
        self.assertEqual(sample.sumIntArray(intList), 10)

    def testDoubleArray(self):
        doubleList = numpy.array([1, 2, 3, 4], dtype = 'double')
        self.assertEqual(sample.sumDoubleArray(doubleList), 10)

    def testIntMatrix(self):
        intMatrix = numpy.array([[1, 2, 3], [4, 5, 6]], dtype = 'int32')
        self.assertEqual(sample.sumIntMatrix(intMatrix), 21)

    def testDoubleMatrix(self):
        doubleMatrix = numpy.array([[1, 2, 3], [4, 5, 6]], dtype = 'double')
        self.assertEqual(sample.sumDoubleMatrix(doubleMatrix), 21)

if __name__ == '__main__' and hasNumPy:
    unittest.main()
