#!/usr/bin/env python
# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

'''Wrapper validity tests for arguments.'''

import os
import sys
import unittest

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
from shiboken_paths import init_paths
init_paths()

from sample import Polygon, Point

class WrapperValidityOfArgumentsTest(unittest.TestCase):
    '''Wrapper validity tests for arguments.'''

    def testInvalidArgumentToMethod(self):
        '''Call to method using invalidated Python wrapper as argument should raise RuntimeError.'''
        poly = Polygon()
        Polygon.stealOwnershipFromPython(poly)
        self.assertRaises(RuntimeError, Polygon.doublePolygonScale, poly)

    def testInvalidArgumentToConstructor(self):
        '''Call to constructor using invalidated Python wrapper as argument should raise RuntimeError.'''
        pt = Point(1, 2)
        Polygon.stealOwnershipFromPython(pt)
        self.assertRaises(RuntimeError, Polygon, pt)

    def testInvalidArgumentWithImplicitConversion(self):
        '''Call to method using invalidated Python wrapper to be implicitly converted should raise RuntimeError.'''
        pt = Point(1, 2)
        Polygon.stealOwnershipFromPython(pt)
        self.assertRaises(RuntimeError, Polygon.doublePolygonScale, pt)

if __name__ == '__main__':
    unittest.main()

