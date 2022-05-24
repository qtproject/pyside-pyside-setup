# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

'''Test cases for connecting signals between threads'''

import os
import sys
import unittest

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
from init_paths import init_test_paths
init_test_paths(False)

from PySide6.QtCore import QThread, QTimer, QObject, Signal, Slot, QCoreApplication


class Source(QObject):
    source = Signal()

    def __init__(self, *args):
        super().__init__(*args)

    @Slot()
    def emit_sig(self):
        self.source.emit()


class Target(QObject):
    def __init__(self, *args):
        super().__init__(*args)
        self.called = False

    @Slot()
    def myslot(self):
        self.called = True


class ThreadJustConnects(QThread):
    def __init__(self, source, *args):
        super().__init__(*args)
        self.source = source
        self.target = Target()

    def run(self):
        self.source.source.connect(self.target.myslot)
        self.source.source.connect(self.quit)
        self.exec()


class BasicConnection(unittest.TestCase):

    def testEmitOutsideThread(self):
        global thread_run

        app = QCoreApplication([])
        source = Source()
        thread = ThreadJustConnects(source)

        thread.finished.connect(QCoreApplication.quit)
        thread.start()

        QTimer.singleShot(50, source.emit_sig)
        app.exec()
        thread.wait()

        self.assertTrue(thread.target.called)


if __name__ == '__main__':
    unittest.main()
