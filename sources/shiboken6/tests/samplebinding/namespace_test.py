#!/usr/bin/env python
# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

'''Test cases for std::map container conversions'''

import os
import sys
import unittest

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
from shiboken_paths import init_paths
init_paths()

from sample import *
from shiboken_test_helper import objectFullname

from shiboken6 import Shiboken

from shibokensupport.signature import get_signature

# For tests of invisible namespaces, see
# enumfromremovednamespace_test.py / removednamespaces.h


class TestVariablesUnderNamespace(unittest.TestCase):
    def testIt(self):
         self.assertEqual(SampleNamespace.variableInNamespace, 42)


class TestClassesUnderNamespace(unittest.TestCase):
    def testIt(self):
        c1 = SampleNamespace.SomeClass()
        e1 = SampleNamespace.SomeClass.ProtectedEnum()
        c2 = SampleNamespace.SomeClass.SomeInnerClass()
        e2 = SampleNamespace.SomeClass.SomeInnerClass.ProtectedEnum()
        c3 = SampleNamespace.SomeClass.SomeInnerClass.OkThisIsRecursiveEnough()
        e3 = SampleNamespace.SomeClass.SomeInnerClass.OkThisIsRecursiveEnough.NiceEnum(0)

    def testFunctionAddedOnNamespace(self):
        res = SampleNamespace.ImInsideANamespace(2, 2)
        self.assertEqual(res, 4)

    def testTpNames(self):
        self.assertEqual(str(SampleNamespace.SomeClass),
            "<class 'sample.SampleNamespace.SomeClass'>")
        self.assertEqual(str(SampleNamespace.SomeClass.ProtectedEnum),
            "<enum 'ProtectedEnum'>" if sys.pyside63_option_python_enum else
            "<class 'sample.SampleNamespace.SomeClass.ProtectedEnum'>")
        self.assertEqual(str(SampleNamespace.SomeClass.SomeInnerClass.ProtectedEnum),
            "<enum 'ProtectedEnum'>" if sys.pyside63_option_python_enum else
            "<class 'sample.SampleNamespace.SomeClass.SomeInnerClass.ProtectedEnum'>")
        self.assertEqual(str(SampleNamespace.SomeClass.SomeInnerClass.OkThisIsRecursiveEnough),
            "<class 'sample.SampleNamespace.SomeClass.SomeInnerClass.OkThisIsRecursiveEnough'>")
        self.assertEqual(str(SampleNamespace.SomeClass.SomeInnerClass.OkThisIsRecursiveEnough.NiceEnum),
            "<enum 'NiceEnum'>" if sys.pyside63_option_python_enum else
            "<class 'sample.SampleNamespace.SomeClass.SomeInnerClass.OkThisIsRecursiveEnough.NiceEnum'>")

        # Test if enum inside of class is correct represented
        self.assertEqual(objectFullname(get_signature(SampleNamespace.enumInEnumOut).parameters['in_'].annotation),
            "sample.SampleNamespace.InValue")
        self.assertEqual(objectFullname(get_signature(SampleNamespace.enumAsInt).parameters['value'].annotation),
            "sample.SampleNamespace.SomeClass.PublicScopedEnum")


    def testInlineNamespaces(self):
        cls = SampleNamespace.ClassWithinInlineNamespace()
        cls.setValue(SampleNamespace.EWIN_Value1)
        self.assertEqual(cls.value(), SampleNamespace.EWIN_Value1)


if __name__ == '__main__':
    unittest.main()
