# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

import os
import sys
import unittest

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
from init_paths import init_test_paths
init_test_paths(False)

from PySide6.QtCore import QCoreApplication, QTimer, Slot


class MyTimer (QTimer):
    def __init__(self):
        super().__init__()
        self.startCalled = False

    @Slot()
    def slotUsedToIncreaseMethodOffset(self):
        pass


class MyTimer2 (MyTimer):

    @Slot()
    def slotUsedToIncreaseMethodOffset2(self):
        pass

    def start(self):
        self.startCalled = True
        QCoreApplication.instance().quit()


class TestBug1019 (unittest.TestCase):
    def testIt(self):
        app = QCoreApplication([])
        t = MyTimer2()
        QTimer.singleShot(0, t.start)
        app.exec()
        self.assertTrue(t.startCalled)


if __name__ == "__main__":
    unittest.main()
