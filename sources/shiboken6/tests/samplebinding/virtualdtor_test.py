#!/usr/bin/env python
# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

'''Test cases for virtual destructor.'''

import gc
import os
import sys
import unittest

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
from shiboken_paths import init_paths
init_paths()

from sample import VirtualDtor

class ExtendedVirtualDtor(VirtualDtor):
    def __init__(self):
        VirtualDtor.__init__(self)

class VirtualDtorTest(unittest.TestCase):
    '''Test case for virtual destructor.'''

    def setUp(self):
        VirtualDtor.resetDtorCounter()

    def testVirtualDtor(self):
        '''Original virtual destructor is being called.'''
        dtor_called = VirtualDtor.dtorCalled()
        for i in range(1, 10):
            vd = VirtualDtor()
            del vd
            # PYSIDE-535: Need to collect garbage in PyPy to trigger deletion
            gc.collect()
            self.assertEqual(VirtualDtor.dtorCalled(), dtor_called + i)

    def testVirtualDtorOnCppCreatedObject(self):
        '''Original virtual destructor is being called for a C++ created object.'''
        dtor_called = VirtualDtor.dtorCalled()
        for i in range(1, 10):
            vd = VirtualDtor.create()
            del vd
            # PYSIDE-535: Need to collect garbage in PyPy to trigger deletion
            gc.collect()
            self.assertEqual(VirtualDtor.dtorCalled(), dtor_called + i)

    def testDtorOnDerivedClass(self):
        '''Original virtual destructor is being called for a derived class.'''
        dtor_called = ExtendedVirtualDtor.dtorCalled()
        for i in range(1, 10):
            evd = ExtendedVirtualDtor()
            del evd
            # PYSIDE-535: Need to collect garbage in PyPy to trigger deletion
            gc.collect()
            self.assertEqual(ExtendedVirtualDtor.dtorCalled(), dtor_called + i)


if __name__ == '__main__':
    unittest.main()

