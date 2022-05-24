#!/usr/bin/env python
# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

'''Test cases for added functions with nested and multi-argument container types.'''

import os
import sys
import unittest

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
from shiboken_paths import init_paths
init_paths()
from sample import sum2d, sumproduct

class TestAddedFunctionsWithContainerArgs(unittest.TestCase):
    '''Tests added functions with nested and multi-argument container types.'''

    def testNestedContainerType(self):
        '''Test added function with single-argument containers.'''
        values = [[1,2],[3,4,5],[6]]
        self.assertEqual(sum2d(values), 21)

    def testMultiArgContainerType(self):
        '''Test added function with a two-argument container.'''
        values = [(1,2),(3,4),(5,6)]
        self.assertEqual(sumproduct(values), 44)

if __name__ == '__main__':
    unittest.main()
