# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

import gc
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
from PySide6.QtGui import QTouchDevice
from PySide6.QtTest import QTest


class MyWidget(QWidget):
    def __init__(self, parent=None):
        QWidget.__init__(self, parent)
        self._sequence = []
        # Fixme (Qt 5): The device needs to be registered (using
        # QWindowSystemInterface::registerTouchDevice()) for the test to work
        self._device = QTouchDevice()
        self.setAttribute(Qt.WA_AcceptTouchEvents)
        QTimer.singleShot(200, self.generateEvent)

    def event(self, e):
        self._sequence.append(e.type())
        return QWidget.event(self, e)

    def generateEvent(self):
        o = QTest.touchEvent(self, self._device)
        o.press(0, QPoint(10, 10))
        o.commit()
        del o
        # PYSIDE-535: Need to collect garbage in PyPy to trigger deletion
        gc.collect()

        QTest.touchEvent(self, self._device).press(0, QPoint(10, 10))
        QTest.touchEvent(self, self._device).stationary(0).press(1, QPoint(40, 10))
        QTest.touchEvent(self, self._device).move(0, QPoint(12, 12)).move(1, QPoint(45, 5))
        QTest.touchEvent(self, self._device).release(0, QPoint(12, 12)).release(1, QPoint(45, 5))
        QTimer.singleShot(200, self.deleteLater)


class TouchEventTest(UsesQApplication):
    def testCreateEvent(self):
        w = MyWidget()
        w.show()
        self.app.exec()
        # same values as C++
        self.assertEqual(w._sequence.count(QEvent.Type.TouchBegin), 2)
        self.assertEqual(w._sequence.count(QEvent.Type.TouchUpdate), 2)
        self.assertEqual(w._sequence.count(QEvent.Type.TouchEnd), 1)


if __name__ == '__main__':
    unittest.main()
