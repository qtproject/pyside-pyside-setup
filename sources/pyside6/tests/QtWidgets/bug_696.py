#!/usr/bin/env python
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
from PySide6.QtWidgets import QMainWindow, QMenu, QApplication


class MainWindow(QMainWindow):
    def __init__(self, *args):
        self._menu = QMenu(self.dontexist)  # attribute called with invalid C++ object


class MainWindow2(QMainWindow):
    def __init__(self):
        self.show()


class Bug696(UsesQApplication):
    def testContructorInitialization(self):
        self.assertRaises(AttributeError, MainWindow)

    def testContructorInitializationAndCPPFunction(self):
        self.assertRaises(RuntimeError, MainWindow2)


if __name__ == '__main__':
    unittest.main()

