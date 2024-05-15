# Copyright (C) 2024 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

import os
import sys
import unittest

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
from init_paths import init_test_paths
init_test_paths(False)

from PySide6.QtCore import QTimer

from helper.usesqapplication import UsesQApplication


class TestBugPYSIDE2745(UsesQApplication):

    def setUp(self):
        UsesQApplication.setUp(self)
        self.counter = 0

    def fail(self):
        self.counter += 1
        raise Exception()

    def test_fail(self):
        QTimer.singleShot(0, self.fail)
        QTimer.singleShot(0, self.fail)
        QTimer.singleShot(1, self.app.quit)
        self.app.exec()
        self.assertEqual(self.counter, 2)


if __name__ == '__main__':
    unittest.main()
