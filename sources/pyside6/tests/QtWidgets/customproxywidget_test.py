# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

import os
import sys
import unittest

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
from init_paths import init_test_paths
init_test_paths(False)

from helper.usesqapplication import UsesQApplication
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QPainter
from PySide6.QtWidgets import QLabel
from PySide6.QtWidgets import QGraphicsScene, QGraphicsView, QGraphicsItem, QGraphicsProxyWidget


class CustomProxy(QGraphicsProxyWidget):
    def __init__(self, parent=None, wFlags=0):
        QGraphicsProxyWidget.__init__(self, parent, wFlags)


class CustomProxyWidgetTest(UsesQApplication):
    def testCustomProxyWidget(self):
        scene = QGraphicsScene()

        proxy = CustomProxy(None, Qt.Window)
        widget = QLabel('Widget')
        proxy.setWidget(widget)
        proxy.setCacheMode(QGraphicsItem.DeviceCoordinateCache)
        scene.addItem(proxy)
        scene.setSceneRect(scene.itemsBoundingRect())

        view = QGraphicsView(scene)
        view.setRenderHints(QPainter.Antialiasing | QPainter.SmoothPixmapTransform)
        view.setViewportUpdateMode(QGraphicsView.BoundingRectViewportUpdate)
        view.show()

        timer = QTimer.singleShot(100, self.app.quit)
        self.app.exec()


if __name__ == '__main__':
    unittest.main()

