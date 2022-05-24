#!/usr/bin/env python
# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

'''Test cases for libsample's Point multiply operator defined in libother module.'''

import os
import sys
import unittest

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
from shiboken_paths import init_paths
init_paths()

from sample import Point
from other import Number

class PointOperationsWithNumber(unittest.TestCase):
    '''Test cases for libsample's Point multiply operator defined in libother module.'''

    def testPointTimesInt(self):
        '''sample.Point * int'''
        pt1 = Point(2, 7)
        num = 3
        pt2 = Point(pt1.x() * num, pt1.y() * num)
        self.assertEqual(pt1 * num, pt2)

    def testIntTimesPoint(self):
        '''int * sample.Point'''
        pt1 = Point(2, 7)
        num = 3
        pt2 = Point(pt1.x() * num, pt1.y() * num)
        self.assertEqual(num * pt1, pt2)

    def testPointTimesNumber(self):
        '''sample.Point * other.Number'''
        pt = Point(2, 7)
        num = Number(11)
        self.assertEqual(pt * num.value(), pt * 11)

if __name__ == '__main__':
    unittest.main()

