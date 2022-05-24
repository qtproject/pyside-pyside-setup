#!/usr/bin/env python
# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

import os
import sys
import unittest

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
from shiboken_paths import init_paths
init_paths()

from sample import IntList

class IntListTest(unittest.TestCase):

    def testAutoFunctionsToBaseList(self):
        lst = IntList()
        self.assertEqual(len(lst), 0)
        lst.append(10)
        self.assertEqual(lst[0], 10)
        lst.append(20)
        self.assertEqual(lst[1], 20)
        lst.append(30)
        self.assertEqual(lst[2], 30)
        lst[1] = 25
        self.assertEqual(lst[0], 10)
        self.assertEqual(lst[1], 25)
        self.assertEqual(lst[2], 30)
        self.assertEqual(len(lst), 3)

    def testIntListCtor_NoParams(self):
        '''IntList constructor receives no parameter.'''
        il = IntList()
        self.assertEqual(len(il), 0)
        self.assertEqual(il.constructorUsed(), IntList.NoParamsCtor)

    def testIntListCtor_int(self):
        '''IntList constructor receives an integer.'''
        value = 123
        il = IntList(value)
        self.assertEqual(len(il), 1)
        self.assertEqual(il[0], value)
        self.assertEqual(il.constructorUsed(), IntList.IntCtor)

    def testIntListCtor_IntList(self):
        '''IntList constructor receives an IntList object.'''
        il1 = IntList(123)
        il2 = IntList(il1)
        self.assertEqual(len(il1), len(il2))
        for i in range(len(il1)):
            self.assertEqual(il1[i], il2[i])
        self.assertEqual(il2.constructorUsed(), IntList.CopyCtor)

    def testIntListCtor_ListOfInts(self):
        '''IntList constructor receives an integer list.'''
        ints = [123, 456]
        il = IntList(ints)
        self.assertEqual(len(il), len(ints))
        for i in range(len(il)):
            self.assertEqual(il[i], ints[i])
        self.assertEqual(il.constructorUsed(), IntList.ListOfIntCtor)

    def testIntListAttributeTypeCheck(self):
        '''Attribute values to IntList.'''
        il = IntList([0, 1, 2])
        self.assertEqual(len(il), 3)
        il[0] = 123
        self.assertEqual(len(il), 3)
        self.assertEqual(il[0], 123)
        il[1] = 432.1
        self.assertEqual(len(il), 3)
        self.assertEqual(il[1], int(432.1))
        self.assertRaises(TypeError, il.__setitem__, 2, '78')

if __name__ == '__main__':
    unittest.main()
