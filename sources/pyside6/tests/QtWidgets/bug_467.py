# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

''' Test bug 367: http://bugs.openbossa.org/show_bug.cgi?id=467'''

import os
import sys
import unittest

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
from init_paths import init_test_paths
init_test_paths(False)

from helper.usesqapplication import UsesQApplication
from PySide6.QtWidgets import QMainWindow, QApplication


class MyWidget(QMainWindow):
    def __init__(self, parent=None):
        QMainWindow.__init__(self, parent)


class BugTest(UsesQApplication):
    def testCase(self):
        w = MyWidget()
        widgets = QApplication.allWidgets()
        self.assertTrue(w in widgets)


if __name__ == '__main__':
    unittest.main()
