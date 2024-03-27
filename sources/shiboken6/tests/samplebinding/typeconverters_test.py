#!/usr/bin/env python
# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

'''Tests various usages of the type converters.'''

import os
import sys
import unittest

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
from shiboken_paths import init_paths
init_paths()

import sample


class GetPythonTypeByNameTest(unittest.TestCase):

    '''Uses an added function with inject code that uses the libshiboken
    function "Shiboken::Conversions::getPythonTypeObject(typeName)".'''

    def testGetObjectType(self):
        pyType1 = sample.getPythonType('ObjectType')
        self.assertEqual(pyType1, sample.ObjectType)
        pyType2 = sample.getPythonType('ObjectType*')
        self.assertEqual(pyType2, sample.ObjectType)
        self.assertEqual(pyType1, pyType2)

    def testGetValueType(self):
        pyType1 = sample.getPythonType('Point')
        self.assertEqual(pyType1, sample.Point)
        pyType2 = sample.getPythonType('Point*')
        self.assertEqual(pyType2, sample.Point)
        self.assertEqual(pyType1, pyType2)

    def testGetUsersPrimitiveType(self):
        pyType = sample.getPythonType('OddBool')
        self.assertEqual(pyType, bool)

    def testGetUsersPrimitiveTypeWithoutTargetLangApiName(self):
        '''If the primitive type attribute "target-lang-api-name" is not set
        there'll be no Python type associated with the C++ type.'''
        pyType = sample.getPythonType('PStr')
        self.assertEqual(pyType, None)

    def testPrimitiveTypeAndTypedef(self):
        pyType = sample.getPythonType('double')
        self.assertEqual(pyType, float)
        pyTypedef = sample.getPythonType('real')
        self.assertEqual(pyType, pyTypedef)

    def testPairContainerType(self):
        pyType = sample.getPythonType('std::pair<Complex,int>')
        self.assertEqual(pyType, list)

    def testListContainerType(self):
        pyType = sample.getPythonType('std::list<int>')
        self.assertEqual(pyType, list)

    def testMapContainerType(self):
        pyType = sample.getPythonType('std::map<std::string,int>')
        self.assertEqual(pyType, dict)

    def testGlobalEnumType(self):
        pyType = sample.getPythonType('GlobalEnum')
        self.assertEqual(pyType, sample.GlobalEnum)

    def testScopedEnumType(self):
        pyType = sample.getPythonType('Abstract::Type')
        self.assertEqual(pyType, sample.Abstract.Type)


class CheckValueAndObjectTypeByNameTest(unittest.TestCase):

    '''Uses an added function with inject code that uses the libshiboken
    functions that check if a type is Object or Value, based on its converter.'''

    def testErrors(self):
        '''not existent type'''
        self.assertRaises(ValueError, sample.cppTypeIsValueType, 'NotExistentType')
        self.assertRaises(ValueError, sample.cppTypeIsObjectType, 'NotExistentType')

    def testObjectType1(self):
        self.assertTrue(sample.cppTypeIsObjectType('ObjectType'))
        self.assertFalse(sample.cppTypeIsValueType('ObjectType'))

    def testObjectType2(self):
        self.assertTrue(sample.cppTypeIsObjectType('ObjectType*'))
        self.assertFalse(sample.cppTypeIsValueType('ObjectType*'))

    def testValueType1(self):
        self.assertTrue(sample.cppTypeIsValueType('Point'))
        self.assertFalse(sample.cppTypeIsObjectType('Point'))

    def testValueType2(self):
        self.assertTrue(sample.cppTypeIsValueType('Point*'))
        self.assertFalse(sample.cppTypeIsObjectType('Point*'))

    def testUsersPrimitiveType(self):
        self.assertFalse(sample.cppTypeIsValueType('Complex'))
        self.assertFalse(sample.cppTypeIsObjectType('Complex'))

    def testContainerType(self):
        self.assertFalse(sample.cppTypeIsValueType('std::list<int>'))
        self.assertFalse(sample.cppTypeIsObjectType('std::list<int>'))


class SpecificConverterTest(unittest.TestCase):

    '''Uses an added function with inject code that uses the libshiboken
    adapter class "Shiboken::Conversions::SpecificConverter".'''

    def testNotExistentType(self):
        conversion = sample.getConversionTypeString('NotExistentType')
        self.assertEqual(conversion, 'Invalid conversion')

    def testObjectType(self):
        conversion = sample.getConversionTypeString('ObjectType')
        self.assertEqual(conversion, 'Pointer conversion')
        conversion = sample.getConversionTypeString('ObjectType*')
        self.assertEqual(conversion, 'Pointer conversion')
        conversion = sample.getConversionTypeString('ObjectType&')
        self.assertEqual(conversion, 'Reference conversion')

    def testValueType(self):
        conversion = sample.getConversionTypeString('Point')
        self.assertEqual(conversion, 'Copy conversion')
        conversion = sample.getConversionTypeString('Point*')
        self.assertEqual(conversion, 'Pointer conversion')
        conversion = sample.getConversionTypeString('Point&')
        self.assertEqual(conversion, 'Reference conversion')


class StringBasedConversionTest(unittest.TestCase):

    def testValueType(self):
        pts = (sample.Point(1, 1), sample.Point(2, 2), sample.Point(3, 3))
        result = sample.convertValueTypeToCppAndThenToPython(pts[0], pts[1], pts[2])
        for orig, new in zip(pts, result):
            self.assertEqual(orig, new)
        self.assertFalse(pts[0] is result[0])
        self.assertTrue(pts[1] is result[1])
        self.assertTrue(pts[2] is result[2])

    def testObjectType(self):
        objs = (sample.ObjectType(), sample.ObjectType())
        objs[0].setObjectName('obj0')
        objs[1].setObjectName('obj1')
        result = sample.convertObjectTypeToCppAndThenToPython(objs[0], objs[1])
        for orig, new in zip(objs, result):
            self.assertEqual(orig, new)
            self.assertEqual(orig.objectName(), new.objectName())
            self.assertTrue(orig is new)

    def testContainerType(self):
        lst = range(4)
        result = sample.convertListOfIntegersToCppAndThenToPython(lst)
        self.assertTrue(len(result), 1)
        self.assertTrue(lst, result[0])


class PrimitiveConversionTest(unittest.TestCase):

    def testCppPrimitiveType(self):
        integers = (12, 34)
        result = sample.convertIntegersToCppAndThenToPython(integers[0], integers[1])
        for orig, new in zip(integers, result):
            self.assertEqual(orig, new)

    def testLargeIntAsFloat(self):
        """PYSIDE-2417: When passing an int to a function taking float,
           a 64bit conversion should be done."""
        point = sample.PointF(1, 2)
        large_int = 2**31 + 2
        point.setX(large_int)
        self.assertEqual(round(point.x()), large_int)

    def testUnsignedLongLongAsFloat(self):
        """PYSIDE-2652: When passing an unsigned long long to a function taking float,
           an unsigned 64bit conversion should be done."""
        point = sample.PointF(1, 2)
        large_int = 2**63
        point.setX(large_int)
        self.assertEqual(round(point.x()), large_int)


if __name__ == '__main__':
    unittest.main()
