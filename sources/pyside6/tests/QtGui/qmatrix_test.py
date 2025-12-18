# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0
from __future__ import annotations

import os
import sys
import unittest

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
from init_paths import init_test_paths
init_test_paths(False)

from PySide6.QtGui import (
    QMatrix2x2,
    QMatrix2x3,
    QMatrix2x4,
    QMatrix3x2,
    QMatrix3x3,
    QMatrix3x4,
    QMatrix4x2,
    QMatrix4x3,
    QMatrix4x4,
)


# Helper function to create sequential data for a matrix
def sequential_values(rows: int, cols: int) -> list[float]:
    return [float(i + 1) for i in range(rows * cols)]


class TestQMatrixIndexing(unittest.TestCase):

    def setUp(self):
        # Matrix types
        self.matrices = [
            (QMatrix2x2(sequential_values(2, 2)), 2, 2),
            (QMatrix2x3(sequential_values(2, 3)), 3, 2),
            (QMatrix2x4(sequential_values(2, 4)), 4, 2),
            (QMatrix3x2(sequential_values(3, 2)), 2, 3),
            (QMatrix3x3(sequential_values(3, 3)), 3, 3),
            (QMatrix3x4(sequential_values(3, 4)), 4, 3),
            (QMatrix4x2(sequential_values(4, 2)), 2, 4),
            (QMatrix4x3(sequential_values(4, 3)), 3, 4),
            (QMatrix4x4(sequential_values(4, 4)), 4, 4),
        ]

    def test_getitem(self):
        """Test [row, col] indexing for all matrix types."""
        for m, rows, cols in self.matrices:
            v = 1.0
            for x in range(rows):
                for y in range(cols):
                    self.assertEqual(m[x, y], v)
                    v += 1.0

    def test_callable_operator(self):
        """Test operator()(row, col) for all QMatrix types."""
        for m, rows, cols in self.matrices:
            v = 1.0
            for x in range(rows):
                for y in range(cols):
                    self.assertEqual(m(x, y), v)
                    v += 1.0


if __name__ == "__main__":
    unittest.main()
