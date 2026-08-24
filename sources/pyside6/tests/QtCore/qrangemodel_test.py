# Copyright (C) 2025 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0
from __future__ import annotations

import os
import sys
import unittest

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
from init_paths import init_test_paths
init_test_paths(False)

from PySide6.QtCore import QRangeModel


try:
    import numpy as np
    HAVE_NUMPY = True
except ModuleNotFoundError:
    HAVE_NUMPY = False


class QRangeModelTest(unittest.TestCase):

    def test_pylist(self):
        test_list = [1, 2, 3]
        model = QRangeModel(test_list)
        self.assertEqual(model.rowCount(), 3)
        self.assertEqual(model.data(model.createIndex(2, 0)), 3)

    def test_pytable(self):
        test_table = [[1, 2], [3, 4]]
        model = QRangeModel(test_table)
        self.assertEqual(model.rowCount(), 2)
        self.assertEqual(model.columnCount(), 2)
        self.assertEqual(model.data(model.createIndex(1, 1)), 4)

    def test_pystringtable(self):
        test_table = [["item11", "item12"], ["item21", "item22"]]
        model = QRangeModel(test_table)
        self.assertEqual(model.rowCount(), 2)
        self.assertEqual(model.columnCount(), 2)
        self.assertEqual(model.data(model.createIndex(1, 1)), "item22")

    @unittest.skipUnless(HAVE_NUMPY, "requires numpy")
    def test_numpy_list(self):
        test_array = np.array([1, 2, 3])
        model = QRangeModel(test_array)
        self.assertEqual(model.rowCount(), 3)
        self.assertEqual(model.data(model.createIndex(2, 0)), 3)

    @unittest.skipUnless(HAVE_NUMPY, "requires numpy")
    def test_numpy_table(self):
        test_table = np.array([[1, 2], [3, 4]])
        model = QRangeModel(test_table)
        self.assertEqual(model.rowCount(), 2)
        self.assertEqual(model.columnCount(), 2)
        self.assertEqual(model.data(model.createIndex(1, 1)), 4)


if __name__ == '__main__':
    unittest.main()
