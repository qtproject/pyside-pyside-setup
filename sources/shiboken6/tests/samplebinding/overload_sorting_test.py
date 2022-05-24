#!/usr/bin/env python
# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

'''Test cases for overload sorting'''

import os
import sys
import unittest

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
from shiboken_paths import init_paths
init_paths()

from sample import *

class Dummy(object):
    pass

class SimpleOverloadSorting(unittest.TestCase):

    def setUp(self):
        self.obj = SortedOverload()

    def testIntDouble(self):
        '''Overloads with int and double'''
        self.assertEqual(self.obj.overload(3), "int")
        self.assertEqual(self.obj.overload(3.14), "double")

    def testImplicitConvert(self):
        '''Overloads with implicit convertible types'''
        self.assertEqual(self.obj.overload(ImplicitTarget()), "ImplicitTarget")
        self.assertEqual(self.obj.overload(ImplicitBase()), "ImplicitBase")

    def testContainer(self):
        '''Overloads with containers arguments'''
        self.assertEqual(self.obj.overload([ImplicitBase()]), "list(ImplicitBase)")

    def testPyObject(self):
        '''Overloads with PyObject args'''
        self.assertEqual(self.obj.overload(Dummy()), "PyObject")

    def testImplicitOnly(self):
        '''Passing an implicit convertible object to an overload'''
        self.assertTrue(self.obj.implicit_overload(ImplicitTarget()))

    def testPyObjectSort(self):
        self.assertEqual(self.obj.pyObjOverload(1, 2), "int,int")
        self.assertEqual(self.obj.pyObjOverload(object(), 2), "PyObject,int")


class DeepOverloadSorting(unittest.TestCase):

    def setUp(self):
        self.obj = SortedOverload()

    def testPyObject(self):
        '''Deep Overload - (int, PyObject *)'''
        self.assertEqual(self.obj.overloadDeep(1, Dummy()), "PyObject")

    def testImplicit(self):
        '''Deep Overload - (int, ImplicitBase *)'''
        self.assertEqual(self.obj.overloadDeep(1, ImplicitBase()), "ImplicitBase")

class EnumOverIntSorting(unittest.TestCase):
    def testEnumOverInt(self):
        ic = ImplicitConv(ImplicitConv.CtorTwo)
        self.assertEqual(ic.ctorEnum(), ImplicitConv.CtorTwo)


class TestCustomOverloadSequence(unittest.TestCase):
    '''Ensure the int-overload (returning v + sizeof(v)) is first as specified via
       overload-number in XML.'''
    def testCustomOverloadSequence(self):
        s = CustomOverloadSequence()
        self.assertEqual(s.overload(42), 46)


if __name__ == '__main__':
    unittest.main()
