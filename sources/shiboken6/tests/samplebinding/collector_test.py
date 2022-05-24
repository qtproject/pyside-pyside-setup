#!/usr/bin/env python
# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

'''Test cases for Collector class' shift operators.'''

import os
import sys
import unittest

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
from shiboken_paths import init_paths
init_paths()

from sample import Collector, IntWrapper, ObjectType


class CollectorTest(unittest.TestCase):
    '''Test cases for Collector class' shift operators.'''

    def testLShiftOperatorSingleUse(self):
        '''Test case for using the Collector.__lshift__ operator just one time.'''
        collector = Collector()
        collector << 13
        self.assertEqual(collector.size(), 1)
        self.assertEqual(collector.items(), [13])

    def testLShiftOperatorMultipleUses(self):
        '''Test case for using the Collector.__lshift__ operator many times in the same line.'''
        collector = Collector()
        collector << 2 << 3 << 5 << 7 << 11
        self.assertEqual(collector.size(), 5)
        self.assertEqual(collector.items(), [2, 3, 5, 7, 11])

class CollectorExternalOperator(unittest.TestCase):
    '''Test cases for external operators of Collector'''

    def testLShiftExternal(self):
        '''Collector external operator'''
        collector = Collector()
        collector << IntWrapper(5)
        self.assertEqual(collector.size(), 1)
        self.assertEqual(collector.items(), [5])


class CollectorObjectType(unittest.TestCase):
    '''Test cases for Collector ObjectType'''

    def testBasic(self):
        '''Collector << ObjectType # greedy collector'''
        collector = Collector()
        obj = ObjectType()
        collector << obj
        self.assertEqual(collector.items()[0], obj.identifier())


if __name__ == '__main__':
    unittest.main()

