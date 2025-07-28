# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0
from __future__ import annotations

'''Test cases for QtMultimediaWidgets'''

import os
import sys
import unittest

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
from init_paths import init_test_paths  # noqa: E402
init_test_paths(False)

from helper.usesqapplication import UsesQApplication  # noqa: E402
from PySide6.QtMultimediaWidgets import QGraphicsVideoItem, QVideoWidget  # noqa: E402
from PySide6.QtWidgets import QGraphicsScene, QGraphicsView, QVBoxLayout, QWidget  # noqa: E402
from PySide6.QtCore import QTimer  # noqa: E402


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

        timer = QTimer.singleShot(100, self.app.quit)  # noqa: F841
        self.app.exec()


if __name__ == '__main__':
    unittest.main()
