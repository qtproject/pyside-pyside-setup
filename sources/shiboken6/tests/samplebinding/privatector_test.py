#!/usr/bin/env python
# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

'''Test cases for a class with only a private constructor.'''

import gc
import os
import sys
import unittest

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
from shiboken_paths import init_paths
init_paths()

from sample import PrivateCtor


class PrivateCtorTest(unittest.TestCase):
    '''Test case for PrivateCtor class'''

    def assertRaises(self, *args, **kwds):
        if not hasattr(sys, "pypy_version_info"):
            # PYSIDE-535: PyPy complains "Fatal RPython error: NotImplementedError"
            return super().assertRaises(*args, **kwds)

    def testPrivateCtorInstanciation(self):
        '''Test if instanciation of class with a private constructor raises an exception.'''
        self.assertRaises(TypeError, PrivateCtor)

    def testPrivateCtorInheritance(self):
        '''Test if inheriting from PrivateCtor raises an exception.'''
        def inherit():
            class Foo(PrivateCtor):
                pass
        self.assertRaises(TypeError, inherit)

    def testPrivateCtorInstanceMethod(self):
        '''Test if PrivateCtor.instance() method return the proper singleton.'''
        pd1 = PrivateCtor.instance()
        calls = pd1.instanceCalls()
        self.assertEqual(type(pd1), PrivateCtor)
        pd2 = PrivateCtor.instance()
        self.assertEqual(pd2, pd1)
        self.assertEqual(pd2.instanceCalls(), calls + 1)

    @unittest.skipUnless(hasattr(sys, "getrefcount"), f"{sys.implementation.name} has no refcount")
    def testPrivateCtorRefCounting(self):
        '''Test refcounting of the singleton returned by PrivateCtor.instance().'''
        pd1 = PrivateCtor.instance()
        calls = pd1.instanceCalls()
        refcnt = sys.getrefcount(pd1)
        pd2 = PrivateCtor.instance()
        self.assertEqual(pd2.instanceCalls(), calls + 1)
        self.assertEqual(sys.getrefcount(pd2), sys.getrefcount(pd1))
        self.assertEqual(sys.getrefcount(pd2), refcnt + 1)
        del pd1
        self.assertEqual(sys.getrefcount(pd2), refcnt)
        del pd2
        gc.collect()
        pd3 = PrivateCtor.instance()
        self.assertEqual(type(pd3), PrivateCtor)
        self.assertEqual(pd3.instanceCalls(), calls + 2)
        self.assertEqual(sys.getrefcount(pd3), refcnt)

if __name__ == '__main__':
    unittest.main()

