# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

import os
import sys
import unittest

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
from init_paths import init_test_paths
init_test_paths(False)

from PySide6.QtGui import QTextCursor
from PySide6.QtPrintSupport import QPrinter, QPrinterInfo
from PySide6.QtWidgets import QLayout, QWidget, QGraphicsLayout, QGraphicsLayoutItem

from helper.usesqapplication import UsesQApplication


class Layout(QLayout):
    def __init__(self):
        super().__init__()


class GraphicsLayout(QGraphicsLayout):
    def __init__(self):
        super().__init__()


class GraphicsLayoutItem(QGraphicsLayoutItem):
    def __init__(self):
        super().__init__()


class ReturnsQuadruplesOfNumbers(UsesQApplication):
    def compareTuples(self, ta, tb):
        for va, vb in zip(ta, tb):
            if round(va) != round(vb):
                return False
        return True

    def testQGraphicsLayoutGetContentsMargins(self):
        obj = GraphicsLayout()
        values = (10.0, 20.0, 30.0, 40.0)
        obj.setContentsMargins(*values)
        self.assertTrue(self.compareTuples(obj.getContentsMargins(), values))

    def testQGraphicsLayoutItemGetContentsMargins(self):
        obj = GraphicsLayoutItem()
        self.assertTrue(self.compareTuples(obj.getContentsMargins(), (0.0, 0.0, 0.0, 0.0)))

    def testQLayoutGetContentsMargins(self):
        obj = Layout()
        values = (10, 20, 30, 40)
        obj.setContentsMargins(*values)
        self.assertTrue(self.compareTuples(obj.getContentsMargins(), values))

    def testQTextCursorSelectedTableCells(self):
        obj = QTextCursor()
        self.assertEqual(obj.selectedTableCells(), (-1, -1, -1, -1))


if __name__ == "__main__":
    unittest.main()

