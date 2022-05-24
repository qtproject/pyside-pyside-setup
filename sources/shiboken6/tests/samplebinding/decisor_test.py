#!/usr/bin/env python
# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

'''Test cases for the method overload decisor.'''

import os
import sys
import unittest

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
from shiboken_paths import init_paths
init_paths()

from sample import SampleNamespace, Point, ObjectType, ObjectModel

class DecisorTest(unittest.TestCase):
    '''Test cases for the method overload decisor.'''

    def testCallWithInvalidParametersSideA(self):
        '''Call a method missing with the last argument missing.
        This can trigger the bug #262, which means using an argument
        not provided by the user.'''
        pt = Point()
        # This exception may move from a TypeError to a ValueError.
        self.assertRaises((TypeError, ValueError), SampleNamespace.forceDecisorSideA, pt)

    def testCallWithInvalidParametersSideB(self):
        '''Same as the previous test, but with an integer as first argument,
        just to complicate things for the overload method decisor.'''
        pt = Point()
        # This exception may move from a TypeError to a ValueError.
        self.assertRaises((TypeError, ValueError), SampleNamespace.forceDecisorSideB, 1, pt)

    def testDecideCallWithInheritance(self):
        '''Call methods overloads that receive parent and inheritor classes' instances.'''
        objecttype = ObjectType()
        objectmodel = ObjectModel()
        self.assertEqual(ObjectModel.receivesObjectTypeFamily(objecttype), ObjectModel.ObjectTypeCalled)
        self.assertNotEqual(ObjectModel.receivesObjectTypeFamily(objecttype), ObjectModel.ObjectModelCalled)
        self.assertEqual(ObjectModel.receivesObjectTypeFamily(objectmodel), ObjectModel.ObjectModelCalled)
        self.assertNotEqual(ObjectModel.receivesObjectTypeFamily(objectmodel), ObjectModel.ObjectTypeCalled)

if __name__ == '__main__':
    unittest.main()

