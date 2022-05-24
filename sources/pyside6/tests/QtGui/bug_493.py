# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

import os
import sys
import unittest

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
from init_paths import init_test_paths
init_test_paths(False)

from PySide6.QtCore import Qt, QEvent
from PySide6.QtGui import QGuiApplication, QKeyEvent, QKeySequence


class TestBug493(unittest.TestCase):

    def testIt(self):
        # We need a qapp otherwise Qt will crash when trying to detect the
        # current platform
        app = QGuiApplication([])
        ev1 = QKeyEvent(QEvent.KeyRelease, Qt.Key_Delete, Qt.NoModifier)
        ev2 = QKeyEvent(QEvent.KeyRelease, Qt.Key_Copy, Qt.NoModifier)
        ks = QKeySequence.Delete

        self.assertTrue(ev1.matches(ks))
        self.assertFalse(ev2.matches(ks))


if __name__ == '__main__':
    unittest.main()
