# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

''' Test the QShortcut constructor'''

import os
import sys
import unittest

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
from init_paths import init_test_paths
init_test_paths(False)

from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QGuiApplication, QKeySequence, QShortcut, QWindow


class Foo(QWindow):
    def __init__(self):
        super().__init__()
        self.ok = False
        self.copy = False

    def slot_of_foo(self):
        self.ok = True

    def slot_of_copy(self):
        self.copy = True


class MyShortcut(QShortcut):
    def __init__(self, keys, wdg, slot):
        QShortcut.__init__(self, keys, wdg, slot)

    def emit_signal(self):
        self.activated.emit()


class QAppPresence(unittest.TestCase):

    def testQShortcut(self):
        self.qapp = QGuiApplication([])
        f = Foo()

        self.sc = MyShortcut(QKeySequence(Qt.Key_Return), f, f.slot_of_foo)
        self.scstd = MyShortcut(QKeySequence.Copy, f, f.slot_of_copy)
        QTimer.singleShot(0, self.init)
        self.qapp.exec()
        self.assertEqual(f.ok, True)
        self.assertEqual(f.copy, True)

    def init(self):
        self.sc.emit_signal()
        self.scstd.emit_signal()
        self.qapp.quit()


if __name__ == '__main__':
    unittest.main()
