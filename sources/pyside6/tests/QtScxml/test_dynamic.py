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
from PySide6.QtCore import QCoreApplication, QObject, Slot, SIGNAL, SLOT
from PySide6.QtScxml import QScxmlStateMachine, QScxmlEvent


class Receiver(QObject):
    def __init__(self):
        super().__init__()
        self.eventReceived = False
        self.reachedStable = False

    @Slot(QScxmlEvent)
    def handleEvent(self, event):
        self.eventReceived = True

    @Slot()
    def slotReachedStable(self):
        self.reachedStable = True


class testDynamicStateMachine(TimedQApplication):
    def setUp(self):
        super().setUp()
        filePath = Path(__file__).parent / "trafficlight.scxml"
        self.assertTrue(filePath.is_file())
        self._machine = QScxmlStateMachine.fromFile(os.fspath(filePath))
        self._receiver = Receiver()
        self._machine.connectToEvent("*", self._receiver,
                                     SLOT("handleEvent(QScxmlEvent)"))
        self._machine.reachedStableState.connect(self._receiver.slotReachedStable)
        self.assertTrue(not self._machine.parseErrors())
        self.assertTrue(self._machine)

    def test(self):
        self._machine.start()
        while not self._receiver.reachedStable and not self._receiver.eventReceived:
            QCoreApplication.processEvents()


if __name__ == '__main__':
    unittest.main()
