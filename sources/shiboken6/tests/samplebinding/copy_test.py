#!/usr/bin/env python
# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

'''Test cases for deep copy of objects'''

import copy
import os
import sys
import unittest

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
from shiboken_paths import init_paths
init_paths()

try:
    import cPickle as pickle
except ImportError:
    import pickle


from sample import Point


class SimpleCopy(unittest.TestCase):
    '''Simple copy of objects'''

    def testCopy(self):
        point = Point(0.1, 2.4)
        new_point = copy.copy(point)

        self.assertTrue(point is not new_point)
        self.assertEqual(point, new_point)


class DeepCopy(unittest.TestCase):
    '''Deep copy with shiboken objects'''

    def testDeepCopy(self):
        '''Deep copy of value types'''
        point = Point(3.1, 4.2)
        new_point = copy.deepcopy([point])[0]

        self.assertTrue(point is not new_point)
        self.assertEqual(point, new_point)


class PicklingTest(unittest.TestCase):
    '''Support pickling'''

    def testSimple(self):
        '''Simple pickling and unpickling'''

        point = Point(10.2, 43.5)

        data = pickle.dumps(point)
        new_point = pickle.loads(data)

        self.assertEqual(point, new_point)
        self.assertTrue(point is not new_point)


if __name__ == '__main__':
    unittest.main()

