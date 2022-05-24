#!/usr/bin/python
# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

import os
import sys
import unittest

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
from init_paths import init_test_paths
init_test_paths(False)

from PySide6.QtWidgets import QGraphicsScene, QGraphicsRectItem, QGraphicsView, QApplication
from PySide6.QtGui import QBrush, QColor
from PySide6.QtCore import QTimer
from helper.usesqapplication import UsesQApplication

qgraphics_item_painted = False


class RoundRectItem(QGraphicsRectItem):

    def __init__(self, x, y, w, h):
        QGraphicsRectItem.__init__(self, x, y, w, h)

    def paint(self, painter, qstyleoptiongraphicsitem, qwidget):
        global qgraphics_item_painted
        qgraphics_item_painted = True
        view = self.scene().views()[0]
        QTimer.singleShot(20, view.close)


class QGraphicsItemTest(UsesQApplication):

    def createRoundRect(self, scene):
        item = RoundRectItem(10, 10, 100, 100)
        item.setBrush(QBrush(QColor(255, 0, 0)))
        scene.addItem(item)
        return item

    def quit_app(self):
        self.app.quit()

    def test_setParentItem(self):
        global qgraphics_item_painted

        scene = QGraphicsScene()
        scene.addText("test")
        view = QGraphicsView(scene)
        view.setWindowTitle("virtual_pure_override_test")

        rect = self.createRoundRect(scene)
        view.show()
        self.app.exec()
        self.assertTrue(qgraphics_item_painted)


if __name__ == '__main__':
    unittest.main()

