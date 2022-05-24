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
from PySide6.QtWidgets import QFrame, QWidget
from PySide6.QtUiTools import QUiLoader


class MyQUiLoader(QUiLoader):
    def __init__(self, baseinstance):
        super().__init__()
        self.baseinstance = baseinstance
        self._widgets = []

    def createWidget(self, className, parent=None, name=""):
        widget = QUiLoader.createWidget(self, className, parent, name)
        self._widgets.append(widget)
        if parent is None:
            return self.baseinstance
        else:
            setattr(self.baseinstance, name, widget)
            return widget


class ButTest(UsesQApplication):
    def testCase(self):
        w = QWidget()
        loader = MyQUiLoader(w)

        filePath = os.path.join(os.path.dirname(__file__), 'minimal.ui')
        ui = loader.load(filePath)

        self.assertEqual(len(loader._widgets), 1)
        self.assertEqual(type(loader._widgets[0]), QFrame)


if __name__ == '__main__':
    unittest.main()

