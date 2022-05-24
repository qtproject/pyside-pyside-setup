#!/usr/bin/env python
# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

'''Test cases for StrList class that inherits from std::list<Str>.'''

import os
import sys
import unittest

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
from shiboken_paths import init_paths
init_paths()

from sample import Str, StrList

class StrListTest(unittest.TestCase):
    '''Test cases for StrList class that inherits from std::list<Str>.'''

    def testStrListCtor_NoParams(self):
        '''StrList constructor receives no parameter.'''
        sl = StrList()
        self.assertEqual(len(sl), 0)
        self.assertEqual(sl.constructorUsed(), StrList.NoParamsCtor)

    def testStrListCtor_Str(self):
        '''StrList constructor receives a Str object.'''
        s = Str('Foo')
        sl = StrList(s)
        self.assertEqual(len(sl), 1)
        self.assertEqual(sl[0], s)
        self.assertEqual(sl.constructorUsed(), StrList.StrCtor)

    def testStrListCtor_PythonString(self):
        '''StrList constructor receives a Python string.'''
        s = 'Foo'
        sl = StrList(s)
        self.assertEqual(len(sl), 1)
        self.assertEqual(sl[0], s)
        self.assertEqual(sl.constructorUsed(), StrList.StrCtor)

    def testStrListCtor_StrList(self):
        '''StrList constructor receives a StrList object.'''
        sl1 = StrList(Str('Foo'))
        sl2 = StrList(sl1)
        #self.assertEqual(len(sl1), len(sl2))
        #self.assertEqual(sl1, sl2)
        self.assertEqual(sl2.constructorUsed(), StrList.CopyCtor)

    def testStrListCtor_ListOfStrs(self):
        '''StrList constructor receives a Python list of Str objects.'''
        strs = [Str('Foo'), Str('Bar')]
        sl = StrList(strs)
        self.assertEqual(len(sl), len(strs))
        self.assertEqual(sl, strs)
        self.assertEqual(sl.constructorUsed(), StrList.ListOfStrCtor)

    def testStrListCtor_MixedListOfStrsAndPythonStrings(self):
        '''StrList constructor receives a Python list of mixed Str objects and Python strings.'''
        strs = [Str('Foo'), 'Bar']
        sl = StrList(strs)
        self.assertEqual(len(sl), len(strs))
        self.assertEqual(sl, strs)
        self.assertEqual(sl.constructorUsed(), StrList.ListOfStrCtor)

    def testCompareStrListWithTupleOfStrs(self):
        '''Compares StrList with a Python tuple of Str objects.'''
        sl = StrList()
        sl.append(Str('Foo'))
        sl.append(Str('Bar'))
        self.assertEqual(len(sl), 2)
        self.assertEqual(sl, (Str('Foo'), Str('Bar')))

    def testCompareStrListWithTupleOfPythonStrings(self):
        '''Compares StrList with a Python tuple of Python strings.'''
        sl = StrList()
        sl.append(Str('Foo'))
        sl.append(Str('Bar'))
        self.assertEqual(len(sl), 2)
        self.assertEqual(sl, ('Foo', 'Bar'))

    def testCompareStrListWithTupleOfStrAndPythonString(self):
        '''Compares StrList with a Python tuple of mixed Str objects and Python strings.'''
        sl = StrList()
        sl.append(Str('Foo'))
        sl.append(Str('Bar'))
        self.assertEqual(len(sl), 2)
        self.assertEqual(sl, (Str('Foo'), 'Bar'))

if __name__ == '__main__':
    unittest.main()
