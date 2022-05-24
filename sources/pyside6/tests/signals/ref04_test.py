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

from PySide6.QtCore import QObject, Signal


class ExtQObject(QObject):

    mySignal = Signal()

    def __init__(self):
        super().__init__()


class UserSignalTest(unittest.TestCase):

    def setUp(self):
        self.emitter = ExtQObject()
        self.counter = 0

    def tearDown(self):
        del self.emitter
        del self.counter
        # PYSIDE-535: Need to collect garbage in PyPy to trigger deletion
        gc.collect()

    def testConnectEmitDisconnect(self):

        def slot():
            self.counter += 1

        self.emitter.mySignal.connect(slot)

        self.assertEqual(self.counter, 0)
        self.emitter.mySignal.emit()
        self.assertEqual(self.counter, 1)
        self.emitter.mySignal.emit()
        self.assertEqual(self.counter, 2)

        self.emitter.mySignal.disconnect(slot)

        self.emitter.mySignal.emit()
        self.assertEqual(self.counter, 2)

#    def testConnectWithConfigureMethod(self):
#
#        def slot():
#            self.counter += 1
#
#        self.emitter.pyqtConfigure(mySignal=slot)
#        self.assertEqual(self.counter, 0)
#        self.emitter.mySignal.emit()
#        self.assertEqual(self.counter, 1)


if __name__ == '__main__':
    unittest.main()

