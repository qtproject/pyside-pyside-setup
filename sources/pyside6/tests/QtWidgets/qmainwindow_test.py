# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

import os
import sys
import unittest
import weakref

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
from init_paths import init_test_paths
init_test_paths(False)

from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QMainWindow, QPushButton, QToolButton, QWidget
from helper.usesqapplication import UsesQApplication


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.createToolbar()

    def createToolbar(self):
        pointerButton = QToolButton()
        pointerToolbar = self.addToolBar("Pointer type")
        pointerToolbar.addWidget(pointerButton)


class MyButton(QPushButton):
    def __init__(self, parent=None):
        super().__init__()
        self._called = False

    def myCallback(self):
        self._called = True


class TestMainWindow(UsesQApplication):

    def testCreateToolbar(self):
        w = MainWindow()
        w.show()
        QTimer.singleShot(1000, self.app.quit)
        self.app.exec()

    def objDel(self, obj):
        self.app.quit()

    @unittest.skipUnless(hasattr(sys, "getrefcount"), f"{sys.implementation.name} has no refcount")
    def testRefCountToNull(self):
        w = QMainWindow()
        c = QWidget()
        self.assertEqual(sys.getrefcount(c), 2)
        w.setCentralWidget(c)
        self.assertEqual(sys.getrefcount(c), 3)
        wr = weakref.ref(c, self.objDel)
        w.setCentralWidget(None)
        c = None
        self.app.exec()

    @unittest.skipUnless(hasattr(sys, "getrefcount"), f"{sys.implementation.name} has no refcount")
    def testRefCountToAnother(self):
        w = QMainWindow()
        c = QWidget()
        self.assertEqual(sys.getrefcount(c), 2)
        w.setCentralWidget(c)
        self.assertEqual(sys.getrefcount(c), 3)

        c2 = QWidget()
        w.setCentralWidget(c2)
        self.assertEqual(sys.getrefcount(c2), 3)

        wr = weakref.ref(c, self.objDel)
        w.setCentralWidget(None)
        c = None

        self.app.exec()

    def testSignalDisconect(self):
        w = QMainWindow()
        b = MyButton("button")
        b.clicked.connect(b.myCallback)
        w.setCentralWidget(b)

        b = MyButton("button")
        b.clicked.connect(b.myCallback)
        w.setCentralWidget(b)

        b.click()
        self.assertEqual(b._called, True)


if __name__ == '__main__':
    unittest.main()

