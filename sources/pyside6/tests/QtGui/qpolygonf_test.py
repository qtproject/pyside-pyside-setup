# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

import os
import sys
import unittest

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
from init_paths import init_test_paths
init_test_paths(False)

from PySide6.QtCore import QPoint, QPointF
from PySide6.QtGui import QPolygon, QPolygonF


class QPolygonFNotIterableTest(unittest.TestCase):
    """Test if a QPolygonF is iterable"""

    def testIt(self):
        points = []
        for i in range(0, 4):
            points.append(QPointF(float(i), float(i)))

        p = QPolygonF(points)
        self.assertEqual(len(p), 4)

        i = 0
        for point in p:
            self.assertEqual(int(point.x()), i)
            self.assertEqual(int(point.y()), i)
            i += 1

    def testPolygonShiftOperators(self):
        p = QPolygon()
        self.assertEqual(len(p), 0)
        p << QPoint(10, 20) << QPoint(20, 30) << [QPoint(20, 30), QPoint(40, 50)]
        self.assertEqual(len(p), 4)


if __name__ == '__main__':
    unittest.main()
