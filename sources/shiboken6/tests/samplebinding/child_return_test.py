#!/usr/bin/env python
# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

'''The BlackBox class has cases of ownership transference between C++ and Python.'''

import gc
import os
import sys
import unittest

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
from shiboken_paths import init_paths
init_paths()

from sample import *

class ReturnOfChildTest(unittest.TestCase):
    '''The BlackBox class has cases of ownership transference between C++ and Python.'''

    def testKillParentKeepingChild(self):
        '''Ownership transference from Python to C++ and back again.'''
        o1 = ObjectType.createWithChild()
        child = o1.children()[0]
        del o1
        # PYSIDE-535: Need to collect garbage in PyPy to trigger deletion
        gc.collect()
        self.assertRaises(RuntimeError, child.objectName)

    def testKillParentKeepingChild2(self):
        '''Ownership transference from Python to C++ and back again.'''
        o1 = ObjectType.createWithChild()
        child = o1.findChild("child")
        del o1
        # PYSIDE-535: Need to collect garbage in PyPy to trigger deletion
        gc.collect()
        self.assertRaises(RuntimeError, child.objectName)

if __name__ == '__main__':
    unittest.main()

