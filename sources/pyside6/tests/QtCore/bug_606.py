# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

import os
import sys
import unittest

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
from init_paths import init_test_paths
init_test_paths(False)

import PySide6
from PySide6.QtCore import QPoint, QPointF
from PySide6.QtCore import QLine, QLineF
from PySide6.QtCore import QSize, QSizeF


class testCases(unittest.TestCase):
    def testQPointToTuple(self):
        p = QPoint(1, 2)
        self.assertEqual((1, 2), p.toTuple())

    def testQPointFToTuple(self):
        p = QPointF(1, 2)
        self.assertEqual((1, 2), p.toTuple())

    def testQLineToTuple(self):
        l = QLine(1, 2, 3, 4)
        self.assertEqual((1, 2, 3, 4), l.toTuple())

    def testQLineFToTuple(self):
        l = QLineF(1, 2, 3, 4)
        self.assertEqual((1, 2, 3, 4), l.toTuple())

    def testQSizeToTuple(self):
        s = QSize(1, 2)
        self.assertEqual((1, 2), s.toTuple())

    def testQSizeFToTuple(self):
        s = QSizeF(1, 2)
        self.assertEqual((1, 2), s.toTuple())


if __name__ == '__main__':
    unittest.main()
