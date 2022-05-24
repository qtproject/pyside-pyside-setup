# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

import os
import sys
import unittest

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
from init_paths import init_test_paths
init_test_paths(False)

from PySide6.QtCore import QMetaObject, Slot
from PySide6.QtWidgets import QApplication, QPushButton, QWidget


class MyObject(QWidget):
    def __init__(self, parent=None):
        QWidget.__init__(self, parent)
        self._method_called = False

    @Slot()
    def on_button_clicked(self):
        self._method_called = True


class AutoConnectionTest(unittest.TestCase):

    def testConnection(self):
        app = QApplication([])

        win = MyObject()
        btn = QPushButton("click", win)
        btn.setObjectName("button")
        QMetaObject.connectSlotsByName(win)
        btn.click()
        self.assertTrue(win._method_called)


if __name__ == '__main__':
    unittest.main()
