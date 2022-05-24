# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

''' Test bug 243: http://bugs.openbossa.org/show_bug.cgi?id=243'''

import os
import sys
import unittest

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
from init_paths import init_test_paths
init_test_paths(False)

from PySide6.QtWidgets import QApplication, QMainWindow, QLayout


class QAppPresence(unittest.TestCase):

    def testBug(self):
        app = QApplication(sys.argv)
        window = QMainWindow()
        l = window.layout()
        self.assertTrue(isinstance(l, QLayout))


if __name__ == '__main__':
    unittest.main()
