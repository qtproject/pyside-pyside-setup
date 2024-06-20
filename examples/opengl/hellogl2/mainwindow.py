# Copyright (C) 2023 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause
from __future__ import annotations

from PySide6.QtCore import Slot, Qt
from PySide6.QtGui import QKeySequence
from PySide6.QtWidgets import QMainWindow, QMessageBox

from window import Window


class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()
        menuWindow = self.menuBar().addMenu("Window")
        menuWindow.addAction("Add new", QKeySequence(Qt.CTRL | Qt.Key_N),
                             self.onAddNew)
        menuWindow.addAction("Quit", QKeySequence(Qt.CTRL | Qt.Key_Q),
                             qApp.closeAllWindows)  # noqa: F821

        self.onAddNew()

    @Slot()
    def onAddNew(self):
        if not self.centralWidget():
            self.setCentralWidget(Window(self))
        else:
            QMessageBox.information(self, "Cannot Add Window()",
                                    "Already occupied. Undock first.")
