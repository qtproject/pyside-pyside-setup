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

import PySide6.QtCore as QtCore


class Signaller(QtCore.QObject):
    s1 = QtCore.Signal()
    s2 = QtCore.Signal()


class TestBug920(unittest.TestCase):

    def testIt(self):
        s = Signaller()
        s.s1.connect(self.onSignal)
        s.s2.connect(self.onSignal)
        self.assertTrue(s.s1.disconnect(self.onSignal))
        self.assertTrue(s.s2.disconnect(self.onSignal))

    def onSignal(self):
        pass


if __name__ == "__main__":
    unittest.main()
