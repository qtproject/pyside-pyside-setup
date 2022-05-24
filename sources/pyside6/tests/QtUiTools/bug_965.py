# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

import os
import sys
import unittest

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
from init_paths import init_test_paths
init_test_paths(False)

from PySide6.QtUiTools import QUiLoader

from helper.usesqapplication import UsesQApplication


class MyQUiLoader(QUiLoader):
    def __init__(self):
        super().__init__()

    def createWidget(self, className, parent=None, name=""):
        return None


class BugTest(UsesQApplication):
    def testCase(self):
        loader = MyQUiLoader()
        file = Path(__file__).resolve().parent / 'bug_965.ui'
        self.assertTrue(file.is_file())
        self.assertRaises(RuntimeError, loader.load, file)


if __name__ == '__main__':
    unittest.main()
