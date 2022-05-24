# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

# Qt5: this is gone: from PySide6.QtGui import QMacStyle

import os
import sys
import unittest

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
from init_paths import init_test_paths
init_test_paths(False)

from PySide6.QtWidgets import QApplication, QLabel, QStyleFactory
from PySide6.QtCore import QObject

from helper.usesqapplication import UsesQApplication


class QMacStyleTest(UsesQApplication):
    def setUp(self):
        UsesQApplication.setUp(self)
        self.QMacStyle = type(QStyleFactory.create('Macintosh'))

    def testWidgetStyle(self):
        w = QLabel('Hello')
        self.assertTrue(isinstance(w.style(), self.QMacStyle))


if __name__ == '__main__':
    unittest.main()
