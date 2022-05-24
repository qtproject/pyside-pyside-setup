#!/usr/bin/env python
# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

'''Test cases for added functions.'''

import os
import sys
import unittest

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
from shiboken_paths import init_paths
init_paths()
from sample import SampleNamespace, ObjectType, Point

class TestAddedFunctionsWithSimilarTypes(unittest.TestCase):
    '''Adds new signatures very similar to already existing ones.'''

    def testValueTypeReferenceAndValue(self):
        '''In C++ we have "function(const ValueType&, double)",
        in Python we add "function(ValueType)".'''
        point = Point(10, 20)
        multiplier = 4.0
        control = (point.x() + point.y()) * multiplier
        self.assertEqual(SampleNamespace.passReferenceToValueType(point, multiplier), control)
        control = point.x() + point.y()
        self.assertEqual(SampleNamespace.passReferenceToValueType(point), control)

    def testObjectTypeReferenceAndPointer(self):
        '''In C++ we have "function(const ObjectType&, int)",
        in Python we add "function(ValueType)".'''
        obj = ObjectType()
        obj.setObjectName('sbrubbles')
        multiplier = 3.0
        control = len(obj.objectName()) * multiplier
        self.assertEqual(SampleNamespace.passReferenceToObjectType(obj, multiplier), control)
        control = len(obj.objectName())
        self.assertEqual(SampleNamespace.passReferenceToObjectType(obj), control)

if __name__ == '__main__':
    unittest.main()
