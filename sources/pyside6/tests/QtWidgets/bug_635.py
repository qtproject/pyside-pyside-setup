# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

''' Test bug 635: http://bugs.openbossa.org/show_bug.cgi?id=635'''

import os
import sys
import unittest

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
from init_paths import init_test_paths
init_test_paths(False)

from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication, QToolBar


class testQToolBar(unittest.TestCase):
    def callback(self):
        self._called = True

    def testAddAction(self):
        bar = QToolBar()
        self._called = False
        a = bar.addAction("act1", self.callback)
        a.trigger()
        self.assertTrue(self._called)

    def testAddActionWithIcon(self):
        bar = QToolBar()
        self._called = False
        icon = QIcon()
        a = bar.addAction(icon, "act1", self.callback)
        a.trigger()
        self.assertTrue(self._called)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    unittest.main()
