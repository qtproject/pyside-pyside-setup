#!/usr/bin/env python
# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

'''Test cases for libsample bindings module'''

import os
import sys
import unittest

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
from shiboken_paths import init_paths
init_paths()

import sample

class ModuleTest(unittest.TestCase):
    '''Test case for module and global functions'''

    @unittest.skipIf(sys.pyside63_option_python_enum, "Makes no sense with strict Enums")
    def testModuleMembers(self):
        '''Test availability of classes, global functions and other members on binding'''
        expected_members = set(['Abstract', 'Derived', 'Point',
                                'ListUser', 'PairUser', 'MapUser',
                                'gimmeComplexList', 'gimmeDouble', 'gimmeInt',
                                'makeCString', 'multiplyPair', 'returnCString',
                                'SampleNamespace', 'transmuteComplexIntoPoint',
                                'transmutePointIntoComplex', 'sumComplexPair',
                                'FirstThing', 'SecondThing', 'ThirdThing',
                                'GlobalEnum', 'NoThing'])
        self.assertTrue(expected_members.issubset(dir(sample)))

    @unittest.skipIf(sys.pyside63_option_python_enum, "Makes no sense with strict Enums")
    def testAbstractPrintFormatEnum(self):
        '''Test availability of PrintFormat enum from Abstract class'''
        enum_members = set(['PrintFormat', 'Short', 'Verbose',
                            'OnlyId', 'ClassNameAndId'])
        self.assertTrue(enum_members.issubset(dir(sample.Abstract)))

    @unittest.skipIf(sys.pyside63_option_python_enum, "Makes no sense with strict Enums")
    def testSampleNamespaceOptionEnum(self):
        '''Test availability of Option enum from SampleNamespace namespace'''
        enum_members = set(['Option', 'None_', 'RandomNumber', 'UnixTime'])
        self.assertTrue(enum_members.issubset(dir(sample.SampleNamespace)))

    def testAddedFunctionAtModuleLevel(self):
        '''Calls function added to module from type system description.'''
        str1 = 'Foo'
        self.assertEqual(sample.multiplyString(str1, 3), str1 * 3)
        self.assertEqual(sample.multiplyString(str1, 0), str1 * 0)

    def testAddedFunctionWithVarargs(self):
        '''Calls function that receives varargs added to module from type system description.'''
        self.assertEqual(sample.countVarargs(1), 0)
        self.assertEqual(sample.countVarargs(1, 2), 1)
        self.assertEqual(sample.countVarargs(1, 2, 3, 'a', 'b', 4, (5, 6)), 6)

    def testSampleComparisonOpInNamespace(self):
        s1 = sample.sample.sample(10)
        s2 = sample.sample.sample(10)
        self.assertEqual(s1, s2)

    def testConstant(self):
        self.assertEqual(sample.sample.INT_CONSTANT, 42)

    def testStringFunctions(self):
        # Test plain ASCII, UCS1 and UCS4 encoding which have different
        # representations in the PyUnicode objects.
        for t1 in ["ascii", "Ümläut", "😀"]:
            expected = t1 + t1
            self.assertEqual(sample.addStdStrings(t1, t1), expected)
            self.assertEqual(sample.addStdWStrings(t1, t1), expected)

    def testNullPtrT(self):
        sample.testNullPtrT(None)
        self.assertRaises(TypeError, sample.testNullPtrT, 42)


if __name__ == '__main__':
    unittest.main()

