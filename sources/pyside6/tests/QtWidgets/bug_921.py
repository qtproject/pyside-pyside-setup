#!/usr/bin/env python
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

from PySide6.QtCore import QObject, Signal, Qt
from PySide6.QtWidgets import QMainWindow
from helper.timedqapplication import TimedQApplication


class Signaller(QObject):
    s1 = Signal()
    s2 = Signal()
    s3 = Signal()


class Window(object):

    def __init__(self, s):
        self._window = QMainWindow()
        self._window.setAttribute(Qt.WA_DeleteOnClose, True)
        self._window.setWindowTitle("Demo!")

        self._s = s
        self._s.s1.connect(self._on_signal)
        self._s.s2.connect(self._on_signal)

    def show(self):
        self._window.show()

    def _on_signal(self):
        self._window.setWindowTitle("Signaled!")


class TestTimedApp(TimedQApplication):
    def testSignals(self):
        s = Signaller()
        w = Window(s)
        w.show()

        def midleFunction():
            def internalFunction():
                pass
            s.s3.connect(internalFunction)

        midleFunction()
        self.app.exec()
        del w
        # PYSIDE-535: Need to collect garbage in PyPy to trigger deletion
        gc.collect()

        s.s1.emit()
        s.s2.emit()
        s.s3.emit()


if __name__ == '__main__':
    unittest.main()
