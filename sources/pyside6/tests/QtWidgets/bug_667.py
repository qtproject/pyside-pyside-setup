# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

import os
import sys

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
sys.path.append(os.fspath(Path(__file__).resolve().parents[1] / "util"))
from init_paths import init_test_paths
init_test_paths()

from PySide6.QtCore import QTimer, QPointF
from PySide6.QtWidgets import QApplication, QGraphicsView, QGraphicsScene, QGraphicsEllipseItem


class Ball(QGraphicsEllipseItem):
    def __init__(self, d, parent=None):
        super().__init__(0, 0, d, d, parent)
        self.vel = QPointF(0, 0)   #commenting this out prevents the crash


class Foo(QGraphicsView):
    def __init__(self):
        super().__init__(None)
        self.scene = QGraphicsScene(self.rect())
        self.setScene(self.scene)
        self.scene.addItem(Ball(10))


if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = Foo()
    w.show()
    w.raise_()
    QTimer.singleShot(0, w.close)
    sys.exit(app.exec())
