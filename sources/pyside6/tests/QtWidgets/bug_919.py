# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

import os
import sys
import unittest

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
from init_paths import init_test_paths
init_test_paths(False)

from helper.timedqapplication import TimedQApplication
from PySide6.QtCore import Signal, QTimer
from PySide6.QtGui import QPainter
from PySide6.QtWidgets import QPushButton, QStyleOptionButton, QApplication, QStyle


class MyWidget(QPushButton):
    def __init__(self, parent=None):
        QPushButton.__init__(self, parent)
        self._painted = False

    def _emitPainted(self):
        self.paintReceived.emit()

    def paintEvent(self, e):
        p = QPainter(self)
        style = QApplication.style()
        option = QStyleOptionButton()
        style.drawControl(QStyle.CE_PushButton, option, p)
        self._painted = True
        QTimer.singleShot(0, self._emitPainted)

    paintReceived = Signal()


class TestBug919(TimedQApplication):
    def setUp(self):
        TimedQApplication.setUp(self, 2000)

    def testFontInfo(self):
        w = MyWidget()
        w.paintReceived.connect(self.app.quit)
        w.show()
        self.app.exec()
        self.assertTrue(w._painted)


if __name__ == '__main__':
    unittest.main()
