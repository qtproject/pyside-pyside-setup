# Copyright (C) 2026 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

import os
import sys
import unittest

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
from init_paths import init_test_paths
init_test_paths(False)

from helper.usesqapplication import UsesQApplication
from PySide6.QtCore import QCoreApplication, QObject, QPoint, QThread, Slot
from PySide6.QtGui import QWindow


class DestroyReceiver(QObject):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.destroy_thread = None

    @Slot(QObject)
    def slotDestroyed(self, o):
        self.destroy_thread = QThread.currentThread()


class Window(QWindow, QPoint):
    def __init__(self):
        QWindow.__init__(self)
        QPoint.__init__(self)


class Thread(QThread):
    def __init__(self, obj: QObject):
        super().__init__()
        self._objects = [obj]
        self.setObjectName("thread")

    def run(self):
        self._objects.clear()


class TestQGuiApplication(UsesQApplication):
    """PYSIDE-3473: Test whether a class using the "delete-in_main-thread" attribute (like
       QWindow and Python-derived classes (multiple inheritance) are deleted in the main thread."""
    def test(self):
        destroy_receiver = DestroyReceiver()
        test = Window()
        test.destroyed.connect(destroy_receiver.slotDestroyed)
        thread = Thread(test)
        test = None
        thread.start()
        thread.wait()
        while destroy_receiver.destroy_thread is None:
            QCoreApplication.processEvents()
        self.assertEqual(destroy_receiver.destroy_thread, qApp.thread())  # noqa: F821


if __name__ == '__main__':
    unittest.main()
