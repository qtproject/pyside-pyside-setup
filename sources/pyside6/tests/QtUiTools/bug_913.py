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

from PySide6.QtWidgets import QApplication
from PySide6.QtUiTools import QUiLoader


class TestBug913 (unittest.TestCase):

    def testIt(self):
        app = QApplication([])

        loader = QUiLoader()
        file = Path(__file__).resolve().parent / 'bug_913.ui'
        self.assertTrue(file.is_file())
        widget = loader.load(file)
        widget.tabWidget.currentIndex()  # direct child is available as member
        widget.le_first.setText('foo')  # child of QTabWidget must also be available!


if __name__ == '__main__':
    unittest.main()
