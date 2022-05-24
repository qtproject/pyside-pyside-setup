#!/usr/bin/env python
# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

import gc
import os
import sys
import unittest

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
from shiboken_paths import init_paths
init_paths()

import sample

delCalled = False

class MyObject(sample.ObjectType):
    def __del__(self):
        global delCalled
        delCalled = True

class TestDel(unittest.TestCase):
    def testIt(self):
        a = MyObject()
        del a
        # PYSIDE-535: Need to collect garbage in PyPy to trigger deletion
        gc.collect()
        self.assertTrue(delCalled)

if __name__ == '__main__':
    unittest.main()

