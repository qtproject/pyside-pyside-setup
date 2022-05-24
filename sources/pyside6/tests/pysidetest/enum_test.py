# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

import os
import sys
import unittest

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
from init_paths import init_test_paths
init_test_paths(True)

from PySide6.QtCore import Qt
from testbinding import Enum1, TestObjectWithoutNamespace


class ListConnectionTest(unittest.TestCase):

    def testEnumVisibility(self):
        self.assertEqual(Enum1.Option1, 1)
        self.assertEqual(Enum1.Option2, 2)
        self.assertEqual(TestObjectWithoutNamespace.Enum2.Option3, 3)
        self.assertEqual(TestObjectWithoutNamespace.Enum2.Option4, 4)

    def testFlagComparisonOperators(self):  # PYSIDE-1696, compare to self
        f1 = Qt.AlignHCenter | Qt.AlignBottom
        f2 = Qt.AlignHCenter | Qt.AlignBottom
        self.assertTrue(f1 == f1)
        self.assertTrue(f1 <= f1)
        self.assertTrue(f1 >= f1)
        self.assertFalse(f1 != f1)
        self.assertFalse(f1 < f1)
        self.assertFalse(f1 > f1)

        self.assertTrue(f1 == f2)
        self.assertTrue(f1 <= f2)
        self.assertTrue(f1 >= f2)
        self.assertFalse(f1 != f2)
        self.assertFalse(f1 < f2)
        self.assertFalse(f1 > f2)

        self.assertTrue(Qt.AlignHCenter < Qt.AlignBottom)
        self.assertFalse(Qt.AlignHCenter > Qt.AlignBottom)
        self.assertFalse(Qt.AlignBottom < Qt.AlignHCenter)
        self.assertTrue(Qt.AlignBottom > Qt.AlignHCenter)


if __name__ == '__main__':
    unittest.main()

