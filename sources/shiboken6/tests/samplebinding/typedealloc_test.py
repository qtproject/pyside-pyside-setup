#!/usr/bin/env python
# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

'''Test deallocation of type extended in Python.'''

import gc
import os
import sys
import unittest
import weakref

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
from shiboken_paths import init_paths
init_paths()

from sample import Point


class TypeDeallocTest(unittest.TestCase):

    def setUp(self):
        self.called = False

    def tearDown(self):
        del self.called
        # PYSIDE-535: Need to collect garbage in PyPy to trigger deletion
        gc.collect()

    def callback(self, *args):
        self.called = True

    def testScopeEnd(self):
        ref = None
        def scope():
            class Ext(Point):
                pass
            o = Ext()
            global ref
            ref = weakref.ref(Ext, self.callback)
        scope()
        gc.collect()
        self.assertTrue(self.called)

    def testDeleteType(self):
        class Ext(Point):
            pass
        ref = weakref.ref(Ext, self.callback)
        del Ext
        gc.collect()
        self.assertTrue(self.called)


if __name__ == '__main__':
    unittest.main()

