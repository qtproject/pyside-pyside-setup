#!/usr/bin/env python
# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

'''The BlackBox class has cases of ownership transference between Python and C++.'''

import os
import sys
import unittest

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
from shiboken_paths import init_paths
init_paths()

from sample import Point, BlackBox

class OwnershipInvalidateNonPolymorphicTest(unittest.TestCase):
    '''The BlackBox class has cases of ownership transference between Python and C++.'''

    def testOwnershipTransference(self):
        '''Ownership transference from Python to C++ and back again.'''
        p1 = Point(10, 20)
        bb = BlackBox()
        p1_ticket = bb.keepPoint(p1)
        self.assertRaises(RuntimeError, p1.x)
        p1_ret = bb.retrievePoint(p1_ticket)
        self.assertEqual(p1_ret, Point(10, 20))

if __name__ == '__main__':
    unittest.main()

