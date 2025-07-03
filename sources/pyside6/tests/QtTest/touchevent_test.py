# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0
from __future__ import annotations

import os
import sys
import unittest

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
from init_paths import init_test_paths
init_test_paths(False)

from helper.usesqapplication import UsesQApplication

from PySide6.QtWidgets import QWidget
from PySide6.QtCore import QPoint, QTimer, Qt, QEvent
from PySide6.QtGui import QPointingDevice
from PySide6.QtTest import QTest


class MyWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._sequence = []
        self._device = QPointingDevice.primaryPointingDevice()
        self.setAttribute(Qt.WA_AcceptTouchEvents)
        QTimer.singleShot(200, self.generateEvent)

    def event(self, e):
        et = e.type()
        if (et == QEvent.Type.TouchBegin or et == QEvent.Type.TouchUpdate
                or et == QEvent.Type.TouchEnd):
            e.accept()
            self._sequence.append(et)
            return True
        return super().event(e)

    def generateEvent(self):
        QTest.touchEvent(self, self._device).press(0, QPoint(10, 10))
        QTest.touchEvent(self, self._device).stationary(0).press(1, QPoint(40, 10))
        QTest.touchEvent(self, self._device).move(0, QPoint(12, 12)).move(1, QPoint(45, 5))
        QTest.touchEvent(self, self._device).release(0, QPoint(12, 12)).release(1, QPoint(45, 5))
        QTimer.singleShot(200, self.deleteLater)


class TouchEventTest(UsesQApplication):
    @unittest.skipIf(QPointingDevice.primaryPointingDevice() is None, "No device")
    def testCreateEvent(self):
        w = MyWidget()
        w.show()
        self.app.exec()
        self.assertEqual(w._sequence.count(QEvent.Type.TouchBegin), 1)
        self.assertEqual(w._sequence.count(QEvent.Type.TouchUpdate), 2)
        self.assertEqual(w._sequence.count(QEvent.Type.TouchEnd), 1)


if __name__ == '__main__':
    unittest.main()
