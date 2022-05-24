# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

import os
import sys
import unittest

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
from init_paths import init_test_paths
init_test_paths(False)

from PySide6.QtCore import QCoreApplication, QEventLoop, QObject, Qt, QThread, QTimer, SIGNAL


class Emitter(QThread):
    def __init__(self):
        super().__init__()

    def run(self):
        print("Before emit.")
        self.emit(SIGNAL("signal(int)"), 0)
        print("After emit.")


class Receiver(QObject):
    def __init__(self, eventloop):
        super().__init__()
        self.eventloop = eventloop

    def receive(self, number):
        print(f"Received number: {number}")
        self.eventloop.exit(0)


class TestBugPYSIDE164(unittest.TestCase):

    def testBlockingSignal(self):
        app = QCoreApplication.instance() or QCoreApplication([])
        eventloop = QEventLoop()
        emitter = Emitter()
        receiver = Receiver(eventloop)
        emitter.connect(emitter, SIGNAL("signal(int)"),
                        receiver.receive, Qt.BlockingQueuedConnection)
        emitter.start()
        retval = eventloop.exec()
        emitter.wait(2000)
        self.assertEqual(retval, 0)


if __name__ == '__main__':
    unittest.main()
