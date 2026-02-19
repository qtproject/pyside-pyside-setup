#!/usr/bin/env python
# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0
from __future__ import annotations

'''Test cases for the method overload decisor.'''

import os
import sys
import unittest

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
from shiboken_paths import init_paths
init_paths()

from sample import asciiCode, SampleNamespace, Point, ObjectType, ObjectModel


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
        self.assertEqual(ObjectModel.receivesObjectTypeFamily(objecttype),
                         ObjectModel.MethodCalled.ObjectTypeCalled)
        self.assertNotEqual(ObjectModel.receivesObjectTypeFamily(objecttype),
                            ObjectModel.MethodCalled.ObjectModelCalled)
        self.assertEqual(ObjectModel.receivesObjectTypeFamily(objectmodel),
                         ObjectModel.MethodCalled.ObjectModelCalled)
        self.assertNotEqual(ObjectModel.receivesObjectTypeFamily(objectmodel),
                            ObjectModel.MethodCalled.ObjectTypeCalled)

    def testKeywordArguments(self):
        '''PYSIDE-3281: Test the complex SbkChar type check expression in conjunction with
           keyword arguments.'''
        self.assertEqual(asciiCode("a"), ord('a'))  # Default parameter "a"
        self.assertEqual(asciiCode("b"), ord('b'))  # Positional
        self.assertEqual(asciiCode(character="b"), ord('b'))  # Keyword


if __name__ == '__main__':
    unittest.main()
