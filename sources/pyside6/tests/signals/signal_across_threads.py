# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

'''Test case for PYSIDE-1354: Ensure that slots are invoked from the receiver's
thread context when using derived classes (and thus, a global receiver).'''

import os
import sys
import unittest

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
from init_paths import init_test_paths
init_test_paths(False)

from PySide6.QtCore import QObject, QThread, QTimer, Slot
from helper.usesqapplication import UsesQApplication


class ReceiverBase(QObject):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.senderThread = None

    @Slot()
    def slot_function(self):
        self.senderThread = QThread.currentThread()


class Receiver(ReceiverBase):
    pass


class TestThread(QThread):
    def __init__(self, parent=None):
        super().__init__(parent)

    def run(self):
        pass


class SignalAcrossThreads(UsesQApplication):
    def setUp(self):
        UsesQApplication.setUp(self)
        self._timer_tick = 0
        self._timer = QTimer()
        self._timer.setInterval(20)
        self._timer.timeout.connect(self._control_test)
        self._worker_thread = TestThread()

    def tearDown(self):
        UsesQApplication.tearDown(self)

    @Slot()
    def _control_test(self):
        if self._timer_tick == 0:
            self._worker_thread.start()
        elif self._timer_tick == 1:
            self._worker_thread.wait()
        else:
            self._timer.stop()
            self.app.quit()
        self._timer_tick += 1

    def test(self):
        worker_thread_receiver = Receiver()
        worker_thread_receiver.moveToThread(self._worker_thread)
        self._worker_thread.started.connect(worker_thread_receiver.slot_function)

        main_thread = QThread.currentThread()
        main_thread_receiver = Receiver()
        self._worker_thread.started.connect(main_thread_receiver.slot_function)

        self._timer.start()
        self.app.exec()

        self.assertEqual(worker_thread_receiver.senderThread, self._worker_thread)
        self.assertEqual(main_thread_receiver.senderThread, main_thread)


if __name__ == '__main__':
    unittest.main()
