# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

import os
import sys
import unittest

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
from init_paths import init_test_paths
init_test_paths(False)

from PySide6.QtGui import QAction
from PySide6.QtWidgets import QToolBar, QApplication, QToolButton


class TestLabelPixmap(unittest.TestCase):
    def testReference(self):
        toolbar = QToolBar()

        for i in range(20):
            toolbar.addAction(QAction(f"Action {i}"))

        buttons = toolbar.findChildren(QToolButton, "")
        toolbar.clear()

        for b in buttons:
            self.assertRaises(RuntimeError, b.objectName)


if __name__ == '__main__':
    app = QApplication([])
    unittest.main()

