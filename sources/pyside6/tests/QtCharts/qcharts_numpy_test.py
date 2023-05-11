#!/usr/bin/python
# Copyright (C) 2023 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

'''Test cases for QCharts/numpy'''

import os
import sys
import unittest
try:
    import numpy as np
    HAVE_NUMPY = True
except ModuleNotFoundError:
    HAVE_NUMPY = False

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
from init_paths import init_test_paths
init_test_paths(False)

from helper.usesqapplication import UsesQApplication
from PySide6.QtCore import QCoreApplication
from PySide6.QtCharts import QLineSeries


class QChartsNumpyTestCase(UsesQApplication):
    '''Tests related to QCharts/numpy'''

    @unittest.skipUnless(HAVE_NUMPY, "requires numpy")
    def test(self):
        """PYSIDE-2313: Verify various types."""
        line_series = QLineSeries()
        data_types = [np.short, np.ushort, np.int32, np.uint32,
                      np.int64, np.uint64, np.float32, np.float64]
        for dt in data_types:
            print("Testing ", dt)
            old_size = line_series.count()
            x_arr = np.array([2], dtype=dt)
            y_arr = np.array([3], dtype=dt)
            line_series.appendNp(x_arr, y_arr)
            size = line_series.count()
            self.assertEqual(size, old_size + 1)
            point = line_series.points()[size - 1]
            self.assertEqual(point.x(), 2)
            self.assertEqual(point.y(), 3)


if __name__ == '__main__':
    unittest.main()
