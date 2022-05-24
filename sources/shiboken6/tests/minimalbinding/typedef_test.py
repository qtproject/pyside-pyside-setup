#!/usr/bin/env python
# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

from functools import reduce
import os
import sys
import unittest

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
from shiboken_paths import init_paths
init_paths()
from minimal import *

try:
    import numpy as np
except ImportError as e:
    print(e)
    np = None


class TypedefTest(unittest.TestCase):

    def setUp(self):
        self.the_size = 8

    def test_arrayFuncInt(self):
        none = ()
        full = range(self.the_size)
        self.assertTrue(arrayFuncInt(none), "None is empty, arrayFuncInt should return true")
        self.assertFalse(arrayFuncInt(full), "Full is NOT empty, arrayFuncInt should return false")

        self.assertTrue(arrayFuncInt(np.array(none)), "None is empty, arrayFuncInt should return true")
        self.assertFalse(arrayFuncInt(np.array(full)), "Full is NOT empty, arrayFuncInt should return false")

    def test_arrayFuncIntTypedef(self):
        none = ()
        full = (1, 2, 3)
        self.assertTrue(arrayFuncIntTypedef(none), "None is empty, arrayFuncIntTypedef should return true")
        self.assertFalse(arrayFuncIntTypedef(full), "Full is NOT empty, arrayFuncIntTypedef should return false")

        self.assertTrue(arrayFuncIntTypedef(np.array(none)), "None is empty, arrayFuncIntTypedef should return true")
        self.assertFalse(arrayFuncIntTypedef(np.array(full)), "Full is NOT empty, arrayFuncIntTypedef should return false")

    def test_arrayFuncIntReturn(self):
        none = arrayFuncIntReturn(0)
        full = arrayFuncIntReturn(self.the_size)
        self.assertTrue((len(none) == 0), "none should be empty")
        self.assertTrue((len(full) == self.the_size), "full should have " + str(self.the_size) + " elements")

    def test_arrayFuncIntReturnTypedef(self):
        none = arrayFuncIntReturnTypedef(0)
        full = arrayFuncIntReturnTypedef(self.the_size)
        self.assertTrue((len(none) == 0), "none should be empty")
        self.assertTrue((len(full) == self.the_size), "full should have " + str(self.the_size) + " elements")

    def test_arrayFunc(self):
        none = ()
        full = range(self.the_size)
        self.assertTrue(arrayFunc(none), "None is empty, arrayFunc should return true")
        self.assertFalse(arrayFunc(full), "Full is NOT empty, arrayFunc should return false")

        self.assertTrue(arrayFunc(np.array(none)), "None is empty, arrayFunc should return true")
        self.assertFalse(arrayFunc(np.array(full)), "Full is NOT empty, arrayFunc should return false")

    def test_arrayFuncTypedef(self):
        none = ()
        full = (1, 2, 3)
        self.assertTrue(arrayFuncTypedef(none), "None is empty, arrayFuncTypedef should return true")
        self.assertFalse(arrayFuncTypedef(full), "Full is NOT empty, arrayFuncTypedef should return false")

        self.assertTrue(arrayFuncTypedef(np.array(none)), "None is empty, arrayFuncTypedef should return true")
        self.assertFalse(arrayFuncTypedef(np.array(full)), "Full is NOT empty, arrayFuncTypedef should return false")

    def test_arrayFuncReturn(self):
        none = arrayFuncReturn(0)
        full = arrayFuncReturn(self.the_size)
        self.assertTrue((len(none) == 0), "none should be empty")
        self.assertTrue((len(full) == self.the_size), "full should have " + str(self.the_size) + " elements")

    def test_arrayFuncReturnTypedef(self):
        none = arrayFuncReturnTypedef(0)
        full = arrayFuncReturnTypedef(self.the_size)
        self.assertTrue((len(none) == 0), "none should be empty")
        self.assertTrue((len(full) == self.the_size), "full should have " + str(self.the_size) + " elements")


if __name__ == '__main__':
    if np != None:
        unittest.main()
