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

from PySide6.QtGui import QAction
from PySide6.QtWidgets import QComboBox, QWidget
from PySide6.QtUiTools import QUiLoader


class MyWidget(QComboBox):
    def __init__(self, parent=None):
        QComboBox.__init__(self, parent)

    def isPython(self):
        return True


class BugTest(UsesQApplication):
    def testCase(self):
        w = QWidget()
        loader = QUiLoader()

        filePath = os.path.join(os.path.dirname(__file__), 'action.ui')
        result = loader.load(filePath, w)
        self.assertTrue(isinstance(result.actionFoo, QAction))

    def testPythonCustomWidgets(self):
        w = QWidget()
        loader = QUiLoader()
        loader.registerCustomWidget(MyWidget)
        self.assertTrue('MyWidget' in loader.availableWidgets())

        filePath = os.path.join(os.path.dirname(__file__), 'pycustomwidget.ui')
        result = loader.load(filePath, w)
        self.assertTrue(isinstance(result.custom, MyWidget))
        self.assertTrue(result.custom.isPython())

    def testPythonCustomWidgetsTwice(self):
        w = QWidget()
        loader = QUiLoader()
        loader.registerCustomWidget(MyWidget)
        self.assertTrue('MyWidget' in loader.availableWidgets())

        filePath = os.path.join(os.path.dirname(__file__), 'pycustomwidget2.ui')
        result = loader.load(filePath, w)
        self.assertTrue(isinstance(result.custom, MyWidget))
        self.assertTrue(isinstance(result.custom2, MyWidget))
        self.assertTrue(result.custom.isPython())


if __name__ == '__main__':
    unittest.main()

