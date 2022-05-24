#!/usr/bin/env python
# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

'''Test cases for argument modification with more than nine arguments.'''

import os
import sys
import unittest

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
from shiboken_paths import init_paths
init_paths()

from sample import Point, applyHomogeneousTransform

class TransformTest(unittest.TestCase):
    '''Test cases for modifying a function with > 9 arguments.'''

    def testTransform_ValidMatrix(self):
        '''Transform applies successfully.'''
        p = Point(3, 4)
        r = applyHomogeneousTransform(p, 0, 1, 0, -1, 0, 0, 0, 0, 1)
        self.assertTrue(type(r) is Point)
        self.assertEqual(r.x(), 4)
        self.assertEqual(r.y(), -3)

    def testTransform_InvalidMatrix(self):
        '''Transform does not apply successfully.'''
        p = Point(3, 4)
        r = applyHomogeneousTransform(p, 1, 0, 0, 0, 1, 0, 0, 0, 0)
        self.assertTrue(r is None)

if __name__ == '__main__':
    unittest.main()
