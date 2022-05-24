#!/usr/bin/env python
# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0

import os
import sys
import unittest

from pathlib import Path
sys.path.append(os.fspath(Path(__file__).resolve().parents[1]))
from init_paths import init_test_paths
init_test_paths(False)

from PySide6.QtCore import QObject, Signal


class Emitter(QObject):
    s1 = Signal()
    s2 = Signal()
    s3 = Signal()
    s4 = Signal()
    s5 = Signal()
    s6 = Signal()
    s7 = Signal()
    s8 = Signal()
    s9 = Signal()
    s10 = Signal()
    s11 = Signal()
    s12 = Signal()
    s13 = Signal()
    s14 = Signal()


class SignalNumberLimitTest(unittest.TestCase):
    def myCb(self):
        self._count += 1

    def testBug(self):
        e = Emitter()
        e.s1.connect(self.myCb)
        e.s2.connect(self.myCb)
        e.s3.connect(self.myCb)
        e.s4.connect(self.myCb)
        e.s5.connect(self.myCb)
        e.s6.connect(self.myCb)
        e.s7.connect(self.myCb)
        e.s8.connect(self.myCb)
        e.s9.connect(self.myCb)
        e.s10.connect(self.myCb)
        e.s11.connect(self.myCb)
        e.s12.connect(self.myCb)
        e.s13.connect(self.myCb)
        e.s14.connect(self.myCb)

        self._count = 0
        e.s1.emit()
        e.s2.emit()
        e.s3.emit()
        e.s4.emit()
        e.s5.emit()
        e.s6.emit()
        e.s7.emit()
        e.s8.emit()
        e.s9.emit()
        e.s10.emit()
        e.s11.emit()
        e.s12.emit()
        e.s13.emit()
        e.s14.emit()
        self.assertEqual(self._count, 14)


if __name__ == '__main__':
    unittest.main()
