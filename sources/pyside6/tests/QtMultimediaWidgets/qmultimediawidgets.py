# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

'''Test cases for QtMultimediaWidgets'''

import os
import sys
import unittest

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
from init_paths import init_test_paths
init_test_paths(False)

from helper.usesqapplication import UsesQApplication
from PySide6.QtMultimediaWidgets import QGraphicsVideoItem, QVideoWidget
from PySide6.QtWidgets import QGraphicsScene, QGraphicsView, QVBoxLayout, QWidget
from PySide6.QtCore import QTimer


class MyWidget(QWidget):
    def __init__(self):
        super().__init__()

        layout = QVBoxLayout(self)
        layout.addWidget(QVideoWidget())

        graphicsScene = QGraphicsScene()
        graphicsView = QGraphicsView(graphicsScene)
        graphicsScene.addItem(QGraphicsVideoItem())
        layout.addWidget(graphicsView)


class QMultimediaWidgetsTest(UsesQApplication):
    def testMultimediaWidgets(self):
        w = MyWidget()
        w.show()

        timer = QTimer.singleShot(100, self.app.quit)
        self.app.exec()


if __name__ == '__main__':
    unittest.main()
