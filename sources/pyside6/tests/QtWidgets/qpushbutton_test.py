# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

import os
import sys
import unittest

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
from init_paths import init_test_paths
init_test_paths(False)

from helper.usesqapplication import UsesQApplication
from PySide6.QtWidgets import QPushButton, QMenu, QWidget
from PySide6.QtCore import QTimer, Qt


class MyWidget(QWidget):
    def __init__(self):
        super().__init__()

        m = QMenu(self)
        b = QPushButton("Hello", self)
        b.setMenu(m)


class QPushButtonTest(UsesQApplication):
    def createMenu(self, button):
        m = QMenu()
        button.setMenu(m)

    def testSetMenu(self):
        w = MyWidget()
        w.show()

        timer = QTimer.singleShot(100, self.app.quit)
        self.app.exec()

    def buttonCb(self, checked):
        self._clicked = True

    def testBoolinSignal(self):
        b = QPushButton()
        b.setCheckable(True)
        b.setShortcut(Qt.Key_A)
        self._clicked = False
        b.toggled[bool].connect(self.buttonCb)
        b.toggle()
        self.assertTrue(self._clicked)


if __name__ == '__main__':
    unittest.main()

