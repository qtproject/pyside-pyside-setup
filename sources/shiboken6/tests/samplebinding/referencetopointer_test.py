#!/usr/bin/env python
# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

'''Test cases for a reference to pointer argument type.'''

import os
import sys
import unittest

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
from shiboken_paths import init_paths
init_paths()

from sample import VirtualMethods, Str

class ExtendedVirtualMethods(VirtualMethods):
    def __init__(self):
        VirtualMethods.__init__(self)
        self.prefix = 'Ext'

    def createStr(self, text):
        ext_text = text
        if text is not None:
            ext_text = self.prefix + text
        return VirtualMethods.createStr(self, ext_text)


class ReferenceToPointerTest(unittest.TestCase):
    '''Test cases for a reference to pointer argument type.'''

    def testSimpleCallWithNone(self):
        '''Simple call to createStr method with a None argument.'''
        obj = VirtualMethods()
        ok, string = obj.createStr(None)
        self.assertFalse(ok)
        self.assertEqual(string, None)

    def testSimpleCallWithString(self):
        '''Simple call to createStr method with a Python string argument.'''
        obj = VirtualMethods()
        ok, string = obj.createStr('foo')
        self.assertTrue(ok)
        self.assertEqual(string, Str('foo'))

    def testCallNonReimplementedMethodWithNone(self):
        '''Calls createStr method from C++ with a None argument.'''
        obj = VirtualMethods()
        ok, string = obj.callCreateStr(None)
        self.assertFalse(ok)
        self.assertEqual(string, None)

    def testCallNonReimplementedMethodWithString(self):
        '''Calls createStr method from C++ with a Python string argument.'''
        obj = VirtualMethods()
        ok, string = obj.callCreateStr('foo')
        self.assertTrue(ok)
        self.assertEqual(string, Str('foo'))

    def testCallReimplementedMethodWithNone(self):
        '''Calls reimplemented createStr method from C++ with a None argument.'''
        obj = ExtendedVirtualMethods()
        ok, string = obj.callCreateStr(None)
        self.assertFalse(ok)
        self.assertEqual(string, None)

    def testCallReimplementedMethodWithString(self):
        '''Calls reimplemented createStr method from C++ with a Python string argument.'''
        obj = ExtendedVirtualMethods()
        ok, string = obj.callCreateStr('foo')
        self.assertTrue(ok)
        self.assertEqual(string, Str(obj.prefix + 'foo'))

if __name__ == '__main__':
    unittest.main()

