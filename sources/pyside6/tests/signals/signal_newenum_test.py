# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

import os
import sys
import unittest

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
from init_paths import init_test_paths
init_test_paths(False)

from PySide6.QtCore import QCoreApplication, QTimer, QEvent, Qt, Signal
from PySide6.QtWidgets import QApplication, QWidget
from PySide6.QtGui import QKeyEvent


class Window(QWidget):
    test_sig1 = Signal(Qt.AlignmentFlag)
    test_sig2 = Signal(Qt.AlignmentFlag, str)

    def __init__(self):
        super().__init__()

    def keyPressEvent(self, e):
        self.test_sig1.emit(Qt.AlignLeft)
        self.test_sig2.emit(Qt.AlignLeft, "bla")

    def handler1(self, e):
        print('\nhandler1', e, "type=", type(e).__name__)
        self.result += 1

    def handler2(self, e, s):
        print('handler2', e, "type=", type(e).__name__, s)
        self.result += 2


class TestSignalNewEnum(unittest.TestCase):

    def testIt(self):
        app = QApplication()
        self.window = window = Window()
        window.result = 0
        window.show()

        window.test_sig1.connect(window.handler1)
        window.test_sig2.connect(window.handler2)

        QTimer.singleShot(0, self.sendKbdEvent)
        QTimer.singleShot(100, app.quit)
        app.exec()

        self.assertEqual(window.result, 3)

    def sendKbdEvent(self):
        ev = QKeyEvent(QEvent.KeyPress, Qt.Key_A, Qt.NoModifier, 'a')
        QCoreApplication.sendEvent(self.window, ev)


if __name__ == '__main__':
    unittest.main()
