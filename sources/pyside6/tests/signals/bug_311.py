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

from PySide6.QtCore import QDate, QObject, Signal
from helper.usesqapplication import UsesQApplication


class DerivedDate(QDate):
    def __init__(self, y, m, d):
        super().__init__(y, m, d)


class Emitter(QObject):
    dateSignal1 = Signal(QDate)
    dateSignal2 = Signal(DerivedDate)
    tupleSignal = Signal(tuple)


class SignaltoSignalTest(UsesQApplication):
    def myCb(self, dt):
        self._dt = dt

    def testBug(self):
        e = Emitter()
        d = DerivedDate(2010, 8, 24)
        self._dt = None
        e.dateSignal1.connect(self.myCb)
        e.dateSignal1.emit(d)
        self.assertEqual(self._dt, d)

        self._dt = None
        e.dateSignal2.connect(self.myCb)
        e.dateSignal2.emit(d)
        self.assertEqual(self._dt, d)

        myTuple = (5, 6, 7)
        self._dt = None
        e.tupleSignal.connect(self.myCb)
        e.tupleSignal.emit(myTuple)
        self.assertEqual(myTuple, self._dt)


if __name__ == '__main__':
    unittest.main()

