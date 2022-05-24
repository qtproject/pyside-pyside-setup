#!/usr/bin/env python
# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

'''Test cases for Collector shift operators defined in other modules.'''

import os
import sys
import unittest

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
from shiboken_paths import init_paths
init_paths()

from sample import Collector, ObjectType
from other import OtherObjectType

class CollectorOtherObjectType(unittest.TestCase):
    '''Test cases for Collector << OtherObjectType'''

    def testLShiftWithExpectedType(self):
        '''Collector << ObjectType # libsample << operator'''
        collector = Collector()
        obj = ObjectType()
        collector << obj
        self.assertEqual(collector.items()[0], obj.identifier())

    def testOtherReversal(self):
        '''Collector << OtherObjectType # libother << operator'''
        collector = Collector()
        obj = OtherObjectType()
        collector << obj
        self.assertEqual(collector.items()[0], obj.identifier() * 2)

if __name__ == '__main__':
    unittest.main()

