# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

import os
import sys
import unittest

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
from init_paths import init_test_paths
init_test_paths(False)

from PySide6.QtCore import QCoreApplication, QTimer, QEvent, Qt
from PySide6.QtWidgets import QApplication, QSpinBox
from PySide6.QtGui import QKeyEvent


class MySpinBox(QSpinBox):

    def validate(self, text, pos):
        return QSpinBox.validate(self, text, pos)


class TestBug879 (unittest.TestCase):

    def testIt(self):
        app = QApplication([])
        self.box = MySpinBox()
        self.box.show()

        QTimer.singleShot(0, self.sendKbdEvent)
        QTimer.singleShot(100, app.quit)
        app.exec()

        self.assertEqual(self.box.text(), '0')

    def sendKbdEvent(self):
        ev = QKeyEvent(QEvent.KeyPress, Qt.Key_A, Qt.NoModifier, 'a')
        QCoreApplication.sendEvent(self.box, ev)


if __name__ == '__main__':
    unittest.main()
