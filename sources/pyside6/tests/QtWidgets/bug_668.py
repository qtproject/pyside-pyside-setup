# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

import os
import sys

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
sys.path.append(os.fspath(Path(__file__).resolve().parents[1] / "util"))
from init_paths import init_test_paths
init_test_paths()

from PySide6.QtCore import QDir, QModelIndex, QTimer
from PySide6.QtWidgets import QApplication, QFileSystemModel, QMainWindow, QTreeView


class A(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        a = QFileSystemModel(self)
        a.setRootPath(QDir.homePath())

        v = QTreeView(self)
        v.setModel(a)
        self.setCentralWidget(v)
        # Test index() method (see PYSIDE-570, PYSIDE-331)
        index = a.index(0, 0, QModelIndex())


app = QApplication([])
m = A()
m.show()
QTimer.singleShot(0, m.close)
app.exec()
