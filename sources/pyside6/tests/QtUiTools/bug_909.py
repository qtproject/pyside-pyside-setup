# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

import os
import sys
import unittest

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
from init_paths import init_test_paths
init_test_paths(False)

from PySide6.QtCore import QFile
from PySide6.QtWidgets import QTabWidget
from PySide6.QtUiTools import QUiLoader

from helper.usesqapplication import UsesQApplication


class TestDestruction(UsesQApplication):
    @unittest.skipUnless(hasattr(sys, "getrefcount"), f"{sys.implementation.name} has no refcount")
    def testBug909(self):
        file = Path(__file__).resolve().parent / 'bug_909.ui'
        self.assertTrue(file.is_file())
        fileName = QFile(file)
        loader = QUiLoader()
        main_win = loader.load(fileName)
        self.assertEqual(sys.getrefcount(main_win), 2)
        fileName.close()

        tw = QTabWidget(main_win)
        main_win.setCentralWidget(tw)
        main_win.show()


if __name__ == '__main__':
    unittest.main()
