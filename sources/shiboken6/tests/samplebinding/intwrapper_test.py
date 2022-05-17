# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

import os
import sys
import unittest

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
from shiboken_paths import init_paths
init_paths()

from sample import IntWrapper


class IntWrapperTest(unittest.TestCase):

    def testOperators(self):
        ten1  = IntWrapper(10)
        ten2  = IntWrapper(10)
        twenty = IntWrapper(20)
        self.assertTrue(ten1 == ten2)
        self.assertTrue(ten1 != twenty)
        self.assertTrue(ten1 + ten2 == twenty)
        self.assertTrue(ten1 - ten2 == IntWrapper(0))
        i = IntWrapper(ten1.toInt())
        i += ten2
        self.assertTrue(i == twenty)
        i -= ten2
        self.assertTrue(i == ten1)

    def testAddPyMethodDef(self):
        """Test of added free function (PYSIDE-1905)."""
        i = IntWrapper(10)
        self.assertEqual(i.add_ints(10, 20), 30)


if __name__ == '__main__':
    unittest.main()
