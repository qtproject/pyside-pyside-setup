# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

import os
import sys
import unittest

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
from init_paths import init_test_paths
init_test_paths(False)

from PySide6.QtWidgets import QMainWindow
from PySide6.QtUiTools import QUiLoader
from helper.timedqapplication import TimedQApplication


class Gui_Qt(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)

        lLoader = QUiLoader()

        # this used to cause a segfault because the old inject code used to destroy the parent layout
        file = Path(__file__).resolve().parent / 'bug_958.ui'
        assert(file.is_file())
        self._cw = lLoader.load(file, self)

        self.setCentralWidget(self._cw)


class BugTest(TimedQApplication):
    def testCase(self):
        lMain = Gui_Qt()
        lMain.show()
        self.app.exec()


if __name__ == "__main__":
    unittest.main()
