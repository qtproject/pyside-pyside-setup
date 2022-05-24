# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

''' Test cases related to QGraphicsItem and subclasses'''

import gc
import os
import sys
import unittest

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
from init_paths import init_test_paths
init_test_paths(False)

from PySide6.QtGui import QPolygonF, QColor, QBrush
from PySide6.QtWidgets import QGraphicsScene

from helper.usesqapplication import UsesQApplication


class QColorOnSetBrush(UsesQApplication):
    '''Test case for passing a QColor directly to setBrush'''

    def setUp(self):
        # Acquire resources
        super(QColorOnSetBrush, self).setUp()

        self.scene = QGraphicsScene()
        poly = QPolygonF()
        self.item = self.scene.addPolygon(poly)
        self.color = QColor('black')

    def tearDown(self):
        # Release resources
        del self.color
        del self.item
        del self.scene
        # PYSIDE-535: Need to collect garbage in PyPy to trigger deletion
        gc.collect()
        super(QColorOnSetBrush, self).tearDown()

    def testQColor(self):
        # QGraphicsAbstractShapeItem.setBrush(QColor)
        self.item.setBrush(self.color)
        self.assertEqual(QBrush(self.color), self.item.brush())


if __name__ == '__main__':
    unittest.main()
