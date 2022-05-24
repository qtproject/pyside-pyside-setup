#!/usr/bin/env python
# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

import os
import sys
import unittest

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
from shiboken_paths import init_paths
init_paths()
from sample import *

class ObjectTypeOperatorsTest(unittest.TestCase):

    def testIt(self):
        a = ObjectTypeOperators("a")
        b = ObjectTypeOperators("b")
        self.assertFalse(a == b)
        self.assertEqual(a, a < b)

        # this should change a.key() and return nothing.
        self.assertEqual(None, a > b)
        self.assertEqual(a.key(), "aoperator>")

    def testPointerOpeators(self):
        a = ObjectTypeOperators("a")
        b = ObjectTypeOperators("b")
        self.assertEqual(a + "bc", "abc")
        self.assertEqual("bc" + a, "bca")
        self.assertEqual("a", a)
        self.assertEqual(a, "a")

    def testOperatorInjection(self):
        a = ObjectTypeOperators("a")
        self.assertNotEqual(a, "b")

if __name__ == '__main__':
    unittest.main()
