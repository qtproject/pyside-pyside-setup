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

from helper.usesqapplication import UsesQApplication
from PySide6.QtGui import QPaintEngine, QPainter, QPaintDevice
from PySide6.QtCore import QPoint, QRect, QLine


class PaintEngine(QPaintEngine):
    def __init__(self):
        super().__init__()
        self.line_count = 0
        self.point_count = 0
        self.rect_count = 0

    def drawPoints(self, points):
        self.point_count = len(points)

    def drawRects(self, rects):
        self.rect_count = len(rects)

    def drawLines(self, lines):
        self.line_count = len(lines)

    def updateState(self, s):
        pass

    def begin(self, _dev):
        return True

    def end(self):
        return True


class PaintDevice(QPaintDevice):
    def __init__(self):
        super().__init__()
        self._engine = PaintEngine()

    def paintEngine(self):
        return self._engine

    def metric(self, metric):
        if metric == QPaintDevice.PaintDeviceMetric.PdmDevicePixelRatioScaled:
            return super().metric(metric)
        return 1


class QPaintEngineTest(UsesQApplication):
    """PYSIDE-3002: test whether virtual functions of QPaintEngine taking
       a C-style array of geometry primitives can be overridden."""
    def setUp(self):
        super().setUp()
        self._paint_device = PaintDevice()

    def tearDown(self):
        self._paint_device = None

    def test(self):
        points = [QPoint(1, 2), QPoint(3, 4)]
        rectangles = [QRect(1, 1, 1, 1), QRect(2, 2, 2, 2)]
        lines = [QLine(1, 2, 3, 4), QLine(3, 4, 5, 6)]

        with QPainter(self._paint_device) as painter:
            painter.drawPoints(points)
            painter.drawRects(rectangles)
            painter.drawLines(lines)

        engine = self._paint_device.paintEngine()
        self.assertTrue(engine.line_count, 2)
        self.assertTrue(engine.point_count, 2)
        self.assertTrue(engine.rect_count, 2)


if __name__ == '__main__':
    unittest.main()
