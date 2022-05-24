# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

import colorsys
import os
import sys
import unittest

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
from init_paths import init_test_paths
init_test_paths(False)

from PySide6.QtCore import SIGNAL
from PySide6.QtWidgets import QPushButton, QApplication


class Test (QApplication):
    def __init__(self, argv):
        super().__init__(argv)
        self._called = False

    def called(self):
        self._called = True


class QApplicationSignalsTest(unittest.TestCase):
    def testQuit(self):
        app = Test([])
        button = QPushButton("BUTTON")
        app.connect(button, SIGNAL("clicked()"), app.called)
        button.click()
        self.assertTrue(app._called)


if __name__ == '__main__':
    unittest.main()
