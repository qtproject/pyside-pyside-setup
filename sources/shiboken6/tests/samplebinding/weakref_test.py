#!/usr/bin/env python
# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

'''Test weakref support'''

import gc
import os
import sys
import unittest
import weakref

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
from shiboken_paths import init_paths
init_paths()

from sample import ObjectType, PrivateDtor


class WeakrefBasicTest(unittest.TestCase):
    '''Simple test case of using a weakref'''

    def setUp(self):
        self.called = False

    def cb(self, *args):
        self.called = True

    def testBasic(self):
        '''ObjectType weakref'''
        obj = ObjectType()
        ref = weakref.ref(obj, self.cb)
        del obj
        # PYSIDE-535: Need to collect garbage in PyPy to trigger deletion
        gc.collect()
        self.assertTrue(self.called)

    def testPrivateDtor(self):
        '''PrivateDtor weakref'''
        obj = PrivateDtor.instance()
        ref = weakref.ref(obj, self.cb)
        del obj
        # PYSIDE-535: Need to collect garbage in PyPy to trigger deletion
        gc.collect()
        self.assertTrue(self.called)


if __name__ == '__main__':
    unittest.main()
