#!/usr/bin/env python
# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

'''Test case for Array types (PySequence).'''

import os
import sys
import unittest

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
from shiboken_paths import init_paths
init_paths()
import sample

class ArrayTester(unittest.TestCase):
    '''Test case for arrays.'''

    def testIntArray(self):
        intList = [1, 2, 3, 4]
        self.assertEqual(sample.sumIntArray(intList), 10)

    def testIntArrayModified(self):
        intList = [1, 2, 3, 4]
        tester = sample.ArrayModifyTest()
        self.assertEqual(tester.sumIntArray(4, intList), 10)

    def testDoubleArray(self):
        doubleList = [1.2, 2.3, 3.4, 4.5]
        self.assertEqual(sample.sumDoubleArray(doubleList), 11.4)

if __name__ == '__main__':
    unittest.main()
