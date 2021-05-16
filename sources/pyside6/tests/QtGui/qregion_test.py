# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

import os
import sys
import unittest

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
from init_paths import init_test_paths
init_test_paths(False)

from PySide6.QtGui import QRegion
from PySide6.QtCore import QPoint, QRect, QSize
from helper.usesqapplication import UsesQApplication


class QRegionTest(UsesQApplication):

    def testFunctionUnit(self):
        r = QRegion(0, 0, 10, 10)
        r2 = QRegion(5, 5, 10, 10)

        ru = r.united(r2)
        self.assertTrue(ru.contains(QPoint(0, 0)))
        self.assertTrue(ru.contains(QPoint(5, 5)))
        self.assertTrue(ru.contains(QPoint(10, 10)))
        self.assertTrue(ru.contains(QPoint(14, 14)))

    def testSequence(self):
        region = QRegion()
        region += QRect(QPoint(0, 0), QSize(10, 10))
        region += QRect(QPoint(10, 0), QSize(20, 20))
        self.assertEqual(len(region), 2)
        for r in region:
            pass


if __name__ == '__main__':
    unittest.main()
