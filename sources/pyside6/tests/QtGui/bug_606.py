# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

import os
import sys
import unittest

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
from init_paths import init_test_paths
init_test_paths(False)

from PySide6.QtGui import QVector2D, QVector3D, QVector4D, qFuzzyCompare
from PySide6.QtGui import QColor


class testCases(unittest.TestCase):
    def testQVector2DToTuple(self):
        vec = QVector2D(1, 2)
        self.assertEqual((1, 2), vec.toTuple())
        self.assertTrue(qFuzzyCompare(vec, vec))
        vec2 = QVector2D(1, 3)
        self.assertFalse(qFuzzyCompare(vec, vec2))

    def testQVector3DToTuple(self):
        vec = QVector3D(1, 2, 3)
        self.assertEqual((1, 2, 3), vec.toTuple())
        vec2 = QVector3D(1, 3, 4)
        self.assertFalse(qFuzzyCompare(vec, vec2))

    def testQVector4DToTuple(self):
        vec = QVector4D(1, 2, 3, 4)
        self.assertEqual((1, 2, 3, 4), vec.toTuple())
        self.assertTrue(qFuzzyCompare(vec, vec))
        vec2 = QVector4D(1, 3, 4, 5)
        self.assertFalse(qFuzzyCompare(vec, vec2))

    def testQColorToTuple(self):
        c = QColor(0, 0, 255)
        c.setRgb(1, 2, 3)
        self.assertEqual((1, 2, 3, 255), c.toTuple())


if __name__ == '__main__':
    unittest.main()
