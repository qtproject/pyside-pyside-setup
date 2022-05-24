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
from smart import Integer, StdSharedPtrTestBench, std


def call_func_on_ptr(ptr):
    ptr.printInteger()


class StdSharedPtrTests(unittest.TestCase):
    def testInteger(self):
        p = StdSharedPtrTestBench.createInteger()
        StdSharedPtrTestBench.printInteger(p)
        self.assertTrue(p)
        call_func_on_ptr(p)

        np = StdSharedPtrTestBench.createNullInteger()
        StdSharedPtrTestBench.printInteger(np)
        self.assertFalse(np)
        self.assertRaises(AttributeError, call_func_on_ptr, np)

        iv = Integer()
        iv.setValue(42)
        np = std.shared_ptr_Integer(iv)
        self.assertEqual(np.value(), 42)

    def testInt(self):
        np = StdSharedPtrTestBench.createNullInt()
        StdSharedPtrTestBench.printInt(np)
        self.assertFalse(np)
        p = StdSharedPtrTestBench.createInt()
        StdSharedPtrTestBench.printInt(p)


if __name__ == '__main__':
    unittest.main()
