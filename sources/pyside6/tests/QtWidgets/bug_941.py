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

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication, QHeaderView

received_column = None
received_order = None


def foo(colum, order):
    global received_column, received_order
    received_column = colum
    received_order = order


class TestBug941 (unittest.TestCase):

    def testIt(self):
        app = QApplication([])  # noqa: F841
        view = QHeaderView(Qt.Orientation.Horizontal)
        self.assertTrue(view.sortIndicatorChanged.connect(foo))
        # this can't raise an exception!
        view.sortIndicatorChanged.emit(0, Qt.SortOrder.DescendingOrder)
        self.assertEqual(received_column, 0)
        self.assertEqual(received_order, Qt.SortOrder.DescendingOrder)


if __name__ == '__main__':
    unittest.main()
