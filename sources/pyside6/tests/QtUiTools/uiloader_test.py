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

from PySide6.QtWidgets import QWidget
from PySide6.QtUiTools import QUiLoader


class OverridingLoader(QUiLoader):
    def createWidget(self, class_name, parent=None, name=''):
        if class_name == 'QWidget':
            w = QWidget(parent)
            w.setObjectName(name)
            return w
        return QUiLoader.createWidget(self, class_name, parent, name)


class QUiLoaderTester(UsesQApplication):
    def setUp(self):
        UsesQApplication.setUp(self)
        self._filePath = os.path.join(os.path.dirname(__file__), 'test.ui')

    def testLoadFile(self):
        loader = QUiLoader()
        parent = QWidget()
        w = loader.load(self._filePath, parent)
        self.assertNotEqual(w, None)

        self.assertEqual(len(parent.children()), 1)

        child = w.findChild(QWidget, "child_object")
        self.assertNotEqual(child, None)
        self.assertEqual(w.findChild(QWidget, "grandson_object"), child.findChild(QWidget, "grandson_object"))

    def testLoadFileOverride(self):
        # PYSIDE-1070, override QUiLoader::createWidget() with parent=None crashes
        loader = OverridingLoader()
        w = loader.load(self._filePath)
        self.assertNotEqual(w, None)


if __name__ == '__main__':
    unittest.main()

