# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

import os
import sys

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
sys.path.append(os.fspath(Path(__file__).resolve().parents[1] / "util"))
from init_paths import init_test_paths
init_test_paths()

from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QApplication, QGraphicsScene, QGraphicsView


class Test(QGraphicsView):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.s = QGraphicsScene()
        self.setScene(self.s)


a = QApplication(sys.argv)
t = Test()
t.show()
QTimer.singleShot(0, t.close)
sys.exit(a.exec_())
