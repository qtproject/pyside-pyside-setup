# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

import os
import sys

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
sys.path.append(os.fspath(Path(__file__).resolve().parents[1] / "util"))
from init_paths import init_test_paths
init_test_paths()

from PySide6.QtCore import QTimer, Qt
from PySide6.QtWidgets import QApplication, QDockWidget, QMainWindow


class Window(QMainWindow):
    def childEvent(self, event):
        super(Window, self).childEvent(event)


app = QApplication([])
window = Window()

dock1 = QDockWidget()
dock2 = QDockWidget()
window.addDockWidget(Qt.LeftDockWidgetArea, dock1)
window.addDockWidget(Qt.LeftDockWidgetArea, dock2)
window.tabifyDockWidget(dock1, dock2)

window.show()
QTimer.singleShot(0, window.close)
app.exec()
