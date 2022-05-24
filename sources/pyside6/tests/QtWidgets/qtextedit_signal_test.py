# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

import os
import sys
import unittest

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
from init_paths import init_test_paths
init_test_paths(False)

from PySide6.QtCore import Signal, Slot
from PySide6.QtWidgets import QMainWindow, QPushButton, QTextEdit
from helper.usesqapplication import UsesQApplication


class MyWindow(QMainWindow):
    appendText = Signal(str)

    @Slot()
    def onButtonPressed(self):
        self.appendText.emit("PySide")

    def __init__(self, parent=None):
        super().__init__(parent)

        self.textEdit = QTextEdit()
        self.btn = QPushButton("ClickMe")
        self.btn.clicked.connect(self.onButtonPressed)
        self.appendText.connect(self.textEdit.append)

    def start(self):
        self.btn.click()

    def text(self):
        return self.textEdit.toPlainText()


class testSignalWithCPPSlot(UsesQApplication):

    def testEmission(self):
        w = MyWindow()
        w.start()
        self.assertEqual(w.text(), "PySide")


if __name__ == '__main__':
    unittest.main()

