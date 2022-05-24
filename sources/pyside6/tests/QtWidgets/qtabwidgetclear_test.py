# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

import os
import sys
import unittest

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
from init_paths import init_test_paths
init_test_paths(False)

from PySide6.QtWidgets import QMainWindow, QTabWidget, QTextEdit, QSplitter
from helper.usesqapplication import UsesQApplication


class TabWidgetClear(QMainWindow):
    def __init__(self):
        super().__init__()
        self.tabWidget = QTabWidget(self)
        self.setCentralWidget(self.tabWidget)
        self.editBox = QTextEdit(self)
        self.tabWidget.addTab(self.getSplitter(), 'Test')

    def getSplitter(self):
        splitter = QSplitter()
        splitter.addWidget(self.editBox)
        return splitter

    def toggle(self):
        self.tabWidget.clear()
        self.getSplitter()


class TestTabWidgetClear(UsesQApplication):

    def testClear(self):
        self.window = TabWidgetClear()
        self.window.show()
        try:
            self.window.toggle()
        except RuntimeError as e:
            # This should never happened, PYSIDE-213
            raise e


if __name__ == '__main__':
    unittest.main()
