# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause
from __future__ import annotations

"""PySide6 Active Qt Viewer example"""

import sys
from PySide6.QtAxContainer import QAxSelect, QAxWidget
from PySide6.QtGui import QAction
from PySide6.QtWidgets import (QApplication, QDialog,
                               QMainWindow, QMessageBox, QToolBar)


class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()

        toolBar = QToolBar()
        self.addToolBar(toolBar)
        fileMenu = self.menuBar().addMenu("&File")
        loadAction = QAction("Load...", self, shortcut="Ctrl+L", triggered=self.load)
        fileMenu.addAction(loadAction)
        toolBar.addAction(loadAction)
        exitAction = QAction("E&xit", self, shortcut="Ctrl+Q", triggered=self.close)
        fileMenu.addAction(exitAction)

        aboutMenu = self.menuBar().addMenu("&About")
        aboutQtAct = QAction("About &Qt", self, triggered=qApp.aboutQt)  # noqa: F821
        aboutMenu.addAction(aboutQtAct)
        self.axWidget = QAxWidget()
        self.setCentralWidget(self.axWidget)

    def load(self):
        axSelect = QAxSelect(self)
        if axSelect.exec() == QDialog.Accepted:
            clsid = axSelect.clsid()
            if not self.axWidget.setControl(clsid):
                QMessageBox.warning(self, "AxViewer", f"Unable to load {clsid}.")


if __name__ == '__main__':
    app = QApplication(sys.argv)
    mainWin = MainWindow()
    availableGeometry = mainWin.screen().availableGeometry()
    mainWin.resize(availableGeometry.width() / 3, availableGeometry.height() / 2)
    mainWin.show()
    sys.exit(app.exec())
