# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

import os
import sys
import unittest

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
from init_paths import init_test_paths
init_test_paths(False)

from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QWidget, QApplication


class TestW1(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        TestW2(parent, self)


class TestW2(QWidget):
    def __init__(self, ancestor, parent=None):
        super().__init__(parent)
        self.ancestor_ref = ancestor


class Test(QWidget):
    def __init__(self):
        super().__init__()
        TestW1(self)


class TestQApplicationDestrcutor(unittest.TestCase):
    def testDestructor(self):
        w = Test()
        w.show()
        QTimer.singleShot(0, w.close)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    unittest.main()
    sys.exit(app.exec())
